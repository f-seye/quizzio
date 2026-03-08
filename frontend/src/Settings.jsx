import { BACKEND_URL } from './constants';
import defaultPic from './assets/defaultPic.png'
import { useState, useEffect, useContext } from 'react'
import { AuthContext } from './AuthContext';
import './Settings.css'

function Settings() {
    const [username, setUsername] = useState('');
    const [profilePic, setProfilePic] = useState('');
    const [name, setName] = useState('');
    const [mail, setMail] = useState('');
    const [birthday, setBirthday] = useState('');
    const [password, setPassword] = useState('');

    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [editField, setEditField] = useState(null);
    const [newProfilePic, setNewProfilePic] = useState(null);
    const [modifiedFields, setModifiedFields] = useState({});
    const [originalValues, setOriginalValues] = useState({});

    const { isConnected } = useContext(AuthContext);

    

    useEffect(() => {
        if (!isConnected)
            window.location.href = '/';

    }, [isConnected])


    useEffect(() => {
        fetch(`${BACKEND_URL}/api/settings`, { credentials: 'include' })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => {
                        throw new Error(err.message);
                    });
                }
                return res.json();
            })
            .then(data => {
                setUsername(data.username);
                const profilePicUrl = data.profilePic && data.profilePic.startsWith('/')
                    ? `${BACKEND_URL}${data.profilePic}`
                    : defaultPic;
                setProfilePic(profilePicUrl);
                setName(data.name || '');
                setMail(data.mail || '');
                setBirthday(data.birthday || '');
                setOriginalValues({
                    name: data.name || '',
                    mail: data.mail || '',
                    birthday: data.birthday || '',
                    profilePic: profilePicUrl,
                    password: ''
                });
                setError(null);
                fetchFlashedMessages();
            })
            .catch(err => {
                console.error(err);
                setError(err.message);
            });
    }, []);

    useEffect(() => {
        const handleBeforeUnload = () => {
            if (newProfilePic && Object.keys(modifiedFields).includes('profilePic')) {
                console.log('Sending cleanup beacon for staged profile picture');
                navigator.sendBeacon(`${BACKEND_URL}/api/cancel-profile-pic`, new FormData());
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            if (newProfilePic && Object.keys(modifiedFields).includes('profilePic')) {
                fetch(`${BACKEND_URL}/api/cancel-profile-pic`, {
                    method: 'POST',
                    credentials: 'include'
                })
                    .then(res => res.json())
                    .then(data => {
                        console.log(data.message);
                    })
                    .catch(err => {
                        console.error('Erreur lors du nettoyage de la photo de profil:', err);
                    });
            }
        };
    }, [newProfilePic, modifiedFields]);

    function handleEdit(field) {
        setEditField(field);
        setError(null);
        setSuccess(null);
    }

    const handlePicChange = async (e) => {
        const file = e.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('profilePic', file);
            try {
                const response = await fetch(`${BACKEND_URL}/api/upload-profile-pic`, {
                    method: 'POST',
                    credentials: 'include',
                    body: formData,
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.message);

                setNewProfilePic(`${BACKEND_URL}${data.profilePic}`);
                setModifiedFields(prev => ({ ...prev, profilePic: data.profilePic }));
                setSuccess('Photo de profil prête à etre enregistrée');
                fetchFlashedMessages();
                setEditField(null);
            } catch (err) {
                setError(err.message);
            }
        }
    };

    const handleSubmit = async () => {
        const updatedData = { ...modifiedFields };

        if (updatedData.name && updatedData.name.length > 100) {
            setError('Nom trop long (max 100 caractères)');
            return;
        }

        if (updatedData.mail && !/^\S+@\S+\.\S+$/.test(updatedData.mail)) {
            setError('Email invalide');
            return;
        }

        if (updatedData.birthday && !/^\d{4}-\d{2}-\d{2}$/.test(updatedData.birthday)) {
            setError('Date de naissance invalide (format: YYYY-MM-DD)');
            return;
        }

        if (updatedData.password && updatedData.password.length < 8) {
            setError('Mot de passe trop court (minimum 8 caractères)');
            return;
        }


        if (Object.keys(updatedData).length === 0) {
            setError('Aucune modification détectée.');
            return;
        }

        try {
            const response = await fetch(`${BACKEND_URL}/api/settings`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(updatedData)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.message || 'Erreur lors de la sauvegarde');
            }

            const data = await response.json();
            setSuccess('Modifications enregistrées');
            setModifiedFields({});
            setPassword('');
            setNewProfilePic(null);

            setOriginalValues({
                name: data.name || '',
                mail: data.mail || '',
                birthday: data.birthday || '',
                profilePic: data.profilePic && data.profilePic.startsWith('/')
                    ? `${BACKEND_URL}${data.profilePic}`
                    : defaultPic,
                password: ''
            });

            setProfilePic(data.profilePic && data.profilePic.startsWith('/')
                ? `${BACKEND_URL}${data.profilePic}`
                : defaultPic);
            fetchFlashedMessages();

        } catch (err) {
            setError(err.message);
        }
    };


    const handleChange = (field, value) => {
        switch (field) {
            case 'name':
                setName(value);
                if (value !== originalValues.name) {
                    setModifiedFields(prev => ({ ...prev, [field]: value }));
                } else {
                    setModifiedFields(prev => {
                        const { [field]: _, ...rest } = prev;
                        return rest;
                    });
                }
                break;
            case 'mail':
                setMail(value);
                if (value !== originalValues.mail) {
                    setModifiedFields(prev => ({ ...prev, [field]: value }));
                } else {
                    setModifiedFields(prev => {
                        const { [field]: _, ...rest } = prev;
                        return rest;
                    });
                }
                break;
            case 'birthday':
                setBirthday(value);
                if (value !== originalValues.birthday) {
                    setModifiedFields(prev => ({ ...prev, [field]: value }));
                } else {
                    setModifiedFields(prev => {
                        const { [field]: _, ...rest } = prev;
                        return rest;
                    });
                }
                break;
            case 'password':
                setPassword(value);
                if (value) {
                    setModifiedFields(prev => ({ ...prev, [field]: value }));
                } else {
                    setModifiedFields(prev => {
                        const { [field]: _, ...rest } = prev;
                        return rest;
                    });
                }
                break;
            default:
                return;
        }
        setEditField(null);
        setSuccess('Modification prête à être enregistrée');
    };

    const handleCancel = (field) => {
        switch (field) {
            case 'name':
                setName(originalValues.name);
                break;
            case 'mail':
                setMail(originalValues.mail);
                break;
            case 'birthday':
                setBirthday(originalValues.birthday);
                break;
            case 'password':
                setPassword(originalValues.password);
                break;
            case 'profilePic':
                setNewProfilePic(null);
                fetch(`${BACKEND_URL}/api/cancel-profile-pic`, {
                    method: 'POST',
                    credentials: 'include'
                })
                    .then(res => res.json())
                    .then(data => {
                        console.log(data.message);
                    })
                    .catch(err => {
                        console.error('Erreur lors de l\'annulation de la photo de profil:', err);
                    });
                break;
            default:
                return;
        }
        setModifiedFields(prev => {
            const { [field]: _, ...rest } = prev;
            return rest;
        });
        setEditField(null);
    };

    const fetchFlashedMessages = async () => {
        const response = await fetch(`${BACKEND_URL}/api/flashed-messages`, {
            credentials: 'include'
        });
        const data = await response.json();
        if (data.messages.length) {
            setError(data.messages.join(' '));
        }

    };

    const imageSrc = newProfilePic || profilePic || defaultPic;

    return (
        <>
            <div className="settings-container">
                <h2 className="setting-title">Settings</h2>
                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}

                <div className="profile-section">
                    <img src={imageSrc} alt="Photo de profil" className="profile-pic" />
                    {editField === 'profilePic' ? (
                        <div className="edit-field">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handlePicChange}
                                className="file-input"
                            />
                            <button
                                className="cancel-button"
                                onClick={() => handleCancel('profilePic')}
                            >
                                Annuler
                            </button>
                        </div>
                    ) : (
                        <button className="edit-button" onClick={() => handleEdit('profilePic')}>
                            Modifier
                        </button>
                    )}
                    <h3 className="username">{username}</h3>
                </div>

                <div className="settings-form">
                    <div className="form-group">
                        <label htmlFor="name">Nom</label>
                        {editField === 'name' ? (
                            <div className="edit-field">
                                <input
                                    id="name"
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="input"
                                />
                                <button className="save-button" onClick={() => handleChange('name', name)} disabled={!name}>
                                    Enregistrer
                                </button>
                                <button
                                    className="cancel-button"
                                    onClick={() => handleCancel('name')}
                                >
                                    Annuler
                                </button>
                            </div>
                        ) : (
                            <div className="field-display">
                                <span>{name || 'Non défini'}</span>
                                <button
                                    className="edit-button"
                                    onClick={() => handleEdit('name')}
                                >
                                    Modifier
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="mail">E-mail</label>
                        {editField === 'mail' ? (
                            <div className="edit-field">
                                <input
                                    id="mail"
                                    type="email"
                                    value={mail}
                                    onChange={(e) => setMail(e.target.value)}
                                    className="input"
                                />
                                <button className="save-button" onClick={() => handleChange('mail', mail)} disabled={!mail}>
                                    Enregistrer
                                </button>
                                <button
                                    className="cancel-button"
                                    onClick={() => handleCancel('mail')}
                                >
                                    Annuler
                                </button>
                            </div>
                        ) : (
                            <div className="field-display">
                                <span>{mail || 'Non défini'}</span>
                                <button
                                    className="edit-button"
                                    onClick={() => handleEdit('mail')}
                                >
                                    Modifier
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="birthday">Date de naissance</label>
                        {editField === 'birthday' ? (
                            <div className="edit-field">
                                <input
                                    id="birthday"
                                    type="date"
                                    value={birthday}
                                    onChange={(e) => setBirthday(e.target.value)}
                                    className="input"
                                />
                                <button className="save-button" onClick={() => handleChange('birthday', birthday)} disabled={!birthday}>
                                    Enregistrer
                                </button>
                                <button
                                    className="cancel-button"
                                    onClick={() => handleCancel('birthday')}
                                >
                                    Annuler
                                </button>
                            </div>
                        ) : (
                            <div className="field-display">
                                <span>{birthday || 'Non défini'}</span>
                                <button
                                    className="edit-button"
                                    onClick={() => handleEdit('birthday')}
                                >
                                    Modifier
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Mot de passe</label>
                        {editField === 'password' ? (
                            <div className="edit-field">
                                <input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input"
                                />
                                <button className="save-button" onClick={() => handleChange('password', password)} disabled={!password}>
                                    Enregistrer
                                </button>
                                <button
                                    className="cancel-button"
                                    onClick={() => handleCancel('password')}
                                >
                                    Annuler
                                </button>
                            </div>
                        ) : (
                            <div className="field-display">
                                <span>********</span>
                                <button
                                    className="edit-button"
                                    onClick={() => handleEdit('password')}
                                >
                                    Modifier
                                </button>
                            </div>
                        )}
                    </div>
                </div>
                <button
                    className="submit-button"
                    onClick={handleSubmit}
                    disabled={Object.keys(modifiedFields).length === 0}
                >
                    Sauvegarder
                </button>
            </div>
        </>
    );
}

export default Settings;