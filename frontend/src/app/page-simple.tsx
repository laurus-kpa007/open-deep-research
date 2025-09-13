'use client';

import { useState } from 'react';

export default function SimpleTestPage() {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testBackend = async () => {
    setLoading(true);
    try {
      // 1. Health check test
      const healthResponse = await fetch('http://localhost:8000/api/v1/health');
      const healthData = await healthResponse.json();
      console.log('Health check:', healthData);
      
      // 2. Research start test
      const researchResponse = await fetch('http://localhost:8000/api/v1/research/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'Test query',
          language: 'ko'
        })
      });
      
      const researchData = await researchResponse.json();
      console.log('Research response:', researchData);
      
      setResult(`
Health: ${JSON.stringify(healthData, null, 2)}

Research: ${JSON.stringify(researchData, null, 2)}
      `);
    } catch (error) {
      console.error('Error:', error);
      setResult(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: 'blue' }}>Deep Research Agent - Test Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={testBackend}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Testing...' : 'Test Backend Connection'}
        </button>
      </div>

      <div>
        <h2>CSS Test</h2>
        <div className="bg-blue-500 text-white p-4 rounded">
          Tailwind CSS Test - 이 박스가 파란색이면 CSS 작동
        </div>
      </div>

      {result && (
        <div>
          <h2>Backend Response:</h2>
          <pre style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '10px', 
            overflow: 'auto',
            fontSize: '12px'
          }}>
            {result}
          </pre>
        </div>
      )}
    </div>
  );
}