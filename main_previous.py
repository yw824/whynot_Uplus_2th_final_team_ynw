from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import asyncio
from datetime import datetime
import streamlit as st

app = FastAPI()

# Static 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 엑셀 파일 경로
EXCEL_FILE = "dialog.xlsx"

# 엑셀 데이터를 읽어오는 함수
def load_dialog_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df[["Role", "Message"]].values.tolist()

# SSE 스트리밍을 위한 대화 데이터를 가져오는 함수
async def chat_stream():
    dialog = load_dialog_from_excel(EXCEL_FILE)
    for role, message in dialog:
        # 현재 시간 추가
        now = datetime.now().strftime("%H:%M:%S")
        # Role에 따른 라벨
        label = f"[고객:1234]" if role == "고객" else "[상담사:김상담]"
        # 클라이언트로 데이터 전송 (라벨과 메시지를 분리)
        yield f"data: {label} {now};;{message}\n\n"  # 구분자로 ";;" 사용
        await asyncio.sleep(6)

@app.get("/chat")
async def stream_chat():
    return StreamingResponse(chat_stream(), media_type="text/event-stream")


# HTML 렌더링
@app.get("/", response_class=HTMLResponse)
async def serve_html():
    with open("static/chat.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

@app.post("/dialog")
async def input_dialog(voice: str):
    print(voice)
    return voice


# streamlit run main.py
# uvicorn main:app --reload

