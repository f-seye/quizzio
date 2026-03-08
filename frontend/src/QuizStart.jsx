import { BACKEND_URL } from './constants';
import { useState, useEffect, useContext } from 'react'
import { useParams } from 'react-router-dom'
import { AuthContext } from './AuthContext.jsx'
import './QuizStart.css';

function QuizStart() {
    const { quiz_id } = useParams();
    const { isConnected, username } = useContext(AuthContext);
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(-1);
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    const [userAnswers, setUserAnswers] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);
    const [results, setResults] = useState(null);

    const BACKEND_URL = 'http://localhost:5000'

    const handleStartQuiz = () => {
        if (questions.length > 0) {
            setCurrentQuestionIndex(0);
            setSelectedAnswers([]);
            setError('');
        }
    };

    const handleAnswerSelect = (answerId) => {
        const currentQuestion = questions[currentQuestionIndex];
        if (currentQuestion.nb_good_answers > 1) {
            if (selectedAnswers.includes(answerId)) {
                setSelectedAnswers(selectedAnswers.filter(id => id !== answerId));
            } else {
                setSelectedAnswers([...selectedAnswers, answerId]);
            }
        }

        else {
            setSelectedAnswers([answerId]);
        }
        setError('');
    };

    const handleNextQuestion = async () => {
        const currentQuestion = questions[currentQuestionIndex];
        if (selectedAnswers.length === 0) {
            setError('Veuillez sélectionner au moins une réponse');
            return;
        }

        setUserAnswers([
            ...userAnswers.filter(ans => ans.question_id !== currentQuestion.id),
            { question_id: currentQuestion.id, answer_choice_ids: selectedAnswers }
        ]);

        if (isConnected && username) {
            try {
                const response = await fetch(`${BACKEND_URL}/api/user-answers`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        user_id: username,
                        answer_choice_ids: selectedAnswers,
                    }),
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Erreur lors de la sauvegarde de la réponse');
                }
            } catch (err) {
                console.error('Erreur lors de la sauvegarde:', err);
                setError('Erreur lors de la sauvegarde de la réponse');
                return;
            }
        }

        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setSelectedAnswers([]);
        }

        else {
            let score = 0;
            questions.forEach(question => {
                const userAnswer = userAnswers.find(ans => ans.question_id === question.id) ||
                    { question_id: question.id, answer_choice_ids: selectedAnswers };
                const correctAnswers = question.answer_choice
                    .filter(ac => ac.is_answer)
                    .map(ac => ac.id);
                const isCorrect =
                    userAnswer.answer_choice_ids.length === correctAnswers.length &&
                    userAnswer.answer_choice_ids.every(id => correctAnswers.includes(id));
                if (isCorrect) score += 1;
            });
            setResults({ score, total: questions.length });
            if (isConnected && username) {
                fetch(`${BACKEND_URL}/api/quizzes/${quiz_id}/finish`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        user_id: username,
                        score: score,
                    }),
                }).catch(err => console.error('Erreur lors de la mise à jour du score:', err));
            }
        }
    };

    const handlePrevQuestion = () => {
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(currentQuestionIndex - 1);
            const prevAnswer = userAnswers.find(ans => ans.question_id === questions[currentQuestionIndex - 1].id);
            setSelectedAnswers(prevAnswer ? prevAnswer.answer_choice_ids : []);
            setError('');
        }
    };


    useEffect(() => {
        document.title = `Quiz ${quiz_id}`;
        fetch(`${BACKEND_URL}/api/quizzes/${quiz_id}/questions`)
            .then(res => {
                if (!res.ok) {
                    throw new Error('Pas de questions trouvées');
                }
                return res.json();

            })
            .then(data => {
                setQuestions(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setError('Erreur lors du chargement des questions');
                setLoading(false);
            });
    }, [quiz_id])

    if (loading) return <div className="loading">Chargement...</div>;
    if (error) return <div className="error-message">{error}</div>;
    if (questions.length === 0) return <div className="error-message">Aucune question disponible</div>;

    if (results) {
        return (
            <div className="quiz-start-container">
                <h2>Résultats du Quiz</h2>
                <p>Votre score : {results.score} / {results.total}</p>

                {questions.map((question, index) => {
                    const userAnswer = userAnswers.find(ans => ans.question_id === question.id) || { answer_choice_ids: [] };

                    return (
                        <div key={question.id} className="question-result">
                            <h3>Question {index + 1} : {question.label}</h3>
                            <ul>
                                {question.answer_choice.map(answer => {
                                    const isCorrect = answer.is_answer;
                                    const isSelected = userAnswer.answer_choice_ids.includes(answer.id);

                                    let className = "";
                                    if (isCorrect && isSelected) className = "answer-correct"; // vert
                                    else if (!isCorrect && isSelected) className = "answer-incorrect"; // rouge
                                    else if (isCorrect && !isSelected) className = "answer-missed"; // vert aussi

                                    return (
                                        <li key={answer.id} className={className}>
                                            {answer.label}
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    );
                })}

                <button
                    className="nav-button back"
                    onClick={() => window.location.href = '/'}
                >
                    Retour à l'accueil
                </button>
                <button
                    className="nav-button restart"
                    onClick={() => {
                        setCurrentQuestionIndex(-1);
                        window.location.href=`/quiz/${quiz_id}`
                    }}
                >
                    Recommencer
                </button>
            </div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];


    return (
        <div className="quiz-start-container">
            {currentQuestionIndex === -1 ? (
                <div>
                    <h2>Quiz {quiz_id}</h2>
                    {!isConnected &&
                        <p>Vous jouez en mode invité</p>
                    }
                    <button onClick={handleStartQuiz} className="start-button">
                        Commencer
                    </button>
                </div>
            ) : (
                <div className="question-container">
                    <h2>Question {currentQuestionIndex + 1}</h2>
                    <h3 className="question-label">{currentQuestion.label}</h3>
                    <div className="answers-container">
                        {currentQuestion.answer_choice.map((answer) => (
                            <div key={answer.id} className="answer-choice">
                                <input
                                    type={currentQuestion.nb_good_answers > 1 ? 'checkbox' : 'radio'}
                                    name={`question-${currentQuestion.id}`}
                                    value={answer.id}
                                    checked={selectedAnswers.includes(answer.id)}
                                    onChange={() => handleAnswerSelect(answer.id)}
                                />
                                <label>{answer.label}</label>
                            </div>
                        ))}
                    </div>
                    {error && <div className="error-message">{error}</div>}
                    <div className="navigation-buttons">
                        <button
                            onClick={handlePrevQuestion}
                            disabled={currentQuestionIndex === 0}
                            className="nav-button"
                        >
                            Précédent
                        </button>
                        <button
                            onClick={handleNextQuestion}
                            disabled={selectedAnswers.length === 0}
                            className="nav-button"
                        >
                            Suivant
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default QuizStart