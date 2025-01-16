from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from datetime import datetime
import asyncio
import json
import os
from langchain_upstage import UpstageEmbeddings
from langchain_pinecone import PineconeVectorStore
from fastapi.middleware.cors import CORSMiddleware

# 환경 변수 로드
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Embedding 및 Pinecone 초기화
embedding = UpstageEmbeddings(model="solar-embedding-1-large", api_key=UPSTAGE_API_KEY)
index_name = 'upstage-index'
database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],  # Vite 기본 포트 추가
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 대화 데이터 저장
dialog = []

class ChatMessage(BaseModel):
    message: str

class ChatMessageRequest(BaseModel):
    user_message: str

# 챗봇 응답 처리
@app.post("/chatbot")
async def chatbot_response(message: dict):
    try:
        user_message = message.get("user_message", "")
        # Pinecone에서 유사한 문서 검색
        retrieved_docs = database.similarity_search(user_message, k=4)
        # 가장 유사한 문서에서 답변 추출
        best_doc = retrieved_docs[0]
        best_answer_part = best_doc.page_content.split("Answer:")[-1].split("keywords:")[0].strip()
        
        return {"bot_response": best_answer_part}
    except Exception as e:
        return {"error": str(e)}

# WebSocket 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

 # 고객 메시지 추가 엔드포인트
@app.post("/chat/customer")
async def input_customer_dialog(voice: ChatMessage):
    global dialog
    print(f"Received customer input: {voice.message}")
    dialog.append(("고객", voice.message))
    return {"message": "고객 메시지가 성공적으로 추가되었습니다."}

# 상담사 메시지 추가 엔드포인트
@app.post("/chat/agent")
async def input_agent_dialog(voice: ChatMessage):
    global dialog
    print(f"Received agent input: {voice.message}")
    dialog.append(("상담사", voice.message))
    return {"message": "상담사 메시지가 성공적으로 추가되었습니다."}


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        sent_length = 0
        while True:
            if len(dialog) > sent_length:
                role, message = dialog[sent_length]
                now = datetime.now().strftime("%H:%M:%S")
                
                if role == "고객":
                    position = "left"
                    label = f"[고객:1234] {now}"
                else:
                    position = "right"
                    label = f"[상담사:김상담] {now}"

                await websocket.send_text(
                    json.dumps({
                        "label": label,
                        "position": position,
                        "message": message.strip()
                    })
                )
                sent_length += 1

            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "서버가 정상적으로 실행 중입니다."}
