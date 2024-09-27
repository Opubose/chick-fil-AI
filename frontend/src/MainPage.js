import React, { useState } from 'react';
import './styles/App.css';
import Chat from './Chat'; 
import logo from './icons/cfa-logo.png';

function MainPage() {
  const [isOrdering, setIsOrdering] = useState(false);
  const [showChat, setShowChat] = useState(false); 

  const handleClick = () => {
    setIsOrdering(true);
    setTimeout(() => {
      setShowChat(true); // Show Chat component after a delay
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
          />
          <span className="arrow-icon"></span>
        </div>
      </div>
      <div className="settings"></div>
      {showChat && <Chat />}
    </div>
  );
}

export default MainPage;
