import { BACKEND_URL } from './constants';
import './Reset.css'
import { useState, useEffect } from 'react'

function ResetPassword() {

    const [email, setEmail] = useState('');
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

    async function handleConfirm() {
        setError('');
        setSuccess('');
        setFlashMessages([]);

        if (!email) {
            setError("Email is required");
            return;
        }

        const data = {
            email,
        };

        try {
            const res = await fetch(`${BACKEND_URL}/api/reset-password`, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                credentials: 'include',
            });

            const responseData = await res.json();

            if (!res.ok) {
                setError(responseData.message || "Une erreur est survenue lors de la demande de réinitialisation.");
                fetchFlashMessages();
                return;
            }

            setSuccess(responseData.message);
            setEmail('');
            fetchFlashMessages();
            // setTimeout(() => {
            //     window.location.href = '/sign-in';
            // }, 3000); 
        } catch (err) {
            setError(err.message || "Une erreur inconnue est survenue.");
            setSuccess('');
            fetchFlashMessages();
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
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
            <div className="container">
                <h3 className="title">
                    Vous avez demandé à réinitialiser votre mot de passe ?
                </h3>
                <input onChange={(e) => { setEmail(e.target.value) }} type="email" className="email-input" value={email} placeholder="Enter your email" />
                <button className="button" onClick={handleConfirm}>
                    Confirmez
                </button>
            </div>
        </>);
}

export default ResetPassword