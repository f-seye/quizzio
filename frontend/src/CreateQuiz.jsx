import { BACKEND_URL } from './constants';
import { useState, useEffect, useContext } from 'react'
import { AuthContext } from './AuthContext.jsx'
import plus from './assets/plus.jpg'
import './CreateQuiz.css'

function CreateQuiz() {

    const { isConnected, username } = useContext(AuthContext);
    const [title, setTitle] = useState('');
    const [categoryName, setCategoryName] = useState('');
    const [newCategory, setNewCategory] = useState('');
    const [themeName, setThemeName] = useState('');
    const [newTheme, setNewTheme] = useState('');
    const [categories, setCategories] = useState([]);
    const [allThemes, setAllThemes] = useState([]);
    const [questions, setQuestions] = useState([]);
    const [difficulty, setDifficulty] = useState(1);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);

    const BACKEND_URL = "http://localhost:5000"

    useEffect(() => {
        if (!isConnected) {
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
            return;
        }

        Promise.all([
            fetch(`${BACKEND_URL}/api/categories`).then(res => {
                if (!res.ok) {
                    if (res.status === 404) throw new Error('Aucune catégorie trouvée');
                    throw new Error('Erreur lors du chargement des catégories');
                }
                return res.json();
            }),
            fetch(`${BACKEND_URL}/api/themes`).then(res => {
                if (!res.ok) {
                    if (res.status === 404) throw new Error('Aucun thème trouvé');
                    throw new Error('Erreur lors du chargement des thèmes');
                }
                return res.json();
            })
        ])

            .then(([categoriesData, themesData]) => {
                const categories = categoriesData.map(cat => ({
                    id: cat.id,
                    name: cat.name,
                    themes: cat.themes
                }));
                setCategories(categories);
                setAllThemes(themesData);
                setLoading(false);
            })
            .catch(err => {
                console.error('Erreur:', err);
                setError(err.message);
                setLoading(false);
            });
    }, [isConnected]);

    // Filtrer les thèmes par categoryName
    const themes = allThemes.filter(theme => {
        const category = categories.find(cat => cat.name === categoryName);
        return category && theme.category_id === category.id;
    });

    // Réinitialiser themeName quand categoryName change
    useEffect(() => {
        setThemeName('');
    }, [categoryName]);

    const handleCreateCategory = async () => {
        if (!newCategory.trim()) {
            setError('Le nom de la catégorie est requis');
            return;
        }

        try {
            const response = await fetch(`${BACKEND_URL}/api/categories`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ name: newCategory }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erreur lors de la création de la catégorie');
            }

            const data = await response.json();
            setCategories([...categories, { id: data.category_id, name: newCategory, themes: [] }]);
            setCategoryName(newCategory);
            setNewCategory('');
            setError('');
        } catch (err) {
            console.error('Erreur:', err);
            setError(err.message);
        }
    };

    const handleCreateTheme = async () => {
        if (!newTheme.trim()) {
            setError('Le nom du thème est requis');
            return;
        }
        if (!categoryName) {
            setError('Veuillez sélectionner une catégorie d’abord');
            return;
        }

        const category = categories.find(cat => cat.name === categoryName);
        if (!category) {
            setError('Catégorie non trouvée');
            return;
        }

        try {
            const response = await fetch(`${BACKEND_URL}/api/themes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ name: newTheme, category_id: category.id }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erreur lors de la création du thème');
            }

            const data = await response.json();
            setAllThemes([...allThemes, { id: data.theme_id, name: newTheme, category_id: category.id }]);
            setThemeName(newTheme);
            setNewTheme('');
            setError('');
        } catch (err) {
            console.error('Erreur:', err);
            setError(err.message);
        }
    };

    const handleAddQuestion = () => {
        setQuestions([
            ...questions,
            {
                label: '',
                answer_choices: [{ label: '', is_answer: false }, { label: '', is_answer: false }],
            },
        ]);
    };

    const handleQuestionChange = (index, field, value) => {
        const updatedQuestions = [...questions];
        updatedQuestions[index][field] = value;
        setQuestions(updatedQuestions);
    };

    const handleAnswerChoiceChange = (questionIndex, choiceIndex, field, value) => {
        const updatedQuestions = [...questions];
        updatedQuestions[questionIndex].answer_choices[choiceIndex][field] = value;
        setQuestions(updatedQuestions);

        const invalidQuestion = updatedQuestions.find(
            q =>
                q.answer_choices.some(ac => !ac.label.trim()) ||
                !q.answer_choices.some(ac => ac.is_answer)
        );
        if (invalidQuestion) {
            setError('Tous les choix de réponse doivent avoir un libellé non vide et chaque question doit avoir au moins une bonne réponse');
        } else {
            setError('');
        }
    };

    const handleAddAnswerChoice = (questionIndex) => {
        const updatedQuestions = [...questions];
            updatedQuestions[questionIndex].answer_choices.push({ label: '', is_answer: false });
            setQuestions(updatedQuestions);
    };

    const handleRemoveAnswerChoice = (questionIndex, choiceIndex) => {
        const updatedQuestions = [...questions];
            updatedQuestions[questionIndex].answer_choices.splice(choiceIndex, 1);
            setQuestions(updatedQuestions);
    };

    const handleRemoveQuestion = (questionIndex) => {
        const updatedQuestions = questions.filter((_, i) => i !== questionIndex);
        setQuestions(updatedQuestions);
        const invalidQuestion = updatedQuestions.find(
            q =>
                q.answer_choices.some(ac => !ac.label.trim()) ||
                !q.answer_choices.some(ac => ac.is_answer)
        );
        if (!invalidQuestion) {
            setError('');
        }
    };

    const handleSaveQuiz = async () => {
        if (!title.trim()) {
            setError('Le titre du quiz est requis');
            return;
        }
        if (!categoryName) {
            setError('Veuillez sélectionner ou créer une catégorie');
            return;
        }
        if (!themeName) {
            setError('Veuillez sélectionner ou créer un thème');
            return;
        }

        const validQuestions = questions.filter(
            q =>
                q.label.trim() &&
                q.answer_choices.length >= 2 &&
                q.answer_choices.every(ac => ac.label.trim()) &&
                q.answer_choices.some(ac => ac.is_answer)
        );

        if (validQuestions.length === 0) {
            setError('Au moins une question valide est requise (tous les choix doivent avoir un libellé non vide et au moins une bonne réponse)');
            return;
        }

        try {
            const response = await fetch(`${BACKEND_URL}/api/createQuiz`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    title,
                    category_name: categoryName,
                    theme_name: themeName,
                    questions: validQuestions,
                    nb_questions: validQuestions.length,
                    difficulty: difficulty,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erreur lors de la création du quiz');
            }

            setError('');
            window.location.href = '/my-quizzes';
        } catch (err) {
            console.error('Erreur lors de la création du quiz:', err);
            setError(err.message);
        }
    };




    if (loading) return <div className="loading">Chargement...</div>;

    return (
        <div className="create-quiz-container">
            <h2>Créer un nouveau quiz</h2>
            {!isConnected && (
                <p className="error-message">Vous devez être connecté pour créer un quiz.</p>
            )}
            <div className="quiz-title">
                <label>Titre du quiz :</label>
                <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Entrez le titre du quiz"
                    disabled={!isConnected}
                />
            </div>
            <div className="quiz-title">
                <label>Niveau de difficulté :</label>
                <input
                    type="number"
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    placeholder="Indiquez le niveau de difficulté"
                    disabled={!isConnected}
                    max="3"
                    min="1"
                />
            </div>
            <div className="quiz-category">
                <label>Catégorie :</label>
                <select
                    value={categoryName}
                    onChange={(e) => setCategoryName(e.target.value)}
                    disabled={!isConnected}
                >
                    <option value="">Sélectionner une catégorie</option>
                    {categories.map(category => (
                        <option key={category.id} value={category.name}>
                            {category.name}
                        </option>
                    ))}
                </select>
                {categories.length === 0 && (
                    <p className="info-message">Aucune catégorie disponible, créez-en une.</p>
                )}
                <div className="new-category">
                    <input
                        type="text"
                        value={newCategory}
                        onChange={(e) => setNewCategory(e.target.value)}
                        placeholder="Créer une nouvelle catégorie"
                        disabled={!isConnected}
                    />
                    <button
                        onClick={handleCreateCategory}
                        disabled={!isConnected || !newCategory.trim()}
                    >
                        Ajouter la catégorie
                    </button>
                </div>
            </div>
            <div className="quiz-theme">
                <label>Thème :</label>
                <select
                    value={themeName}
                    onChange={(e) => setThemeName(e.target.value)}
                    disabled={!isConnected || !categoryName}
                >
                    <option value="">Sélectionner un thème</option>
                    {themes.map(theme => (
                        <option key={theme.id} value={theme.name}>
                            {theme.name}
                        </option>
                    ))}
                </select>
                {categoryName && themes.length === 0 && (
                    <p className="info-message">Aucun thème disponible pour cette catégorie, créez-en un.</p>
                )}
                <div className="new-theme">
                    <input
                        type="text"
                        value={newTheme}
                        onChange={(e) => setNewTheme(e.target.value)}
                        placeholder="Créer un nouveau thème"
                        disabled={!isConnected || !categoryName}
                    />
                    <button
                        onClick={handleCreateTheme}
                        disabled={!isConnected || !categoryName || !newTheme.trim()}
                    >
                        Ajouter le thème
                    </button>
                </div>
            </div>
            {questions.map((question, qIndex) => (
                <div key={qIndex} className="question-container">
                    <h3>Question {qIndex + 1}</h3>
                    <button
                        className="remove-question"
                        onClick={() => handleRemoveQuestion(qIndex)}
                        disabled={!isConnected}
                    >
                        Supprimer la question
                    </button>
                    <div className="question-field">
                        <label>Libellé :</label>
                        <input
                            type="text"
                            value={question.label}
                            onChange={(e) => handleQuestionChange(qIndex, 'label', e.target.value)}
                            placeholder="Entrez le libellé de la question"
                            disabled={!isConnected}
                        />
                    </div>
                    <div className="answer-choices">
                        {question.answer_choices.map((choice, cIndex) => (
                            <div key={cIndex} className="answer-choice">
                                <input
                                    type="text"
                                    value={choice.label}
                                    onChange={(e) =>
                                        handleAnswerChoiceChange(qIndex, cIndex, 'label', e.target.value)
                                    }
                                    placeholder={`Choix ${cIndex + 1}`}
                                    disabled={!isConnected}
                                />
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={choice.is_answer}
                                        onChange={(e) =>
                                            handleAnswerChoiceChange(qIndex, cIndex, 'is_answer', e.target.checked)
                                        }
                                        disabled={!isConnected}
                                    />
                                    Bonne réponse
                                </label>
                                <button
                                    className="remove-choice"
                                    onClick={() => handleRemoveAnswerChoice(qIndex, cIndex)}
                                    disabled={!isConnected}
                                >
                                    Supprimer
                                </button>
                            </div>
                        ))}
                        <button
                            className="add-choice"
                            onClick={() => handleAddAnswerChoice(qIndex)}
                            disabled={!isConnected}
                        >
                            Ajouter un choix
                        </button>
                    </div>
                </div>
            ))}
            <div className="add-question">
                <img className="add-img" src={plus} onClick={handleAddQuestion} alt="Ajouter une question" width="50"/>
                <span>Ajouter une question</span>
                
            </div>
            <button
                className="save-button"
                onClick={handleSaveQuiz}
                disabled={!isConnected || !title.trim() || !categoryName || !themeName || questions.length === 0}
            >
                Enregistrer le quiz
            </button>
            {error && <div className="error-message">{error}</div>}
        </div>
    );
}

export default CreateQuiz