import React, { useState } from "react";
import "./styles/App.css";
import Chat from "./Chat";
import MenuPopup from "./MenuPopup"; 
import logo from "./images/cfa-logo.png";
import phone_icon from "./images/phone-icon.svg";
import menuImage from "./images/cfa-menu.png"; 

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
  const [isPopupVisible, setIsPopupVisible] = useState(false); 

  const handleClick = () => {
    if (!isOrdering) {
      setIsOrdering(true);
      setChatState('expanded');
    }
  };

  const handleMenuClick = () => {
    setIsPopupVisible(true); 
  };

  const handleClosePopup = () => {
    setIsPopupVisible(false); 
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
        return data.bot_message;
      } else {
        return "Sorry, I'm having trouble connecting to the server.";
      }
    } catch (error) {
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
    const textarea = e.target;
    setInputValue(textarea.value);
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 150); 
    textarea.style.height = `${newHeight}px`;
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
      <div className="top-bar">
        <div className="menu-container" onClick={handleMenuClick}>
          <button className="menu-button">
            View Menu
          </button>
          <img src={phone_icon} alt="Phone icon" className="phone-icon" />
        </div>
        <img src={logo} alt="Chick-Fil-A Logo" className="logo" />
      </div>

      <div className={`chat-container ${chatState}`}>
        {chatState === 'expanded' && <Chat messages={messages} isBotThinking={isBotThinking} />}
      </div>

      <MenuPopup isVisible={isPopupVisible} onClose={handleClosePopup} imgSrc={menuImage} />

      <div className={`input-container ${isOrdering ? "transform" : ""}`}>
        <textarea
          className={`order-input ${isOrdering ? "transform" : ""}`}
          placeholder="Place Your Order"
          readOnly={!isOrdering}
          onClick={handleClick}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          rows={1}
        ></textarea>
      </div>
    </div>
  );
}

export default MainPage;
