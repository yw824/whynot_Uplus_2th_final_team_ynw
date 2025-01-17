import React, { useState, useRef } from "react";

const ChatForm = ({ chatHistory, setChatHistory, generateBotResponse }) => {
  const inputRef = useRef();

  const handleFormSubmit = (e) => {
    e.preventDefault();
    const userMessage = inputRef.current.value.trim();
    if (!userMessage) return; // 메시지가 없으면 리턴
    inputRef.current.value = ""; // 입력 필드 비우기

    // 사용자 메시지 chatHistory에 추가
    setChatHistory((history) => [
      ...history,
      { role: "user", text: userMessage },
    ]);

    // Thinking... 메시지 추가 후, generateBotResponse 호출
    setTimeout(() => {
      // Thinking... 메시지를 chatHistory에 추가
      setChatHistory((history) => [
        ...history,
        { role: "model", text: "Thinking..." },
      ]);

      // generateBotResponse에 사용자 메시지만 전달 (chatHistory 대신)
      generateBotResponse(userMessage); // userMessage를 전송
    }, 600); // 딜레이를 600ms로 설정
  };

  return (
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
  );
};

export default ChatForm;
