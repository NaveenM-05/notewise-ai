import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getQuizData_FAKE } from '../api/mockApi';
import './QuizPage.css';

function QuizPage() {
    const { setId } = useParams();
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [isAnswered, setIsAnswered] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchQuiz = async () => {
            setIsLoading(true);
            const data = await getQuizData_FAKE(setId);
            setQuestions(data);
            setIsLoading(false);
        };
        fetchQuiz();
    }, [setId]);

    const handleAnswerSelect = (option) => {
        if (isAnswered) return; // Don't let them change their answer
        
        setSelectedAnswer(option);
        setIsAnswered(true);

        if (option === questions[currentQuestionIndex].correctAnswer) {
            setScore(score + 1);
        }
    };

    const handleNextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setIsAnswered(false);
            setSelectedAnswer(null);
        } else {
            // End of the quiz
            setShowResults(true);
        }
    };

    if (isLoading) return <p>Loading quiz...</p>;
    if (questions.length === 0) return <p>No quiz found for this set.</p>;

    // Show final score screen
    if (showResults) {
        return (
            <div className="quiz-container results">
                <h1>Quiz Complete!</h1>
                <h2>Your Score: {score} / {questions.length}</h2>
                <Link to="/" className="action-link">Back to Dashboard</Link>
            </div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];

    // Helper function to get button style
    const getOptionClass = (option) => {
        if (!isAnswered) return "option-btn"; // Not answered yet
        if (option === currentQuestion.correctAnswer) return "option-btn correct"; // This is the correct answer
        if (option === selectedAnswer) return "option-btn incorrect"; // This is the wrong one they picked
        return "option-btn"; // Other wrong answers
    };

    return (
        <div className="quiz-container">
            <h1>Quiz Time!</h1>
            <div className="quiz-progress">
                Question {currentQuestionIndex + 1} of {questions.length}
            </div>
            <h3>{currentQuestion.question}</h3>
            
            <div className="options-grid">
                {currentQuestion.options.map((option, index) => (
                    <button 
                        key={index}
                        className={getOptionClass(option)}
                        onClick={() => handleAnswerSelect(option)}
                        disabled={isAnswered}
                    >
                        {option}
                    </button>
                ))}
            </div>

            {isAnswered && (
                <button onClick={handleNextQuestion} className="next-btn">
                    {currentQuestionIndex < questions.length - 1 ? "Next Question" : "Show Results"}
                </button>
            )}
        </div>
    );
}

export default QuizPage;