import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom'; // Make sure Link is imported
import { getStudySets_FAKE, getTodaysReview_FAKE } from '../api/mockApi';
import LoadingSpinner from '../components/LoadingSpinner'; // We're using our new spinner
import './DashboardPage.css';

function DashboardPage() {
    const [studySets, setStudySets] = useState([]);
    const [todayReview, setTodayReview] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            setIsLoading(true);
            try {
                const [setsData, reviewData] = await Promise.all([
                    getStudySets_FAKE(),
                    getTodaysReview_FAKE()
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

            {/* --- Today's Review Section --- */}
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
                    <p>You have no cards due for review today. Great job!</p>
                )}
            </div>
            
            {/* --- All Study Sets Section (WITH NEW LOGIC) --- */}
            <h2>All Study Sets</h2>
            
            {studySets.length > 0 ? (
                // If we HAVE sets, show the grid
                <div className="study-set-grid">
                    {studySets.map(set => (
                        <div key={set.id} className="study-set-card">
                            <h3>{set.title}</h3>
                            <p>{set.cardCount} cards</p>
                            <div className="card-actions">
                                 <Link to={`/study/${set.id}`} className="action-link">Study</Link>
                                 <Link to={`/quiz/${set.id}`} className="action-link quiz">Quiz</Link>
                                 <Link to={`/arena/${set.id}`} className="action-link">Arena</Link>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                // If we have NO sets, show the "Empty State"
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
