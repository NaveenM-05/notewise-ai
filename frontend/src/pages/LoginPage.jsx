import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login_FAKE } from '../api/mockApi';
import './LoginPage.css';

function LoginPage() {
  const [email, setEmail] = useState('user@test.com');
  const [password, setPassword] = useState('password');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const userData = await login_FAKE(email, password);
      login(userData.user);
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
    setIsLoading(false);
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h2>Welcome to NoteWise AI</h2>
        <p>Login to continue to your dashboard.</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          {error && <p className="error-message">{error}</p>}
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
         <p className="demo-creds">Use <strong>user@test.com</strong> and <strong>password</strong> to login.</p>
      </div>
    </div>
  );
}

export default LoginPage;
