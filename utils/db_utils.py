from pymongo import MongoClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")  # MongoDB 연결 정보

# MongoDB 클라이언트 생성
client = MongoClient(MONGO_URI)
db = client["Log"]  # 이미 존재하는 DB 이름
collection = db["log_DB"]  # 이미 존재하는 Collection 이름

def save_to_mongo(query, answer):
    """
    MongoDB에 데이터를 저장하는 함수
    """
    log_entry = {
        "query": query,
        "answer": answer,
        "ts": datetime.now(timezone.utc)  # UTC 시간 저장
    }
    collection.insert_one(log_entry)  # 데이터 삽입
    print(f"Log saved to MongoDB: {log_entry}")
