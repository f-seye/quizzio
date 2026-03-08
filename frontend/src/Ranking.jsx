import { BACKEND_URL } from './constants';
import { useState, useEffect } from 'react'
import './Ranking.css'

function Ranking() {

    
    const [users, setUsers] = useState([]);
    const [error, setError] = useState('');
    const [sortBy, setSortBy] = useState('points')

    const fetchFlashedMessages = async () => {
        try {
            const response = await fetch(`${BACKEND_URL}/api/flashed-messages`, {
                credentials: 'include',
            });
            if (!response.ok) {
                throw new Error('Failed to fetch flashed messages');
            }
            const data = await response.json();
            if (data.messages?.length) {
                setError(data.messages.join(' '));
            }
        } catch (err) {
            setError('Failed to fetch messages');
        }
    };

    useEffect(() => {
        fetch(`${BACKEND_URL}/api/ranking?sort_by=${sortBy}`, { credentials: 'include' })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => { throw new Error(err.message) })
                }
                return res.json()
            })
            .then(data => {
                setUsers(data);
                console.log(data);
                fetchFlashedMessages();
            })
            .catch(err => {
                console.log(err);
                setError(err.message);
                fetchFlashedMessages();
            });
    }, [sortBy]);


    const handleSortChange = (e) => {
        setSortBy(e.target.value);
    };

    return (
        <div className="ranking-container">
            <div className="sort-selector">
                <label htmlFor="sortBy">Trier par :</label>
                <select id="sortBy" value={sortBy} onChange={handleSortChange}>
                    <option value="points">points</option>
                    <option value="average">moyenne</option>
                </select>
            </div>
            <div className="top-players-container">
                {error && <div className="error-message">{error}</div>}
                <h2> Meilleurs joueurs </h2>
                {users.length === 0 && <p className="no-players">Aucun joueur trouvé.</p>}

                {users.length > 0 && users.slice(0, 3).map((u) =>
                    <span key={u.username} className="top-player-display">
                        <img src={`${BACKEND_URL}${u.profilePic}`} width="50" />
                        <p>{u.username}</p>
                        <p>{u.points}</p>
                    </span>
                )}
            </div>

            <div className="ranking-container">
                <div className="ranking-bar">
                    <p className="rank">#</p>
                    <p className="picture"></p>
                    <p className="user">username</p>
                    <p className="points">Points</p>
                    <p className="average">Moyenne</p>
                </div>
                {users.length > 0 && users.map((u, i) =>
                    <div key={u.username} className="player-display">
                        <p>{i + 1}</p>
                        <img src={`${BACKEND_URL}${u.profilePic}`} width="50" />
                        <p>{u.username}</p>
                        <p>{u.points}</p>
                        <p>{u.average}%</p>
                    </div>
                )}
            </div>

        </div>
    );
}

export default Ranking