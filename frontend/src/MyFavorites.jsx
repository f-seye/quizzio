import { BACKEND_URL } from './constants';
import { useEffect, useState, useContext } from "react";
import { AuthContext } from "./AuthContext"
import redHeart from './assets/redHeart.png'
import whiteHeart from './assets/whiteHeart.jpg'
import './MyFavorites.css'

function MyFavorites(){

    const {isConnected} = useContext(AuthContext);
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
        if (data.messages?.length) {
            setError(data.messages.join(' '));
        }
        
    };

    useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/get_my_favorites`, {
          credentials: "include",
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.message);
        }
        const data = await res.json();
        setQuizzes(data);
        setError("");
        await fetchFlashedMessages();
      } catch (err) {
        console.error(err);
        setError(err.message);
      }
    };
    fetchQuizzes();
  }, []);

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

    function handleQuizClick(quiz) {
        window.location.href = `/quiz/${quiz.id}`;
    }

    return (
        <div className="fav-quizzes-container">
            <h2> Favorites </h2>
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
        </div>);


}

export default MyFavorites