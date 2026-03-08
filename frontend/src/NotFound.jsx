import { BACKEND_URL } from './constants';
import loading from "./assets/loading-white.gif"
import { useEffect } from 'react';
import "./NotFound.css"

function NotFound(){
    
    useEffect(() => {
        fetch(`${BACKEND_URL}/api/flash-404`, { method: "POST", credentials: "include" })
            .then(() => {
                window.location.href = "/";
            });
    }, []);

    return(
    <>
        <div className="not-found-container">
            <h2>Page non trouvée</h2>
            <img src={loading}/>
        </div>
    </>);
}

export default NotFound