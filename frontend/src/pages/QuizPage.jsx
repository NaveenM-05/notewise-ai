import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiGetQuiz } from '../api/apiClient'; // Real API
import LoadingSpinner from '../components/LoadingSpinner';
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
            try {
                const data = await apiGetQuiz(setId);
                setQuestions(data);
            } catch (err) {
                console.error("Failed to load quiz", err);
            }
            setIsLoading(false);
        };
        fetchQuiz();
    }, [setId]);

    const handleAnswerSelect = (option) => {
        if (isAnswered) return;
        setSelectedAnswer(option);
        setIsAnswered(true);
        if (option === questions[currentQuestionIndex].correct_answer) { // Note: Python uses correct_answer
            setScore(score + 1);
        }
    };

    const handleNextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setIsAnswered(false);
            setSelectedAnswer(null);
        } else {
            setShowResults(true);
            // TODO: Call apiSubmitQuiz(setId, score) here later
        }
    };

    if (isLoading) return <LoadingSpinner />;
    if (questions.length === 0) return <p>No quiz found for this set.</p>;

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

    const getOptionClass = (option) => {
        if (!isAnswered) return "option-btn";
        if (option === currentQuestion.correct_answer) return "option-btn correct";
        if (option === selectedAnswer) return "option-btn incorrect";
        return "option-btn";
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