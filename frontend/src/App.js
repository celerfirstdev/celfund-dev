import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import SuccessPage from './pages/SuccessPage';
import ScrapingDashboard from './components/ScrapingDashboard';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/success" element={<SuccessPage />} />
          <Route path="/admin/scraping" element={<ScrapingDashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;