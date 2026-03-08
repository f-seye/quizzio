import { BACKEND_URL } from './constants';
import { useState, useEffect } from 'react'
import "./AllQuizPage.css"

function AllQuizPage() {

    const [themes, setThemes] = useState([]);
    const [error, setError] = useState(null);

    

    useEffect(() => {
        document.title = "All Quizzes"
        fetch(`${BACKEND_URL}/api/themes`)
            .then(res => {
                if (!res.ok) {
                    throw new Error("Aucun thème trouvé");
                }
                return res.json();
            })
            .then(data => {
                setThemes(data);
                setError(null);
            })
            .catch(err => {
                console.log(err);
                setThemes([]);
                setError(err.message);
            });

    }, []);

    function handleThemeClick(t){
        window.location.href=`/theme/${t.name}`;
    }

    return (
        <>
            <div className="all-quiz-container">
                <h2 className="title">Thèmes</h2>
                {error ? (
                    <div className="error-message">{error}</div>
                ) : themes.length === 0 ? (
                    <p className="no-themes">Aucun thème disponible</p>
                ) : (
                    <div className="themes-container">
                        {themes.map((t, index) => (
                            <div
                                className="theme-display"
                                key={index}
                                role="button"
                                tabIndex={0}
                                onClick={() => handleThemeClick(t)}
                            >
                                {t.name}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
}

export default AllQuizPage