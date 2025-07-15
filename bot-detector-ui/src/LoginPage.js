import React, { useState, useRef, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

export default function LoginPage() {
  const { setToken } = useContext(AuthContext);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const startRef = useRef(Date.now());
  const navigate = useNavigate();

  const handleSubmit = async e => {
    e.preventDefault();
    setError(null);

    // Measure user typing delay
    const time_to_submit = (Date.now() - startRef.current) / 1000;
    const body = {
      username,
      password,
      uri: '/login',
      client_ip: '203.0.113.5',
      timestamp: Math.floor(Date.now() / 1000),
      time_to_submit
    };

    let res;
    try {
      res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
    } catch {
      setError('Network error — please try again.');
      return;
    }

    const text = await res.text();
    let data;
    try { data = JSON.parse(text); }
    catch { data = { detail: text }; }

    // Bot detected → alert, stay on page
    if (res.status === 403) {
      window.alert(data.detail || 'Bot detected! Access denied.');
      return;
    }
    // Other errors
    if (!res.ok) {
      setError(data.detail || 'Login failed.');
      return;
    }

    // Success: store JWT and account info
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);

    localStorage.setItem('username', username);
    localStorage.setItem('account', data.account);
    localStorage.setItem('balance', data.balance);

    navigate('/dashboard');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      <label>
        Username:
        <input
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
      </label>
      <label>
        Password:
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
      </label>
      <button type="submit">Log In</button>
      {error && <p className="attack">{error}</p>}
    </form>
  );
}
