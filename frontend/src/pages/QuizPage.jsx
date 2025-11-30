import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiGetQuiz, apiSubmitQuiz, apiRegenerateQuiz } from '../api/apiClient';
import LoadingSpinner from '../components/LoadingSpinner';
import './QuizPage.css';

function QuizPage() {
    const { setId } = useParams();
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [userAnswers, setUserAnswers] = useState([]); 
    
    const [selectedOption, setSelectedOption] = useState(null);
    const [isAnswered, setIsAnswered] = useState(false);
    const [serverResult, setServerResult] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isRegenerating, setIsRegenerating] = useState(false);

    useEffect(() => {
        loadQuiz();
    }, [setId]);

    const loadQuiz = async () => {
        setIsLoading(true);
        try {
            const data = await apiGetQuiz(setId);
            setQuestions(data);
        } catch (err) {
            console.error("Failed to load quiz", err);
        }
        setIsLoading(false);
    };

    const handleRegenerate = async () => {
        if(!window.confirm("This will replace the current questions with new AI-generated ones. Continue?")) return;
        setIsRegenerating(true);
        try {
            await apiRegenerateQuiz(setId);
            // Reset state and reload
            setServerResult(null);
            setCurrentQuestionIndex(0);
            setUserAnswers([]);
            setIsAnswered(false);
            setSelectedOption(null);
            await loadQuiz();
        } catch (e) {
            alert("Failed to generate new quiz");
        }
        setIsRegenerating(false);
    };

    const handleAnswerSelect = (option) => {
        if (isAnswered) return;
        setSelectedOption(option);
        setIsAnswered(true);
        const currentQ = questions[currentQuestionIndex];
        setUserAnswers(prev => [...prev, { question_id: currentQ.id, selected: option }]);
    };

    const handleNextQuestion = async () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            setIsAnswered(false);
            setSelectedOption(null);
        } else {
            setIsLoading(true);
            try {
                const result = await apiSubmitQuiz(setId, userAnswers);
                setServerResult(result);
            } catch (err) {
                alert("Something went wrong submitting your quiz.");
            }
            setIsLoading(false);
        }
    };

    if (isLoading || isRegenerating) return <LoadingSpinner />;
    
    // Empty state with regenerate button
    if (questions.length === 0) return (
        <div className="quiz-container">
            <p>No quiz found for this set.</p>
            <button onClick={handleRegenerate} className="regen-btn" disabled={isRegenerating}>
                {isRegenerating ? "Generating..." : "Generate AI Quiz"}
            </button>
        </div>
    );

    if (serverResult) {
        const percentage = Math.round((serverResult.correct / serverResult.answered) * 100);
        return (
            <div className="quiz-container results">
                <h1>Quiz Complete!</h1>
                <div className="score-circle">{percentage}%</div>
                <h2>You got {serverResult.correct} out of {serverResult.answered} correct</h2>
                <div className="actions">
                    <Link to="/" className="action-link">Dashboard</Link>
                    <button onClick={() => window.location.reload()} className="retry-btn">Retake</button>
                    <button onClick={handleRegenerate} className="regen-btn secondary">Generate New Questions</button>
                </div>
            </div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];
    const getOptionClass = (option) => {
        if (!isAnswered) return "option-btn";
        if (option === currentQuestion.correct_answer) return "option-btn correct";
        if (option === selectedOption) return "option-btn incorrect";
        return "option-btn";
    };

    return (
        <div className="quiz-container">
            <div className="quiz-header">
                <h1>Knowledge Check</h1>
                {/* NEW REGENERATE BUTTON */}
                <button onClick={handleRegenerate} className="regen-icon-btn" title="Generate New Questions">↻ New Questions</button>
            </div>
            
            <div className="quiz-progress">Question {currentQuestionIndex + 1} of {questions.length}</div>
            <h3 className="question-text">{currentQuestion.question}</h3>
            
            <div className="options-grid">
                {currentQuestion.options.map((option, index) => (
                    <button key={index} className={getOptionClass(option)} onClick={() => handleAnswerSelect(option)} disabled={isAnswered}>
                        {option}
                    </button>
                ))}
            </div>

            {isAnswered && (
                <button onClick={handleNextQuestion} className="next-btn">
                    {currentQuestionIndex < questions.length - 1 ? "Next Question" : "Finish & Submit"}
                </button>
            )}
        </div>
    );
}

export default QuizPage;