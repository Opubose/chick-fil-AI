import React, { useState } from "react";
import "./styles/App.css";
import Chat from "./Chat";
import logo from "./images/cfa-logo.png";

function MainPage() {
  const [isOrdering, setIsOrdering] = useState(false);
  const [isBotThinking, setIsBotThinking] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      content:
        "Hi, I am Chick-Fil-AI. Ask me anything about our menu or type your order!",
    },
  ]);

  const handleClick = () => {
    setIsOrdering(true);
    setTimeout(() => {
      setShowChat(true);
    }, 1000);
  };

  // Handle sending a message to the backend
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
  
    setIsBotThinking(true); // Bot starts "thinking"
    const botResponse = await sendMessage(userMessage);
    setIsBotThinking(false); // Bot finishes "thinking"
  
    const botMsgObj = {
      id: messages.length + 2,
      sender: "bot",
      content: botResponse,
    };
    setMessages((prevMessages) => [...prevMessages, botMsgObj]);
  };

  return (
    <div className="MainPage">
      <header className="top-bar"></header>
      <img src={logo} alt="Chick-Fil-A Logo" className="logo" />
      <div className="logo-container"></div>
      <div className="settings"></div>
      <div className="menu-container">
        <button className="menu-button">View Menu</button>
      </div>
      {showChat && <Chat messages={messages} isBotThinking={isBotThinking} />}
{" "}
      {/** render the chat messages after pressing button */}
      <div className={`input-container ${isOrdering ? "transform" : ""}`}>
        <input
          type="text"
          className={`order-input ${isOrdering ? "transform" : "initial"}`}
          placeholder="Place Your Order"
          readOnly={!isOrdering}
          onClick={handleClick}
          onKeyDown={(e) => {
            if (e.key === "Enter" && isOrdering) {
              handleUserMessage(e.target.value);
              e.target.value = "";
            }
          }}
        />
        <span
          className="arrow-icon"
          onClick={() => {
            if (isOrdering) { 
              const inputElement = document.querySelector(".order-input");
              const userMessage = inputElement.value.trim();
              console.log("y")
              if (userMessage) {
                handleUserMessage(userMessage);
                inputElement.value = ""; 
              }
            }
          }}
        ></span>
      </div>
    </div>
  );
}

export default MainPage;
