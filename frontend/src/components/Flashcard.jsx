import React from 'react'; // Removed useState
import './Flashcard.css';

// MODIFIED: Component is now controlled by props
function Flashcard({ question, answer, isFlipped, onClick }) {
  return (
    <div className="flashcard-container" onClick={onClick}>
      <div className={`flashcard-inner ${isFlipped ? 'is-flipped' : ''}`}>
        <div className="flashcard-front">
          <h4>{question}</h4>
          <small>Click to reveal</small>
        </div>
        <div className="flashcard-back">
          <p>{answer}</p>
        </div>
      </div>
    </div>
  );
}

export default Flashcard;