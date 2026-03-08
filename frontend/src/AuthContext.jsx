import { createContext, useState, useEffect } from 'react';
import { BACKEND_URL } from './constants';

export const AuthContext = createContext();

/* Fournit le contexte d'authentification : isConnected, username, login, logout, checkAuthStatus. */
export function AuthProvider({ children }) {
    const [isConnected, setIsConnected] = useState(false);
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState(null);

    const checkAuthStatus = () => {
        fetch(`${BACKEND_URL}/api/check-auth`, {
            method: 'GET',
            credentials: 'include',
        })
            .then(res => {
                if (!res.ok) throw new Error('Échec de la vérification de la session.');
                return res.json();
            })
            .then(data => {
                setIsConnected(data.authenticated || false);
                setUsername(data.authenticated ? data.username : null);
            })
            .catch(err => {
                console.error('Erreur lors de la vérification de la session :', err);
                setIsConnected(false);
                setUsername(null);
            })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const login = () => setIsConnected(true);

    const logout = () => {
        fetch(`${BACKEND_URL}/api/logout`, {
            method: 'POST',
            credentials: 'include',
        })
            .then(() => {
                setIsConnected(false);
                setUsername(null);
            })
            .catch(err => {
                console.error('Erreur lors de la déconnexion :', err);
                setIsConnected(false);
                setUsername(null);
            });
    };

    return (
        <AuthContext.Provider value={{ isConnected, username, login, logout, checkAuthStatus }}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
