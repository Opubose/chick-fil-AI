import React from 'react';
import './styles/Chat.css';
import userIcon from './icons/user-icon.svg';
import botIcon from './icons/cfa-cow-icon.svg';

function Chat() {
  return (
    <div className="chat-container">
      <button className="menu-button">View Menu</button>
      <div className="chat">
        <div className="message bot">
          <img src={botIcon} alt="Bot Icon" className="icon" />
          <div className='response'>
            Hi, I am Chick-Fil-AI. Ask me anything about our menu or type your order!
          </div>
        </div>
        <div className="message user">
          <img src={userIcon} alt="User Icon" className="icon" />
          <div className='response'>
            Hi, how many calories are in your 8 count nugget?
          </div>
        </div>
        
      </div>
    </div>
  );
}

export default Chat;
