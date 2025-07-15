import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  if (!token) {
    navigate('/');
    return null;
  }

  const username = localStorage.getItem('username');
  const account = localStorage.getItem('account');
  const balance = localStorage.getItem('balance');

  return (
    <div>
      <h2>Welcome, {username}!</h2>
      <p><strong>Account:</strong> {account}</p>
      <p><strong>Balance:</strong> {balance}</p>
    </div>
  );
}
