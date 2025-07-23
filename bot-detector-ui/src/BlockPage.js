import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function BlockPage() {
  const navigate = useNavigate();
  return (
    <div style={{ padding: '2rem' }}>
      <h2 className="attack">❌ Bot detected! Access denied.</h2>
      <p>If you believe this is an error, please contact support.</p>
      <button onClick={() => navigate('/')}>Return to Login</button>
    </div>
  );
}
