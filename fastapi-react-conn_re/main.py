from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncio
import json

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정 (React 프론트엔드와 연결)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 서버 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 대화 데이터 저장용 리스트
dialog = []

# 대화 요청 모델 정의
class ChatMessage(BaseModel):
    message: str  # 대화 내용

# 루트 경로 정의 (404 방지)
@app.get("/")
async def root():
    return {"message": "FastAPI 서버가 정상적으로 작동 중입니다."}

# WebSocket을 통한 대화 데이터 스트리밍
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

# WebSocket 연결 관리
import json  # JSON 사용 추가

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await manager.connect(websocket)  # 클라이언트 연결
    try:
        sent_length = 0  # 이미 보낸 메시지 개수 추적

        while True:
            # 새로운 메시지가 추가되었는지 확인
            if len(dialog) > sent_length:
                role, message = dialog[sent_length]
                now = datetime.now().strftime("%H:%M:%S")
                if role == "고객":
                    position = "left" # 고객 말풍선 왼쪽
                    label = f"[고객:1234] {now}"
                elif role == "상담사":
                    position = "right" # 상담사 말풍선 오른쪽
                    label = f"[상담사:김상담] {now}"
                else:
                    position = "center"
                    label = "[알 수 없음]"

                # 메시지를 JSON 형식으로 전송
                await websocket.send_text(
                    json.dumps({"label": label, "position": position, "message": message.strip()})
                )
                sent_length += 1

                # 상담 종료 메시지가 있는 경우
                if message.strip().lower() == "상담 종료":
                    # 종료 메시지 전송
                    await websocket.send_text(
                        json.dumps({"label": "종료", "position": "center", "message": "상담이 종료되었습니다."})
                    )
                    # 루프 종료
                    break

            # 새로운 메시지가 없으면 대기
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("클라이언트와의 연결이 끊어졌습니다.")
    finally:
        # 종료 후 연결 해제
        manager.disconnect(websocket)




# uvicorn main:app --reload
# npm start