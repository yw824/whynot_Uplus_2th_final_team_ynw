import React, { useEffect, useState } from "react";
import './App.css';

function App() {
  const [messages, setMessages] = useState([]); // 서버에서 받은 메시지 저장
  const [error, setError] = useState(false); // 에러 상태
  const [ended, setEnded] = useState(false); // 상담 종료 여부

  useEffect(() => {
    const websocket = new WebSocket("ws://127.0.0.1:8000/chat");

    websocket.onopen = () => {
      console.log("상담이 연결되었습니다.");
      setError(false); // 서버 연결 성공 시 에러 상태 초기화
    };

    websocket.onmessage = (event) => {
      try {
        const parsedMessage = JSON.parse(event.data); // JSON 파싱
        const { label, position, message } = parsedMessage;

        setMessages((prevMessages) => [
          ...prevMessages,
          { label, position, message },
        ]);

        if (label === "종료" && position === "center" && message === "상담이 종료되었습니다.") {
          setEnded(true);
          websocket.close();
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    websocket.onerror = () => {
      console.error("WebSocket 에러 발생");
      setError(true); // 에러 발생 시 상태를 true로 설정
    };

    websocket.onclose = () => {
      console.log("WebSocket 연결이 종료되었습니다.");
      setError(true); // 연결 종료 시 에러 상태를 true로 설정
    };

    return () => {
      websocket.close();
    };
  }, []);

  return (
    <div id="chat-wrapper">
      <div id="chat-header">실시간 대화록</div>
      <div id="chat-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.position}`}>
            <div className="label">{msg.label}</div>
            <div className="bubble">{msg.message}</div>
          </div>
        ))}
      </div>
      {error && !ended && (
        <div id="error-message">서버와의 연결이 끊어졌습니다. 연결을 복구 중입니다...</div>
      )}
      {ended && <div id="end-message">상담이 종료되었습니다.</div>}
    </div>
  );
}

export default App;
