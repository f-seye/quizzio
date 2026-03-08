import { BACKEND_URL } from './constants';
import { useState, useEffect, useContext } from 'react'
import {AuthContext} from './AuthContext.jsx'
import './MyScores.css'
import redHeart from './assets/redHeart.png'
import whiteHeart from './assets/whiteHeart.jpg'


function MyScores() {
    const [quizzes, setQuizzes] = useState([]);
    const [categories, setCategories] = useState({});
    const [averageScore, setAverageScore] = useState(0);
    const [error, setError] = useState('');
    const {isConnected} = useContext(AuthContext);

    useEffect(() => {
        if (!isConnected) {
            window.location.href = '/';
        }
    }, [isConnected]);

    useEffect(() => {
        if (!quizzes || quizzes.length === 0) {
            setCategories({});
            setAverageScore(0);
            return;
        }

        const quizzesByCategories = {}
        let totalScore = 0;
        let scoreCount = 0;
        quizzes.forEach(q => {
            const category = q.category || "Autre"
            if (!quizzesByCategories[category]) {
                quizzesByCategories[category] = [];
            }

            quizzesByCategories[category].push(q);
            if (q.score != null && !isNaN(q.score)) {
                totalScore += q.score;
                scoreCount += 1;
            }
        })

        setCategories(quizzesByCategories);
        setAverageScore(scoreCount > 0 ? (totalScore / scoreCount) : 0);

    }, [quizzes]);

    const BACKEND_URL = 'http://localhost:5000'
    useEffect(() => {
        fetch(`${BACKEND_URL}/api/get_my_scores`, { credentials: 'include' })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => { throw new Error(err.message) })
                }
                return res.json();
            })
            .then(data => {
                setQuizzes(data);
            })
            .catch(err => {
                setError(err.message);
                console.log(err);
            })
    }, [])

    async function handleFavoriteToggle(quiz, e) {
        e.stopPropagation();
        try {
            const response = await fetch(`${BACKEND_URL}/api/toggle-favorite`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ quiz_id: quiz.id })
            });
            const data = await response.json();
            if (response.ok) {
                setQuizzes(quizzes.map(q =>
                    q.id === quiz.id ? { ...q, is_favorite: data.is_favorite } : q
                ));
            } else {
                setError(data.message);
            }
        } catch (err) {
            setError('Failed to toggle favorite');
        }
    }

    return (
        <div className="my-scores-container">
            {error && <div className="error-message">{error}</div>}
            <div className="average-display"> <h2>Moyenne : {averageScore}</h2></div>
            <div className="categories-display">
                {quizzes.length === 0 && (
                    <p className="no-scores">Aucun quiz pour le moment.</p>
                )}
                {Object.entries(categories).map(([categoryName, quizzes], i) => (
                    <div key={i} className="category-section">
                        <div className="category-title"><h3>{categoryName}</h3></div>
                        {quizzes.map((q, j) => (
                            <div key={j} className="score-quiz-display">
                                <div className="my-quiz-title">{q.name}</div>
                                <div className="my-quiz-score">{q.score}</div>
                                <img
                                    className="favorite-toggle"
                                    src={q.is_favorite ? redHeart : whiteHeart}
                                    onClick={(e) => handleFavoriteToggle(q, e)}
                                    width="20"
                                    alt={q.is_favorite ? "Favori" : "Non favori"}
                                />
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default MyScores