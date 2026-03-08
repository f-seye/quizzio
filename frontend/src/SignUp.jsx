import { useEffect, useState, useContext } from 'react';
import './SignForm.css';
import { AuthContext } from './AuthContext';
import { BACKEND_URL } from './constants';

/**
 * Page d'inscription.
 * Redirige vers l'accueil si l'utilisateur est déjà connecté.
 */
function SignUp() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [mail, setMail] = useState('');
    const [confirmedPassword, setConfirmedPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const { isConnected } = useContext(AuthContext);

    useEffect(() => {
        if (isConnected) window.location.href = '/';
    }, [isConnected]);

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!username || !password || !mail || !confirmedPassword) {
            setError('Tous les champs sont requis.');
            return;
        }
        if (password !== confirmedPassword) {
            setError('Les mots de passe ne correspondent pas.');
            return;
        }

        fetch(`${BACKEND_URL}/api/sign-up`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, mail, password }),
            credentials: 'include',
        })
            .then(res => {
                if (!res.ok) return res.json().then(d => { throw new Error(d.message); });
                return res.json();
            })
            .then(data => {
                setSuccess(data.message);
                setError('');
                setUsername(''); setPassword(''); setMail(''); setConfirmedPassword('');
                setTimeout(() => { window.location.href = '/sign-in'; }, 1000);
            })
            .catch(err => {
                setError(err.message);
                setSuccess('');
            });
    };

    return (
        <div className="sign-form-container">
            <form onSubmit={handleSubmit} noValidate>
                <h2>Inscription</h2>
                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}
                <div className="form-group">
                    <label htmlFor="username">Nom d'utilisateur :</label>
                    <input id="username" type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Choisissez un nom d'utilisateur" required />
                </div>
                <div className="form-group">
                    <label htmlFor="mail">E-mail :</label>
                    <input id="mail" type="email" value={mail} onChange={e => setMail(e.target.value)} placeholder="Entrez votre e-mail" required />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Mot de passe :</label>
                    <input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Choisissez un mot de passe" required />
                </div>
                <div className="form-group">
                    <label htmlFor="confirmedPassword">Confirmer le mot de passe :</label>
                    <input id="confirmedPassword" type="password" value={confirmedPassword} onChange={e => setConfirmedPassword(e.target.value)} placeholder="Confirmez votre mot de passe" required />
                </div>
                <button type="submit">S'inscrire</button>
            </form>
        </div>
    );
}

export default SignUp;
