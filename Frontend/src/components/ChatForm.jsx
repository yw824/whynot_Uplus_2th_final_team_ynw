import React, { useRef, useEffect } from "react";

const ChatForm = ({ generateBotResponse, chatHistory }) => {
  const inputRef = useRef();
  const chatBodyRef = useRef();

  // 채팅 메시지가 추가될 때마다 스크롤 위치 업데이트
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleFormSubmit = (e) => {
    e.preventDefault();
    const userMessage = inputRef.current.value.trim();
    if (!userMessage) return;

    // 입력 필드 초기화
    inputRef.current.value = "";

    // 메시지 전송
    generateBotResponse(userMessage);

    // 메시지 전송 후 즉시 스크롤 조정
    setTimeout(() => {
      if (chatBodyRef.current) {
        chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
      }
    }, 100);
  };

  return (
    <div className="chat-container">
      <div className="chat-messages" ref={chatBodyRef}>
        {/* 채팅 메시지들이 여기에 표시됨 */}
      </div>
      <form action="#" className="chat-form" onSubmit={handleFormSubmit}>
        <input
          ref={inputRef}
          type="text"
          placeholder="Message..."
          className="message-input"
          required
        />
        <button className="material-symbols-rounded">arrow_upward</button>
      </form>
    </div>
  );
};

export default ChatForm;
