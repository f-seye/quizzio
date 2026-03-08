import { BACKEND_URL } from './constants';
import { useEffect, useState, useContext } from "react";
import { AuthContext } from "./AuthContext"
import plus from './assets/plus.jpg'
import './MyQuizzes.css'
import redHeart from './assets/redHeart.png'
import whiteHeart from './assets/whiteHeart.jpg'

function MyQuizzes() {

    
    const { isConnected } = useContext(AuthContext);
    const [quizzes, setQuizzes] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!isConnected) {
            window.location.href = '/';
        }
    }, [isConnected]);

    const fetchFlashedMessages = async () => {
        const response = await fetch(`${BACKEND_URL}/api/flashed-messages`, {
            credentials: 'include'
        });
        const data = await response.json();
        if (data.messages.length) {
            setError(data.messages.join(' '));
        }

    };

    useEffect(() => {
        fetch(`${BACKEND_URL}/api/get_my_quizzes`, { credentials: 'include' })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => { throw new Error(err.message) });
                }
                return res.json();
            })
            .then(data => {
                setQuizzes(data);
                setError('');
                fetchFlashedMessages();
            })
            .catch(err => {
                console.log(err)
                setError(err.message);
                fetchFlashedMessages();
            });
    }, [])


    function handleQuizClick(quiz) {
        window.location.href = `/quiz/${quiz.id}`;
    }

    function handleCreate() {
        window.location.href = '/create-quiz';
    }

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
        <div className="my-quizzes-container">
            <h2> My Quizzes </h2>
            {error && <div className="error-message">{error}</div>}
            {(quizzes.length === 0 ? (<p className="no-quizzes"> No quiz yet </p>) :
                    (<div className="quizzes-container">
                        {quizzes.map((q, i) =>
                            <div className="quiz-display" key={i} role="button" tabIndex={0} onClick={() => handleQuizClick(q)}>
                                <span>{q.name}</span>
                                <img
                                    className="favorite-icon"
                                    src={q.is_favorite ? redHeart : whiteHeart}
                                    onClick={(e) => handleFavoriteToggle(q, e)}
                                    width="20"
                                />
                            </div>
                        )}
                    </div>)
                )}

            <div className="create-quiz">
                <img className="create-img" src={plus} />
                <button className="create-button" onClick={handleCreate} disabled={!isConnected}>Créer</button>
            </div>
        </div>);


}

export default MyQuizzes