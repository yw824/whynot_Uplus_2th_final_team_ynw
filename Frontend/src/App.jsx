import React, { useState } from "react";
import LiveChatApp from "./components/LiveChat/LiveChatApp";
import ChatbotIcon from "./components/ChatbotIcon";
import ChatForm from "./components/ChatForm";
import ChatMessage from "./components/ChatMessage";

const App = () => {
  const [chatHistory, setChatHistory] = useState([
    {
      hideInChat: true,
      role: "model",
      text: "안녕하세요! 무엇을 도와드릴까요?",
    },
  ]);

  const generateBotResponse = async (userMessage) => {
    const updateHistory = (text, isError = false) => {
      setChatHistory((prev) => [
        ...prev.filter((msg) => msg.text !== "Thinking..."),
        { role: "model", text, isError },
      ]);
    };

    if (!userMessage.trim()) {
      updateHistory("메시지를 입력해주세요.", true);
      return;
    }

    try {
      setChatHistory((prev) => [...prev, { role: "user", text: userMessage }]);

      console.log(chatHistory);

      const response = await fetch("http://localhost:8002/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_message: userMessage }),
      });

      if (!response.ok) throw new Error("서버 오류가 발생했습니다.");

      console.log(response);

      const data = await response.json();
      updateHistory(data.bot_response);
    } catch (error) {
      updateHistory(error.message, true);
    }
  };

  return (
    <div className="app-container">
      <div className="live-chat-section">
        <LiveChatApp />
      </div>
      <div className="chatbot-section">
        <div className="chatbot-popup">
          <div className="chat-header">
            <div className="header-info">
              <ChatbotIcon />
              <h2 className="logo-text">Chatbot</h2>
            </div>
          </div>
          <div className="chat-body">
            {chatHistory.map((chat, index) => (
              <ChatMessage key={index} chat={chat} />
            ))}
          </div>
          <div className="chat-footer">
            <ChatForm
              chatHistory={chatHistory}
              setChatHistory={setChatHistory}
              generateBotResponse={generateBotResponse}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
