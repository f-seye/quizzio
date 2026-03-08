import { BACKEND_URL } from './constants';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'
import "./ThemePage.css"
import redHeart from './assets/redHeart.png'
import whiteHeart from './assets/whiteHeart.jpg'


function ThemePage() {

    const { themeName } = useParams()
    const [quizzes, setQuizzes] = useState([]);
    const [error, setError] = useState(null);
    

    const [levels, setLevels] = useState({ facile: [], intermediaire: [], difficile: [] })
    useEffect(() => {
        const res = {
            facile: quizzes.filter(quiz => quiz.difficulty === 1),
            intermediaire: quizzes.filter(quiz => quiz.difficulty === 2),
            difficile: quizzes.filter(quiz => quiz.difficulty === 3)
        };

        setLevels(res);

    }, [quizzes]);

    useEffect(() => {
        document.title = themeName ? `${themeName} quizzes` : "Theme non specifié"
        if (!themeName) {
            setError("Aucun thème spécifié. Veuillez sélectionner un thème.");
            setQuizzes([]);
            return;
        }

        fetch(`${BACKEND_URL}/api/quiz-by-theme?theme_name=${encodeURIComponent(themeName)}`, { credentials: 'include' })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => {
                        throw new Error(err.message)
                    })
                }
                return res.json();
            })
            .then(data => {
                setQuizzes(data);
                setError(null);

            })
            .catch(err => {
                console.log(err);
                setQuizzes([]);
                setError(err.message);
            });

    }, [themeName]);

    const handleQuizClick = (quiz) => {
        window.location.href = `/quiz/${quiz.id}`;
    };

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
        <div className="theme-container">
            <h1 className="theme-title">Thème : {themeName || ''}</h1>
            <div className="quizzes-by-theme-container">
                {error && <div className="error-message">{error}</div>}
                <div className="easy-quiz">
                    <label className="level-display">Niveau : Facile</label>
                    <div className="quiz-grid">
                        {levels.facile.length > 0 ? (
                            levels.facile.map((q) => (
                                <span
                                    key={q.id}
                                    className="quiz-display"
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => handleQuizClick(q)}
                                >
                                    <span>{q.name}</span>
                                    <img
                                        className="favorite-icon"
                                        src={q.is_favorite ? redHeart : whiteHeart}
                                        onClick={(e) => handleFavoriteToggle(q, e)}
                                        width="20"
                                        alt={q.is_favorite ? "Favori" : "Non favori"}
                                    />
                                </span>
                            ))
                        ) : (
                            <p className="no-quiz">Aucun quiz disponible</p>
                        )}
                    </div>
                </div>

                <div className="medium-quiz">
                    <label className="level-display">Niveau : Intermédiaire</label>
                    <div className="quiz-grid">
                        {levels.intermediaire.length > 0 ? (
                            levels.intermediaire.map((q) => (
                                <span
                                    key={q.id}
                                    className="quiz-display"
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => handleQuizClick(q)}
                                >
                                    <span>{q.name}</span>
                                    <img
                                        className="favorite-icon"
                                        src={q.is_favorite ? redHeart : whiteHeart}
                                        onClick={(e) => handleFavoriteToggle(q, e)}
                                        width="20"
                                        alt={q.is_favorite ? "Favori" : "Non favori"}
                                    />
                                </span>
                            ))
                        ) : (
                            <p className="no-quiz">Aucun quiz disponible</p>
                        )}
                    </div>
                </div>

                <div className="hard-quiz">
                    <label className="level-display">Niveau : Difficile</label>
                    <div className="quiz-grid">
                        {levels.difficile.length > 0 ? (
                            levels.difficile.map((q) => (
                                <span
                                    key={q.id}
                                    className="quiz-display"
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => handleQuizClick(q)}
                                >
                                    <span>{q.name}</span>
                                    <img
                                        className="favorite-icon"
                                        src={q.is_favorite ? redHeart : whiteHeart}
                                        onClick={(e) => handleFavoriteToggle(q, e)}
                                        width="20"
                                        alt={q.is_favorite ? "Favori" : "Non favori"}
                                    />
                                </span>
                            ))
                        ) : (
                            <p className="no-quiz">Aucun quiz disponible</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ThemePage