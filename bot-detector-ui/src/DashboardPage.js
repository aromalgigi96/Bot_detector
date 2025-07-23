import React from 'react';
import { useNavigate } from 'react-router-dom';
import './DashboardPage.css';

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
    <div className="dashboard">
      <div className="balance-card">
        <p className="label">Current Balance</p>
        <h1 className="amount">
          {balance
            ? (isNaN(balance) ? balance : Number(balance).toLocaleString('en-US', { style: 'currency', currency: 'USD' }))
            : '$0.00'}
        </h1>
        <p className="card-info">{account ? account : '**** **** **** 1289'}</p>
        <p className="date">{new Date().toLocaleDateString('en-CA')}</p>
      </div>

      <div className="grid-section">
        <div className="card transactions">
          <h3>Transactions</h3>
          <ul>
            <li>☕ Starbucks New York LLP <span>$5.30</span></li>
            <li>🛒 Walmart Marketplace <span>$135</span></li>
            <li>💸 From Catherine Pierce <span>$250</span></li>
          </ul>
        </div>

        <div className="card transfer">
          <h3>Transfer</h3>
          <input type="text" placeholder={account ? account : "9876 8774 5443 0000 1289"} />
        </div>

        <div className="card conversion">
          <h3>Conversion</h3>
          <select>
            <option value="PLN">PLN</option>
            <option value="USD">USD</option>
          </select>
          <input type="number" defaultValue="5100" />
          <p className="rate">Rate = 5.01 (Jun 21, 13:59 UTC)</p>
        </div>
      </div>
      <div style={{ marginTop: "2rem", textAlign: "right", opacity: 0.7 }}>
        <strong>Welcome, {username}!</strong>
      </div>
    </div>
  );
}
