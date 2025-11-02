import React, { useState } from 'react';
import { X, Zap, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { toast } from 'sonner';

const UpgradeModal = ({ isOpen, onClose, userEmail }) => {
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async () => {
    setLoading(true);
    
    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${BACKEND_URL}/api/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail || 'guest@celfund.com'
        })
      });
      
      const data = await response.json();
      
      if (data.success && data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = data.checkout_url;
      } else {
        console.error('Failed to create checkout session');
        setLoading(false);
      }
    } catch (error) {
      console.error('Checkout error:', error);
      setLoading(false);
    }
  };

  const features = [
    "20 additional matching grants",
    "Deadline tracking & reminders",
    "AI-powered proposal drafting",
    "Priority matching algorithm",
    "Export to PDF & Word",
    "Grant application templates"
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="upgrade-modal">
        <DialogHeader>
          <DialogTitle className="upgrade-title">
            <Zap className="upgrade-icon" size={32} />
            Unlock 20 More Grants
          </DialogTitle>
          <DialogDescription className="upgrade-description">
            Get instant access to more funding opportunities and premium features
          </DialogDescription>
        </DialogHeader>
        
        <div className="upgrade-content">
          <div className="pricing-box">
            <div className="price">
              <span className="price-amount">$39</span>
              <span className="price-period">/month</span>
            </div>
            <p className="price-subtitle">Cancel anytime, no questions asked</p>
          </div>
          
          <div className="features-list">
            {features.map((feature, index) => (
              <div key={index} className="feature-item">
                <CheckCircle size={20} className="feature-icon" />
                <span>{feature}</span>
              </div>
            ))}
          </div>
          
          <div className="modal-actions">
            <Button onClick={handleUpgrade} className="upgrade-btn" disabled={loading}>
              {loading ? 'Opening checkout...' : 'Upgrade Now'}
            </Button>
            <Button onClick={onClose} variant="ghost" className="continue-free-btn">
              Continue Free
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default UpgradeModal;