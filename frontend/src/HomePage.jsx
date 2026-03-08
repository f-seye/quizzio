import { BACKEND_URL } from './constants';

import CategoryAccordion from './CategoryAccordion.jsx';
import { useEffect, useState } from 'react'
import './HomePage.css'
import redHeart from './assets/redHeart.png'
import whiteHeart from './assets/whiteHeart.jpg'

function HomePage() {
    const [quizzes, setQuizzes] = useState([]);
    const [categories, setCategories] = useState([]);
    const [flashMessages, setFlashMessages] = useState([]);
    const [error, setError] = useState('');
    

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


    useEffect(() => {
        document.title = "Home";
    
        fetch(`${BACKEND_URL}/api/flashed-messages`, {credentials: 'include'})

            .then(res => res.json())
            .then(data => {
                if (data.messages && data.messages.length > 0) {
                    setFlashMessages(data.messages);
                }
            })
            .catch(err => console.log(err));

        
        fetch(`${BACKEND_URL}/api/homeQuiz`, { credentials: 'include' })
            .then(res => {
                if (!res.ok) {
                    throw new Error("Pas de quiz trouvé");
                }
                return res.json();
            })
            .then(data => {
                setQuizzes(data);
            })
            .catch(err => {
                console.error(err);
                setQuizzes([]);
            });

        fetch(`${BACKEND_URL}/api/categories`)
            .then(res => {
                if (!res.ok) {
                    throw new Error("Pas de categorie trouvée");
                }
                return res.json();
            })
            .then(data => {
                setCategories(data);
            })
            .catch(err => {
                console.log(err);
                setCategories([]);
            });
    }, []);


    useEffect(() => {
        if (flashMessages.length > 0) {
            const timer = setTimeout(() => {
                setFlashMessages([]);
            }, 2000);
            return () => clearTimeout(timer);
        }
    }, [flashMessages]);

    return (
        <>
            <div className="home-container">
                {flashMessages.length > 0 && (
                    <div className="flash-alert">
                        {flashMessages.map((msg, i) => (
                            <div key={i}>{msg}</div>
                        ))}
                    </div>
                )}
                {error && <div className="error-message">{error}</div> }
                <h4 className="quiz-title"> Challenge yourself now</h4>
                <div className="quizzes-container">
                    {quizzes.map((q) =>
                        <span className="quiz-display" key={q.id} role="button" tabIndex={0} onClick={() => window.location.href = `/quiz/${q.id}`}> 
                                                                    <span>{q.name}</span>
                                                                    <img
                                                                        className="favorite-icon"
                                                                        src={q.is_favorite ? redHeart : whiteHeart}
                                                                        onClick={(e) => handleFavoriteToggle(q, e)}
                                                                        width="20"
                                                                        alt={q.is_favorite ? "Favori" : "Non favori"}
                                                                    /> 
                                                                    </span>
                    )}
                </div>
                <div className="categories-container">
                    <div className="categogy-display">
                        {categories.map((c, i) =>
                            <CategoryAccordion key={i} index={i} title={c.name}
                                content={c.themes} />
                        )}
                    </div>
                </div>

            </div>
        </>);
}

export default HomePage;