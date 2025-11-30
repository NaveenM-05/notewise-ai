import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiGetStudySets, apiGetTodaysReview, apiDeleteStudySet } from '../api/apiClient';
import LoadingSpinner from '../components/LoadingSpinner';
import './DashboardPage.css';

function DashboardPage() {
    const [studySets, setStudySets] = useState([]);
    const [todayReview, setTodayReview] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [setsData, reviewData] = await Promise.all([
                apiGetStudySets(),
                apiGetTodaysReview()
            ]);
            const normalizedSets = setsData?.value ?? setsData;
            const normalizedReview = reviewData?.value ?? reviewData;
            setStudySets(Array.isArray(normalizedSets) ? normalizedSets : []);
            setTodayReview(Array.isArray(normalizedReview) ? normalizedReview : []);
        } catch (error) {
            console.error("Failed to fetch dashboard data:", error);
        }
        setIsLoading(false);
    };

    useEffect(() => { fetchData(); }, []);

    const handleDelete = async (setId) => {
        if (window.confirm("Delete this study set?")) {
            try {
                await apiDeleteStudySet(setId);
                fetchData();
            } catch (error) {
                alert("Failed to delete set");
            }
        }
    };

    if (isLoading) return <LoadingSpinner />;

    return (
        <div className="dashboard-page">
            <h1>My Dashboard</h1>

            {/* Today's Review */}
            <div className="todays-review">
                <h2>Today's Review</h2>
                {todayReview.length > 0 ? (
                    <div className="review-grid">
                        {todayReview.map(set => (
                            <div className="review-card-wrapper" key={set.setId}>
                                <Link to={`/study/${set.setId}?mode=due`} className="review-card">
                                    <h3>{set.title}</h3>
                                    <p>{set.dueCardCount} cards due today</p>
                                    <span className="review-now-btn">Review Now</span>
                                </Link>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-review">
                        <p>You have no cards due for review today. Great job!</p>
                    </div>
                )}
            </div>
            
            {/* Study Sets */}
            <h2>All Study Sets</h2>
            {studySets.length > 0 ? (
                <div className="study-set-grid">
                    {studySets.map(set => (
                        <div key={set.id} className="study-set-card">
                            <div className="card-header">
                                <h3>{set.title}</h3>
                                <button className="delete-btn" onClick={() => handleDelete(set.id)}>✕</button>
                            </div>
                            <div className="stats-row">
                                <p>{set.card_count} cards</p>
                                {set.mastery_score > 0 && (
                                    // FIXED: Added Math.round() here
                                    <span className="mastery-badge">Mastery: {Math.round(set.mastery_score)}%</span>
                                )}
                            </div>
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
                    <h3>No study sets yet.</h3>
                    <Link to="/generate" className="action-link">Generate Your First Set</Link>
                </div>
            )}
        </div>
    );
}

export default DashboardPage;