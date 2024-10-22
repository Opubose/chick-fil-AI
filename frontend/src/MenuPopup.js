import React from 'react';
import './styles/MenuPopup.css'; 

function MenuPopup({ isVisible, onClose, imgSrc }) {
  if (!isVisible) return null; 

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <button className="close-button" onClick={onClose}>
          &times; 
        </button>
        <img src={imgSrc} alt="Menu" className="popup-image" />
      </div>
    </div>
  );
}

export default MenuPopup;
