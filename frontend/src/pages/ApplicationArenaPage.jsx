import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getArenaChallenge_FAKE } from '../api/mockApi';
import LoadingSpinner from '../components/LoadingSpinner';
import './ApplicationArenaPage.css';

function ApplicationArenaPage() {
    const { setId } = useParams();
    const [challenge, setChallenge] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [userAnswer, setUserAnswer] = useState('');
    const [isAnswerRevealed, setIsAnswerRevealed] = useState(false);

    useEffect(() => {
        const fetchChallenge = async () => {
            setIsLoading(true);
            const data = await getArenaChallenge_FAKE(setId);
            setChallenge(data);
            setIsLoading(false);
        };
        fetchChallenge();
    }, [setId]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="arena-page">
            <h1>Application Arena</h1>
            <div className="challenge-card">
                <h3>Your Challenge:</h3>
                <p>{challenge.challenge}</p>

                <textarea
                    placeholder="Type your answer here..."
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    rows="8"
                />

                <button onClick={() => setIsAnswerRevealed(true)} disabled={isAnswerRevealed}>
                    Reveal AI's Approach
                </button>

                {isAnswerRevealed && (
                    <div className="ideal-answer">
                        <h4>Ideal Approach:</h4>
                        <p>{challenge.idealAnswer}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ApplicationArenaPage;
