import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiGetArenaChallenge, apiSubmitArena, apiRegenerateArena } from '../api/apiClient';
import LoadingSpinner from '../components/LoadingSpinner';
import './ApplicationArenaPage.css';

function ApplicationArenaPage() {
    const { setId } = useParams();
    const [challenge, setChallenge] = useState(null);
    const [userResponse, setUserResponse] = useState("");
    const [gradingResult, setGradingResult] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isGrading, setIsGrading] = useState(false);

    // Initial Load
    useEffect(() => {
        const fetchChallenge = async () => {
            try {
                const data = await apiGetArenaChallenge(setId);
                setChallenge(data);
            } catch (err) {
                console.error("Failed to load arena", err);
            }
            setIsLoading(false);
        };
        fetchChallenge();
    }, [setId]);

    // Handle Submission for Grading
    const handleSubmit = async () => {
        if (!userResponse.trim()) return;
        setIsGrading(true);
        try {
            // Call AI grading endpoint
            const result = await apiSubmitArena(setId, challenge.id, userResponse);
            setGradingResult(result);
        } catch (err) {
            alert("Failed to submit for grading");
        }
        setIsGrading(false);
    };

    // Handle Generating a New Scenario
    const handleTryAnother = async () => {
        setIsLoading(true);
        try {
            // 1. Tell Backend to Generate New Scenario
            await apiRegenerateArena(setId);
            
            // 2. Reset UI State
            setGradingResult(null);
            setUserResponse("");
            setIsGrading(false);
            
            // 3. Fetch the Newly Generated Data
            const data = await apiGetArenaChallenge(setId);
            setChallenge(data);
        } catch (err) {
            console.error("Regeneration failed", err);
            alert("Failed to generate a new scenario. Please try again.");
        }
        setIsLoading(false);
    };

    if (isLoading) return <LoadingSpinner />;
    if (!challenge) return <div className="arena-page"><p>No application scenario found.</p></div>;

    // --- RESULTS VIEW (Graded) ---
    if (gradingResult) {
        return (
            <div className="arena-page result">
                <div className="result-card">
                    <h2>AI Assessment Complete</h2>
                    
                    <div className="score-display large">
                        {gradingResult.ai_score}<span className="out-of">/100</span>
                    </div>
                    
                    <div className="feedback-section">
                        <h3>🤖 AI Feedback:</h3>
                        <p className="feedback-text">"{gradingResult.ai_feedback}"</p>
                    </div>

                    <div className="comparison-box">
                        <h4>Ideal Response was:</h4>
                        <p>{challenge.ideal_response}</p>
                    </div>

                    <div className="actions">
                        <Link to="/" className="action-link">Back to Dashboard</Link>
                        {/* This button now triggers AI regeneration instead of just reloading */}
                        <button onClick={handleTryAnother} className="retry-btn">Try Another</button>
                    </div>
                </div>
            </div>
        );
    }

    // --- INPUT VIEW (Scenario) ---
    return (
        <div className="arena-page">
            <div className="arena-header">
                <h1>Application Arena ⚔️</h1>
                <span className="topic-tag">{challenge.related_topic_tag || "General"}</span>
            </div>

            <div className="scenario-card">
                <h3>The Scenario:</h3>
                <p>{challenge.scenario}</p>
            </div>

            <div className="response-area">
                <h3>Your Solution:</h3>
                <textarea 
                    placeholder="Type your detailed solution here..." 
                    value={userResponse}
                    onChange={(e) => setUserResponse(e.target.value)}
                    disabled={isGrading}
                    rows={6}
                />
            </div>

            <button 
                className="submit-arena-btn" 
                onClick={handleSubmit} 
                disabled={isGrading || !userResponse.trim()}
            >
                {isGrading ? "🤖 AI is Grading..." : "Submit for AI Review"}
            </button>
        </div>
    );
}

export default ApplicationArenaPage;