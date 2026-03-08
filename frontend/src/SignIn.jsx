import { useState, useEffect, useContext } from 'react';
import './SignForm.css';
import { AuthContext } from './AuthContext';
import { BACKEND_URL } from './constants';

/**
 * Page de connexion.
 * Redirige vers l'accueil si l'utilisateur est déjà connecté.
 * Propose un bouton de renvoi du lien d'activation si le compte n'est pas activé.
 */
function SignIn() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [flashMessages, setFlashMessages] = useState([]);
    const [showResendActivation, setShowResendActivation] = useState(false);
    const { login, isConnected } = useContext(AuthContext);

    useEffect(() => {
        if (isConnected) {
            window.location.href = '/';
        }
    }, [isConnected]);

    useEffect(() => {
        fetchFlashMessages();
    }, []);

    useEffect(() => {
        if (flashMessages.length > 0) {
            const timer = setTimeout(() => setFlashMessages([]), 5000);
            return () => clearTimeout(timer);
        }
    }, [flashMessages]);

    const fetchFlashMessages = async () => {
        try {
            const res = await fetch(`${BACKEND_URL}/api/flashed-messages`, { credentials: 'include' });
            const data = await res.json();
            if (data.messages?.length) setFlashMessages(data.messages);
        } catch (err) {
            console.error('Erreur lors de la récupération des messages :', err);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!username || !password) {
            setError('Tous les champs sont requis.');
            return;
        }

        fetch(`${BACKEND_URL}/api/sign-in`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include',
        })
            .then(res =>
                res.json().then(json => ({ status: res.status, ok: res.ok, data: json }))
            )
            .then(({ status, ok, data }) => {
                if (!ok) {
                    const msg = data?.message || 'Une erreur est survenue.';
                    if (status === 403 && data?.requires_activation) {
                        setShowResendActivation(true);
                    }
                    throw new Error(msg);
                }
                setSuccess(data.message);
                setError('');
                setUsername('');
                setPassword('');
                login();
                setTimeout(() => { window.location.href = '/'; }, 50);
            })
            .catch(err => {
                setError(err.message || 'Erreur inconnue.');
                setSuccess('');
            });
    };

    const handleResendActivation = () => {
        if (!username) {
            setError("Veuillez entrer votre nom d'utilisateur pour renvoyer le lien.");
            return;
        }
        fetch(`${BACKEND_URL}/api/resend-activation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username }),
            credentials: 'include',
        })
            .then(res => {
                if (!res.ok) return res.json().then(d => { throw new Error(d.message); });
                return res.json();
            })
            .then(data => {
                setSuccess(data.message);
                setError('');
                setShowResendActivation(false);
                fetchFlashMessages();
            })
            .catch(err => {
                setError(err.message);
                setSuccess('');
            });
    };

    return (
        <>
            {flashMessages.length > 0 && (
                <div className="alert alert-warning">
                    {flashMessages.map((msg, i) => <div key={i}>{msg}</div>)}
                </div>
            )}
            <div className="sign-form-container">
                <form onSubmit={handleSubmit} noValidate>
                    <h2>Connexion</h2>
                    {error && <div className="error-message">{error}</div>}
                    {success && <div className="success-message">{success}</div>}
                    <div className="form-group">
                        <label htmlFor="username">Nom d'utilisateur :</label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            placeholder="Entrez votre nom d'utilisateur"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Mot de passe :</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            placeholder="Entrez votre mot de passe"
                            required
                        />
                        <a className="reset-password" href="/reset-password">Mot de passe oublié ?</a>
                    </div>
                    <button type="submit">Se connecter</button>
                </form>
                {showResendActivation && (
                    <div className="resend-link-container">
                        <p>Votre compte n'est pas activé.</p>
                        <button type="button" onClick={handleResendActivation} className="resend-button">
                            Renvoyer le lien d'activation
                        </button>
                    </div>
                )}
            </div>
        </>
    );
}

export default SignIn;
