import React, { useState } from "react";
import "./styles/App.css";
import Chat from "./Chat";
import logo from "./images/cfa-logo.png";

function MainPage() {
  const [isOrdering, setIsOrdering] = useState(false);
  const [isBotThinking, setIsBotThinking] = useState(false);
  const [chatState, setChatState] = useState('initial');  
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      content: "Hi, I am Chick-Fil-AI. Ask me anything about our menu or type your order!",
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleClick = () => {
    if (!isOrdering) {
      setIsOrdering(true);
      setChatState('expanded');  
    }
  };

  
  const sendMessage = async (userMessage) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_message: userMessage }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data.bot_message);
        return data.bot_message;
      } else {
        return "Sorry, I'm having trouble connecting to the server.";
      }
    } catch (error) {
      console.error("Error communicating with the backend:", error);
      return "Sorry, I couldn't process your request.";
    }
  };

  const handleUserMessage = async (userMessage) => {
    const userMsgObj = {
      id: messages.length + 1,
      sender: "user",
      content: userMessage,
    };
    setMessages([...messages, userMsgObj]);

    setIsBotThinking(true);
    const botResponse = await sendMessage(userMessage);
    setIsBotThinking(false);

    const botMsgObj = {
      id: messages.length + 2,
      sender: "bot",
      content: botResponse,
    };
    setMessages((prevMessages) => [...prevMessages, botMsgObj]);
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    const textarea = e.target;
    if (textarea.scrollHeight > textarea.offsetHeight) {
      textarea.style.height = `${textarea.scrollHeight - 30}px`;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && isOrdering) {
      e.preventDefault();
      const userMessage = inputValue.trim();
      if (userMessage) {
        handleUserMessage(userMessage);
        setInputValue(""); 
      }
    }
  };

  return (
    <div className="MainPage">
      <header className="top-bar"></header>
      <img src={logo} alt="Chick-Fil-A Logo" className="logo" />
      <div className="settings"></div>
      <div className="menu-container">
        <button className="menu-button">View Menu</button>
      </div>

      <div className={`chat-container ${chatState}`}>
        {chatState === 'expanded' && <Chat messages={messages} isBotThinking={isBotThinking}/>}
      </div>

      {/* Input field with click handler to trigger ordering */}
      <div className={`input-container ${isOrdering ? "transform" : ""}`}>
        <textarea
          className={`order-input ${isOrdering ? "transform" : ""}`}
          placeholder="Place Your Order"
          readOnly={!isOrdering}
          onClick={handleClick}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
        ></textarea>
      </div>
    </div>
  );
}

export default MainPage;
