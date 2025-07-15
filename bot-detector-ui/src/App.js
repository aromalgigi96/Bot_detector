import React, { useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { AuthContext } from './AuthContext';
import RegisterPage from './RegisterPage';
import LoginPage from './LoginPage';
import DashboardPage from './DashboardPage';
import BlockPage from './BlockPage';
import AdminPage from './AdminPage';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const username = localStorage.getItem('username');
  const isAdmin = username === 'admin';

  const handleLogout = () => {
    localStorage.clear();
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, setToken }}>
      <div className="App">
        <header>
          <h1>Mini Bank Demo</h1>
          <nav>
            {!token && (
              <>
                <Link to="/register">Register</Link> |{' '}
                <Link to="/">Login</Link>
              </>
            )}
            {token && !isAdmin && (
              <>
                <Link to="/dashboard">Dashboard</Link> |{' '}
                <button onClick={handleLogout}>Logout</button>
              </>
            )}
            {token && isAdmin && (
              <>
                <Link to="/dashboard">Dashboard</Link> |{' '}
                <Link to="/admin">Admin</Link> |{' '}
                <button onClick={handleLogout}>Logout</button>
              </>
            )}
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/" element={<LoginPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="*" element={<BlockPage />} />
          </Routes>
        </main>
      </div>
    </AuthContext.Provider>
  );
}

export default App;
