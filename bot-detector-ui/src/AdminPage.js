import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminPage.css';

export default function AdminPage() {
  const [logs, setLogs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLogs = async () => {
      const token = localStorage.getItem('token');
      if (!token) return navigate('/');
      const res = await fetch('/api/attacks', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.status === 401 || res.status === 403) return navigate('/');
      const data = await res.json();
      setLogs(data);
    };

    fetchLogs();
    const id = setInterval(fetchLogs, 5000);
    return () => clearInterval(id);
  }, [navigate]);

  return (
    <div className="admin-container">
      <h2 className="admin-title">🛡️ Bot Attack Dashboard</h2>
      <div className="admin-table-wrapper">
        <table className="admin-table">
          <thead>
            <tr>
              <th>🕒 Time</th>
              <th>🌐 IP Address</th>
              <th>👤 User</th>
              <th>🔗 URI</th>
              <th>🚨 Result</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((e, i) => (
              <tr key={i}>
                <td>{e.time}</td>
                <td>{e.ip}</td>
                <td>{e.username}</td>
                <td>{e.uri}</td>
                <td>
                  <span className={`badge ${e.result === 'Attack' ? 'attack' : 'benign'}`}>
                    {e.result}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
