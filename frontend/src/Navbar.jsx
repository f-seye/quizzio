import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';
import logo from './assets/logo.jpg';

/**
 * Barre de navigation principale.
 * Affiche un menu différent selon que l'utilisateur est connecté ou non.
 */
function Navbar() {
    const { isConnected, logout, loading } = useContext(AuthContext);
    const navigate = useNavigate();

    if (loading) return null;

    const handleLogout = () => {
        logout();
        navigate('/sign-in');
    };

    const accountMenu = isConnected ? (
        <ul className="dropdown-menu dropdown-menu-end">
            <li><button className="dropdown-item" onClick={() => navigate('/settings')}>Paramètres</button></li>
            <li><button className="dropdown-item" onClick={() => navigate('/my-quizzes')}>Mes quiz</button></li>
            <li><button className="dropdown-item" onClick={() => navigate('/my-scores')}>Mes scores</button></li>
            <li><button className="dropdown-item" onClick={() => navigate('/my-favorites')}>Mes favoris</button></li>
            <li><button className="dropdown-item" onClick={handleLogout}>Se déconnecter</button></li>
        </ul>
    ) : (
        <ul className="dropdown-menu dropdown-menu-end">
            <li><a className="dropdown-item" href="/sign-in">Se connecter</a></li>
            <li><a className="dropdown-item" href="/sign-up">Créer un compte</a></li>
        </ul>
    );

    return (
        <nav className="navbar navbar-expand-lg bg-body-tertiary">
            <div className="container-fluid">
                <a className="navbar-brand" href="/">
                    <img src={logo} alt="Quizzio" width={50} height={45} />
                </a>
                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarSupportedContent"
                    aria-controls="navbarSupportedContent"
                    aria-expanded="false"
                    aria-label="Ouvrir la navigation"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <a className="nav-link active" aria-current="page" href="/">Accueil</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="/all-quiz">Tous les quiz</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="/ranking">Classement</a>
                        </li>
                    </ul>
                    <ul className="navbar-nav ms-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <a
                                className="nav-link dropdown-toggle"
                                href="#"
                                role="button"
                                data-bs-toggle="dropdown"
                                aria-expanded="false"
                            >
                                Mon compte
                            </a>
                            {accountMenu}
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
