import React from 'react';
import './styles/App.css';


function Chat() {
  return (
    <div className="frame2">
      <header className="top-bar">
        {/* Top bar content */}
      </header>
      <div className="chat-container">
        <button className="menu-button">View Menu</button>
        <div className="chat-bubble">
        </div>
        <div className="customer-message">
        </div>
        <input
          type="text"
          className="order-input"
          placeholder="Type your order here..."
        />
      </div>
    </div>
  );
}

export default Chat;
