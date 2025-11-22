import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiGetArenaChallenge, apiSubmitArena } from '../api/apiClient';
import LoadingSpinner from '../components/LoadingSpinner';
import './ApplicationArenaPage.css';

function ApplicationArenaPage() {
    const { setId } = useParams();
    const [challenge, setChallenge] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [userAnswer, setUserAnswer] = useState('');
    const [isAnswerRevealed, setIsAnswerRevealed] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchChallenge = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const data = await apiGetArenaChallenge(setId);
                setChallenge(data);
            } catch (err) {
                console.error("Failed to load challenge", err);
                setError("No Application Scenario found for this study set.");
            }
            setIsLoading(false);
        };
        fetchChallenge();
    }, [setId]);

    const handleSelfAssessment = async (score) => {
        // Optimistically update UI
        setIsSubmitted(true);
        try {
            // Send self-assessment score (0.0, 0.5, or 1.0) to backend
            // challenge.id is required by the backend to link the result
            await apiSubmitArena(setId, challenge.id, score);
        } catch (e) {
            console.error("Failed to submit arena score", e);
            alert("Failed to save your progress. Please check your connection.");
            setIsSubmitted(false); // Revert on failure
        }
    };

    if (isLoading) return <LoadingSpinner />;
    
    if (error || !challenge) {
        return (
            <div className="arena-page empty">
                <h2>Arena Not Available</h2>
                <p>{error || "This study set does not have an Application Scenario yet."}</p>
                <Link to="/" className="action-link">Back to Dashboard</Link>
            </div>
        );
    }

    return (
        <div className="arena-page">
            <h1>Application Arena</h1>
            <p className="subtitle">Test your ability to apply concepts in real-world scenarios.</p>
            
            <div className="challenge-card">
                <div className="scenario-section">
                    <h3>The Scenario:</h3>
                    <p className="scenario-text">{challenge.scenario}</p>
                </div>

                <div className="input-section">
                    <textarea
                        placeholder="Type your approach or solution here..."
                        value={userAnswer}
                        onChange={(e) => setUserAnswer(e.target.value)}
                        rows="6"
                        disabled={isAnswerRevealed}
                        className="answer-input"
                    />
                </div>

                {!isAnswerRevealed ? (
                    <div className="action-bar">
                        <button 
                            onClick={() => setIsAnswerRevealed(true)} 
                            disabled={!userAnswer.trim()}
                            className="reveal-btn"
                        >
                            Reveal AI Solution
                        </button>
                        {!userAnswer.trim() && <p className="hint-text">Type an answer to reveal the solution.</p>}
                    </div>
                ) : (
                    <div className="solution-section">
                        <div className="ideal-answer">
                            <h4>AI's Ideal Approach:</h4>
                            {/* Handle text from backend (ideal_response) */}
                            <p>{challenge.ideal_response}</p>
                        </div>

                        {!isSubmitted ? (
                            <div className="assessment-section">
                                <h4>Self-Assessment: How close were you?</h4>
                                <div className="assessment-buttons">
                                    <button 
                                        className="assess-btn poor" 
                                        onClick={() => handleSelfAssessment(0.0)}
                                        title="Reset progress for this topic"
                                    >
                                        ❌ Missed it
                                    </button>
                                    <button 
                                        className="assess-btn partial" 
                                        onClick={() => handleSelfAssessment(0.5)}
                                        title="Maintain current schedule"
                                    >
                                        ⚠️ Close / Partial
                                    </button>
                                    <button 
                                        className="assess-btn perfect" 
                                        onClick={() => handleSelfAssessment(1.0)}
                                        title="Boost mastery & delay reviews"
                                    >
                                        ✅ Nailed it
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="success-message">
                                <h3>Assessment Recorded!</h3>
                                <p>Your learning schedule has been updated based on your performance.</p>
                                <Link to="/" className="action-link">Return to Dashboard</Link>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default ApplicationArenaPage;