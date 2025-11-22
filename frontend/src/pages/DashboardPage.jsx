import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiGetStudySets, apiGetTodaysReview } from '../api/apiClient'; // MODIFIED: Use real API for both
import LoadingSpinner from '../components/LoadingSpinner';
import './DashboardPage.css';

function DashboardPage() {
    const [studySets, setStudySets] = useState([]);
    const [todayReview, setTodayReview] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            setIsLoading(true);
            try {
                // MODIFIED: Now calling the REAL backend for both lists
                const [setsData, reviewData] = await Promise.all([
                    apiGetStudySets(),
                    apiGetTodaysReview() 
                ]);
                setStudySets(setsData);
                setTodayReview(reviewData);
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error);
            }
            setIsLoading(false);
        };
        fetchDashboardData();
    }, []);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="dashboard-page">
            <h1>My Dashboard</h1>

            {/* Today's Review Section */}
            <div className="todays-review">
                <h2>Today's Review</h2>
                {todayReview.length > 0 ? (
                    <div className="review-grid">
                        {todayReview.map(set => (
                            <Link to={`/study/${set.setId}`} className="review-card" key={set.setId}>
                                <h3>{set.title}</h3>
                                <p>{set.dueCardCount} cards due</p>
                                <span className="review-now-btn">Review Now</span>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <div className="empty-review">
                        <p>You have no cards due for review today. Great job!</p>
                    </div>
                )}
            </div>
            
            {/* All Study Sets Section */}
            <h2>All Study Sets</h2>
            
            {studySets.length > 0 ? (
                <div className="study-set-grid">
                    {studySets.map(set => (
                        <div key={set.id} className="study-set-card">
                            <h3>{set.title}</h3>
                            <p>{set.card_count} cards</p>
                            <div className="card-actions">
                                 <Link to={`/study/${set.id}`} className="action-link">Study</Link>
                                 <Link to={`/quiz/${set.id}`} className="action-link quiz">Quiz</Link>
                                 <Link to={`/arena/${set.id}`} className="action-link">Arena</Link>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <h3>You haven't created any study sets yet.</h3>
                    <p>Click the "Generate" button to upload a PDF and get started!</p>
                    <Link to="/generate" className="action-link">
                        Generate Your First Set
                    </Link>
                </div>
            )}
        </div>
    );
}

export default DashboardPage;