import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './MenuBar.css'; // <-- This import is the most critical line

function MenuBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="menu-bar"> {/* <-- This classname is critical */}
      <div className="menu-bar-content">
        <div className="menu-logo">
          <Link to="/">NoteWise AI 🧠</Link>
        </div>
        <ul className="menu-links">
          {user && (
            <>
              <li><Link to="/generate">Generate</Link></li>
              <li><Link to="/">Dashboard</Link></li>
            </>
          )}
        </ul>
        <div className="menu-auth">
          {user ? (
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </div>
      </div>
    </nav>
  );
}

export default MenuBar;