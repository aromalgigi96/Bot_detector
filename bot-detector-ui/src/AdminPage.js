import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function AdminPage() {
  const [logs, setLogs] = useState([]);
  const navigate = useNavigate();

  // Fetch attacks, redirect if not admin or not logged in
  async function fetchLogs() {
    const token = localStorage.getItem('token');
    if (!token) {
      return navigate('/');
    }
    const res = await fetch('/api/attacks', {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.status === 401 || res.status === 403) {
      return navigate('/');
    }
    const data = await res.json();
    setLogs(data);
  }

  useEffect(() => {
    fetchLogs();
    const id = setInterval(fetchLogs, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Attack Dashboard</h2>
      <table>
        <thead>
          <tr>
            <th>Time</th><th>IP</th><th>User</th><th>URI</th><th>Result</th><th>Score</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((e, i) => (
            <tr key={i}>
              <td>{e.time}</td>
              <td>{e.ip}</td>
              <td>{e.username}</td>
              <td>{e.uri}</td>
              <td className={e.result === 'Attack' ? 'attack' : 'benign'}>
                {e.result}
              </td>
              <td>{e.score.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
