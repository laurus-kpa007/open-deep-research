'use client';

import { useState } from 'react';

export default function MinimalTestPage() {
  const [response, setResponse] = useState('');

  const testAPI = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/health');
      const data = await res.text();
      setResponse(data);
    } catch (error) {
      setResponse('Connection failed: ' + error.message);
    }
  };

  return (
    <html>
      <body style={{ fontFamily: 'Arial', padding: '20px' }}>
        <h1 style={{ color: 'red' }}>🚀 MINIMAL TEST PAGE</h1>
        
        <p>If you can see this red title, the frontend is working!</p>
        
        <button 
          onClick={testAPI}
          style={{
            padding: '10px 20px',
            backgroundColor: 'blue',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          Test Backend Connection
        </button>
        
        <div style={{ border: '1px solid #ccc', padding: '10px' }}>
          <strong>Backend Response:</strong>
          <pre>{response}</pre>
        </div>
        
        <hr />
        
        <h2>Instructions:</h2>
        <ol>
          <li>Can you see this red title?</li>
          <li>Click the blue button</li>
          <li>Tell me what happens</li>
        </ol>
      </body>
    </html>
  );
}