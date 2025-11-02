import React from 'react';
import { CheckCircle, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate, useSearchParams } from 'react-router-dom';

const SuccessPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  return (
    <div className="success-page">
      <div className="success-container">
        <div className="success-icon-wrapper">
          <CheckCircle className="success-icon" size={80} />
        </div>
        
        <h1 className="success-title">
          🎉 You're in!
        </h1>
        
        <p className="success-message">
          We'll contact you within 24 hours to activate your CelFund workspace.
        </p>
        
        <div className="success-details">
          <p className="success-detail-item">
            ✓ Access to 20 additional grant matches
          </p>
          <p className="success-detail-item">
            ✓ Deadline tracking & reminders
          </p>
          <p className="success-detail-item">
            ✓ AI-powered proposal drafting
          </p>
          <p className="success-detail-item">
            ✓ Priority support
          </p>
        </div>
        
        {sessionId && (
          <p className="session-info">
            Session ID: {sessionId.substring(0, 20)}...
          </p>
        )}
        
        <Button onClick={() => navigate('/')} className="return-home-btn">
          <ArrowLeft size={20} />
          Return Home
        </Button>
      </div>
    </div>
  );
};

export default SuccessPage;
