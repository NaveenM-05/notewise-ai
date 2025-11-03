import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
// MODIFIED: Import the new fake function
import { getFlashcardsForSet_FAKE, saveReview_FAKE } from '../api/mockApi';
import Flashcard from '../components/Flashcard';
import PomodoroTimer from '../components/PomodoroTimer';
import './StudyPage.css'; // We'll add new styles to this

function StudyPage() {
    const { setId } = useParams();
    const [flashcards, setFlashcards] = useState([]);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isCardFlipped, setIsCardFlipped] = useState(false); // To control flipping

    useEffect(() => {
        const fetchCards = async () => {
            setIsLoading(true);
            const cards = await getFlashcardsForSet_FAKE(setId);
            setFlashcards(cards);
            setIsLoading(false);
        };
        fetchCards();
    }, [setId]);

    // MODIFIED: New function to handle user's review
    const handleReview = async (difficulty) => {
        if (!flashcards[currentCardIndex]) return;

        const cardId = flashcards[currentCardIndex].id;
        await saveReview_FAKE(cardId, difficulty);
        
        // Move to the next card
        goToNextCard();
    };

    const goToNextCard = () => {
        setIsCardFlipped(false); // Flip back to the question
        setCurrentCardIndex((prevIndex) => (prevIndex + 1) % flashcards.length);
    };

    if (isLoading) {
        return <p>Loading study session...</p>;
    }

    if (flashcards.length === 0) {
        return <p>This study set has no cards.</p>
    }

    const currentCard = flashcards[currentCardIndex];

    return (
        <div className="study-page">
            <div className="study-area">
                <div className="flashcard-viewer">
                    <Flashcard 
                        question={currentCard.question}
                        answer={currentCard.answer}
                        isFlipped={isCardFlipped} // Control flip state
                        onClick={() => setIsCardFlipped(!isCardFlipped)} // Allow clicking to flip
                    />
                    
                    {/* --- NEW: SRS Feedback Buttons --- */}
                    {isCardFlipped && (
                        <div className="feedback-controls">
                            <p>How well did you know this?</p>
                            <button className="feedback-btn again" onClick={() => handleReview('again')}>Again</button>
                            <button className="feedback-btn good" onClick={() => handleReview('good')}>Good</button>
                            <button className="feedback-btn easy" onClick={() => handleReview('easy')}>Easy</button>
                        </div>
                    )}

                    {/* --- MODIFIED: Simpler Navigation --- */}
                    <div className="navigation-controls">
                        <span>Card {currentCardIndex + 1} of {flashcards.length}</span>
                        <button onClick={goToNextCard} className="next-btn">Skip Card →</button>
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