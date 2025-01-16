from fastapi import FastAPI
from pydantic import BaseModel
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

# FastAPI 앱 생성
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the chatbot API"}

# CORS 미들웨어 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 특정 origin을 설정할 수 있습니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 헤더를 허용
)

# 사용자로부터 받은 메시지를 처리하기 위한 요청 모델
class ChatMessageRequest(BaseModel):
    user_message: str

class ChatMessageResponse(BaseModel):
    bot_response: str

# 메시지를 처리하는 엔드포인트
@app.post("/chat", response_model=ChatMessageResponse)
async def chat(request: ChatMessageRequest):
    user_message = request.user_message
    
    # Pinecone에서 유사한 문서 검색
    retrieved_docs = database.similarity_search(user_message, k=4)  # 유사한 4개의 결과를 검색

    # 가장 유사한 문서에서 답변 추출
    best_doc = retrieved_docs[0]
    best_answer_part = best_doc.page_content.split("Answer:")[-1].split("keywords:")[0].strip()

    # 반환할 응답 구성
    return ChatMessageResponse(bot_response=best_answer_part)
