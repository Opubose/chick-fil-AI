import React, { useEffect, useRef } from "react";
import "./styles/Chat.css";
import userIcon from "./images/user-icon.svg";
import botIcon from "./images/cfa-cow-icon.svg";

function Chat({ messages, isBotThinking }) {
  // Create a ref to access the chat container
  const chatRef = useRef(null);

  // Use useEffect to scroll to the bottom every time messages change
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, isBotThinking]);

  return (
    <div className="chat-container">
      <div className="chat" ref={chatRef}>
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <img
              src={message.sender === "user" ? userIcon : botIcon}
              alt={`${message.sender} Icon`}
              className="icon"
            />
            <div className="response">{message.content}</div>
          </div>
        ))}
        {isBotThinking && (
          <div className="message bot">
            <img src={botIcon} alt="Bot Icon" className="icon" /> 
            <div className="typing-indicator">
              <div className="typing-indicator-dot"></div>
              <div className="typing-indicator-dot"></div>
              <div className="typing-indicator-dot"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Chat;