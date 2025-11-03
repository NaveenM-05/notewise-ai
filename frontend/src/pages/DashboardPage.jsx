import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
// MODIFIED: Import the new fake function
import { getStudySets_FAKE, getTodaysReview_FAKE } from '../api/mockApi';
import './DashboardPage.css';

function DashboardPage() {
    const [studySets, setStudySets] = useState([]);
    const [todayReview, setTodayReview] = useState([]); // MODIFIED: New state for today's review
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Now fetches both sets of data
        const fetchDashboardData = async () => {
            setIsLoading(true);
            try {
                // Use Promise.all to fetch both in parallel
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
    }, []); // The empty array [] ensures this runs only once

    if (isLoading) {
        return <p>Loading your dashboard...</p>;
    }

    return (
        <div className="dashboard-page">
            <h1>My Dashboard</h1>

            {/* --- NEW SECTION: TODAY'S REVIEW --- */}
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
            {/* ---------------------------------- */}

            <h2>All Study Sets</h2>
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
        </div>
    );
}

export default DashboardPage;