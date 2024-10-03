import React, { useState } from 'react';
import './styles/App.css';
import Chat from './Chat'; 
import logo from './icons/cfa-logo.png';

function MainPage() {
  const [isOrdering, setIsOrdering] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, sender: "bot", content: "Hi, I am Chick-Fil-AI. Ask me anything about our menu or type your order!" }
  ]);

  const handleClick = () => {
    setIsOrdering(true);
    setTimeout(() => {
      setShowChat(true); 
    }, 1000);
  };

  const handleUserMessage = (userMessage) => {
    const newMessage = { id: messages.length + 1, sender: "user", content: userMessage };
    setMessages([...messages, newMessage]);

    //mock response for the chatbot
    setTimeout(() => {
      const botResponse = {
        id: messages.length + 2,
        sender: "bot",
        content: `You asked about: "${userMessage}". I'm still learning!`
      };
      setMessages((prevMessages) => [...prevMessages, botResponse]);
    }, 1000);
  };

  return (
    <div className="MainPage">
      <header className="top-bar"></header>
      <img src={logo} alt="Chick-Fil-A Logo" className="logo" />
      <div className="logo-container">
        <div className={`input-container ${isOrdering ? 'transform' : ''}`}>
          <input
            type="text"
            className={`order-input ${isOrdering ? 'transform' : 'initial'}`}
            placeholder="Place Your Order"
            readOnly={!isOrdering}
            onClick={handleClick}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && isOrdering) {
                handleUserMessage(e.target.value);  
                e.target.value = ""; 
              }
            }}
          />
          <span className="arrow-icon"></span>
        </div>
      </div>
      <div className="settings"></div>
      {showChat && <Chat messages={messages} />} {/** render the chat messages after pressing button */}
    </div>
  );
}

export default MainPage;
