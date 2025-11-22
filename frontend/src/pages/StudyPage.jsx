import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiGetFlashcards, apiSaveReview } from '../api/apiClient';
import Flashcard from '../components/Flashcard';
import PomodoroTimer from '../components/PomodoroTimer';
import LoadingSpinner from '../components/LoadingSpinner';
import './StudyPage.css';

function StudyPage() {
    const { setId } = useParams();
    const [flashcards, setFlashcards] = useState([]);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isCardFlipped, setIsCardFlipped] = useState(false);
    const [isSessionComplete, setIsSessionComplete] = useState(false);

    useEffect(() => {
        const fetchCards = async () => {
            setIsLoading(true);
            try {
                const cards = await apiGetFlashcards(setId);
                setFlashcards(cards);
            } catch (err) {
                console.error("Failed to load cards", err);
            }
            setIsLoading(false);
        };
        fetchCards();
    }, [setId]);

    const handleReview = async (difficulty) => {
        if (!flashcards[currentCardIndex]) return;
        
        const cardId = flashcards[currentCardIndex].id;
        
        try {
             // Send the SM-2 rating to the backend
             await apiSaveReview(cardId, difficulty);
        } catch (e) {
            console.error("Failed to save review:", e);
        }
        
        // Move to next card
        if (currentCardIndex < flashcards.length - 1) {
            setIsCardFlipped(false);
            setCurrentCardIndex(prev => prev + 1);
        } else {
            setIsSessionComplete(true);
        }
    };

    const handleSkip = () => {
        if (currentCardIndex < flashcards.length - 1) {
            setIsCardFlipped(false);
            setCurrentCardIndex(prev => prev + 1);
        } else {
            setIsSessionComplete(true);
        }
    };

    if (isLoading) return <LoadingSpinner />;

    if (flashcards.length === 0) {
        return (
            <div className="study-page empty">
                <h2>No cards found</h2>
                <p>This study set seems to be empty.</p>
                <Link to="/" className="action-link">Back to Dashboard</Link>
            </div>
        );
    }

    if (isSessionComplete) {
        return (
            <div className="study-page complete">
                <div className="completion-card">
                    <h2>🎉 Session Complete!</h2>
                    <p>You've reviewed all the cards in this set.</p>
                    <Link to="/" className="action-link">Back to Dashboard</Link>
                </div>
            </div>
        );
    }

    const currentCard = flashcards[currentCardIndex];

    return (
        <div className="study-page">
            <div className="header-section">
                <h1>Study Session</h1>
                <p className="progress-text">Card {currentCardIndex + 1} of {flashcards.length}</p>
            </div>
            
            <div className="study-area">
                <div className="flashcard-viewer">
                    <Flashcard 
                        question={currentCard.question}
                        answer={currentCard.answer}
                        isFlipped={isCardFlipped}
                        onClick={() => setIsCardFlipped(!isCardFlipped)}
                    />
                    
                    {/* Only show rating buttons if card is flipped */}
                    {isCardFlipped ? (
                        <div className="feedback-controls">
                            <p>How well did you know this?</p>
                            <button className="feedback-btn again" onClick={() => handleReview('again')}>Again</button>
                            <button className="feedback-btn good" onClick={() => handleReview('good')}>Good</button>
                            <button className="feedback-btn easy" onClick={() => handleReview('easy')}>Easy</button>
                        </div>
                    ) : (
                        <div className="instruction-hint">
                            <p>Click the card to reveal the answer</p>
                        </div>
                    )}

                    <div className="navigation-controls">
                        <button onClick={handleSkip} className="next-btn">Skip Card →</button>
                    </div>
                </div>
                
                <div className="pomodoro-container">
                    <PomodoroTimer />
                </div>
            </div>
        </div>
    );
}

export default StudyPage;