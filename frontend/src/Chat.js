import React from 'react';
import './styles/Chat.css';
import userIcon from './icons/user-icon.svg';
import botIcon from './icons/cfa-cow-icon.svg';

function Chat({ messages }) {
  return (
    <div className="chat-container">
      <div className="chat">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <img src={message.sender === "user" ? userIcon : botIcon} alt={`${message.sender} Icon`} className="icon" />
            <div className='response'>
              {message.content}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Chat;
