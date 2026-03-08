import { BACKEND_URL } from './constants';
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Reset.css"



function SetNewPassword() {
    const { token } = useParams();
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [flashMessages, setFlashMessages] = useState([]);
    

    const fetchFlashMessages = async () => {
        try {
            const res = await fetch(`${BACKEND_URL}/api/flashed-messages`, { credentials: 'include' });
            const data = await res.json();
            if (data.messages && data.messages.length > 0) {
                setFlashMessages(data.messages);
            }
        } catch (err) {
            console.error("Error fetching flash messages:", err);
        }
    };

    useEffect(() => {
        fetchFlashMessages();
    }, []);

    useEffect(() => {
        if (flashMessages.length > 0) {
            const timer = setTimeout(() => {
                setFlashMessages([]);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [flashMessages]);

    async function handleSubmit(e) {
        e.preventDefault();
        setError('');
        setSuccess('');
        setFlashMessages([]);

        if (!newPassword || !confirmPassword) {
            setError('Tous les champs sont requis.');
            return;
        }
        if (newPassword !== confirmPassword) {
            setError('Les mots de passe ne correspondent pas.');
            return;
        }
        if (newPassword.length < 6) {
            setError('Le nouveau mot de passe doit contenir au moins 6 caractères.');
            return;
        }
        try {
            const res = await fetch(`${BACKEND_URL}/api/reset-password/${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_password: newPassword }),
                credentials: 'include',
            });

            const data = await res.json();

            if (!res.ok) {
                setError(data.message || 'Échec de la réinitialisation du mot de passe.');
                if (data.message && (data.message.includes("expiré") || data.message.includes("invalide"))) {
                    setTimeout(() => {
                        window.location.href = '/reset-password';
                    }, 3000);
                }
                return;
            }
            setSuccess(data.message);
            setNewPassword('');
            setConfirmPassword('');
            setTimeout(() => {
                window.location.href = '/sign-in'
            }, 2000);

        } catch (err) {
            setError(err.message || 'Une erreur inconnue est survenue.');
            setSuccess('');
        }
    }


    return (
        <>
            {flashMessages.length > 0 && (
                <div className="alert alert-warning">
                    {flashMessages.map((msg, i) => (
                        <div key={i}>{msg}</div>
                    ))}
                </div>
            )}
            <div className="reset-password-container">
                <h2>Réinitialiser votre mot de passe</h2>
                <form onSubmit={handleSubmit} noValidate>
                    {error && <div className="error-message">{error}</div>}
                    {success && <div className="success-message">{success}</div>}
                    <div className="form-group">
                        <label htmlFor="newPassword">Nouveau mot de passe :</label>
                        <input
                            type="password"
                            id="newPassword"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            placeholder="Entrez votre nouveau mot de passe"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirmez le nouveau mot de passe :</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirmez votre nouveau mot de passe"
                            required
                        />
                    </div>
                    <button type="submit" className="button">
                        Réinitialiser le mot de passe
                    </button>
                </form>
            </div>
        </>
    );
}

export default SetNewPassword