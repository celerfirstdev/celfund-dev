import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/checkout" element={
            <div style={{ padding: '60px', textAlign: 'center', background: '#0B0E1A', minHeight: '100vh', color: 'white' }}>
              <h1>🎉 Stripe Checkout (Test Mode)</h1>
              <p style={{ marginTop: '20px', color: '#00FFD1' }}>This is a placeholder for Stripe integration</p>
              <button onClick={() => window.location.href = '/'} style={{ marginTop: '30px', padding: '12px 24px', background: '#00FFD1', color: '#0B0E1A', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>
                Back to Home
              </button>
            </div>
          } />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;