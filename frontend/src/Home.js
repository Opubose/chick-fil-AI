import React, { useState } from 'react';
import './styles/App.css';
import logo from './Chick-fil-A-logo.png';

function Home() {
  const [isOrdering, setIsOrdering] = useState(false);

  const handleOrderClick = () => {
    setIsOrdering(true); 
  };

  return (
    <div className="frame1">
      <header className="top-bar"></header>
      <img src={logo} alt="Chick-Fil-A Logo" className="logo" />
      <div className="logo-container">
        <button 
          className={`order-button ${isOrdering ? 'transform' : ''}`}
          onClick={handleOrderClick}
        >
          {!isOrdering ? (
            <>
              <span className="button-text">Place Your Order</span>
              <span className="arrow-icon"></span>
            </>
          ) : (
            <input
              type="text"
              className="order-input"
              placeholder="Type your order here..."
            />
          )}
        </button>
      </div>
      <div className="settings"></div>
    </div>
  );
}

export default Home;
