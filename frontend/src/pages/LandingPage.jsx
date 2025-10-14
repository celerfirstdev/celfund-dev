import React, { useState, useRef, useEffect } from 'react';
import { ArrowDown, Search } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import GrantCard from '../components/GrantCard';
import UpgradeModal from '../components/UpgradeModal';
import TypingBadge from '../components/TypingBadge';
import { mockGrants } from '../mock-grants';
import { Toaster } from '../components/ui/sonner';

const LandingPage = () => {
  const [formData, setFormData] = useState({
    projectSummary: '',
    organizationType: '',
    focusArea: '',
    email: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [interactionCount, setInteractionCount] = useState(0);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [isFormValid, setIsFormValid] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [cardsVisible, setCardsVisible] = useState(false);
  
  const formRef = useRef(null);
  const resultsRef = useRef(null);

  // Form validation
  useEffect(() => {
    const isValid = 
      formData.projectSummary.trim().length > 10 &&
      formData.organizationType !== '' &&
      formData.focusArea !== '' &&
      formData.email.includes('@');
    setIsFormValid(isValid);
  }, [formData]);

  const scrollToForm = () => {
    formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const handleInteraction = () => {
    const newCount = interactionCount + 1;
    setInteractionCount(newCount);
    if (newCount >= 2 && !showUpgradeModal) {
      setShowUpgradeModal(true);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid) return;
    
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsLoading(false);
    setShowResults(true);
    
    // Trigger card animations
    setTimeout(() => {
      setCardsVisible(true);
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
  };

  const getFocusAreaLabel = () => {
    const focusAreas = {
      'climate': 'Climate & Environment',
      'education': 'Education',
      'health': 'Health & Wellness',
      'technology': 'Technology & Innovation',
      'community': 'Community Development',
      'arts': 'Arts & Culture',
      'other': 'Various'
    };
    return focusAreas[formData.focusArea] || 'your';
  };

  return (
    <div className="landing-page">
      <Toaster />
      
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <TypingBadge />
          
          <h1 className="hero-title">
            Find and win grants <span className="highlight">10× faster.</span><br />
            No consultants. No spreadsheets.
          </h1>
          
          <p className="hero-subtitle">
            Paste your project summary to see matching active grants instantly.
          </p>
          
          <Button onClick={scrollToForm} className="hero-cta hero-cta-enhanced">
            Get 10 Grants Free
            <ArrowDown size={20} className="ml-2 animate-bounce" />
          </Button>
        </div>
        
        <div className="hero-gradient hero-gradient-animated"></div>
      </section>

      {/* Form Section */}
      <section className="form-section" ref={formRef}>
        <div className="container">
          <div className="form-header">
            <h2 className="form-title">Describe Your Project</h2>
            <p className="form-subtitle">Tell us about your organization and we'll find the best grant matches</p>
          </div>
          
          <form onSubmit={handleSubmit} className="grant-form">
            <div className="form-group">
              <Label htmlFor="projectSummary">Project Summary *</Label>
              <Textarea
                id="projectSummary"
                placeholder="Describe your project, mission, and goals. Include key details about your target community and expected impact..."
                value={formData.projectSummary}
                onChange={(e) => setFormData({...formData, projectSummary: e.target.value})}
                onFocus={() => setIsTyping(true)}
                onBlur={() => setIsTyping(false)}
                required
                rows={6}
                className={`form-textarea ${isTyping && formData.projectSummary ? 'form-textarea-active' : ''}`}
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <Label htmlFor="organizationType">Organization Type *</Label>
                <Select
                  value={formData.organizationType}
                  onValueChange={(value) => setFormData({...formData, organizationType: value})}
                  required
                >
                  <SelectTrigger className="form-select">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="nonprofit">Nonprofit Organization</SelectItem>
                    <SelectItem value="startup">Startup / Small Business</SelectItem>
                    <SelectItem value="education">Educational Institution</SelectItem>
                    <SelectItem value="research">Research Organization</SelectItem>
                    <SelectItem value="government">Government Agency</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="form-group">
                <Label htmlFor="focusArea">Focus Area *</Label>
                <Select
                  value={formData.focusArea}
                  onValueChange={(value) => setFormData({...formData, focusArea: value})}
                  required
                >
                  <SelectTrigger className="form-select">
                    <SelectValue placeholder="Select focus" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="climate">Climate & Environment</SelectItem>
                    <SelectItem value="education">Education</SelectItem>
                    <SelectItem value="health">Health & Wellness</SelectItem>
                    <SelectItem value="technology">Technology & Innovation</SelectItem>
                    <SelectItem value="community">Community Development</SelectItem>
                    <SelectItem value="arts">Arts & Culture</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="form-group">
              <Label htmlFor="email">Email Address *</Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                className="form-input"
              />
            </div>
            
            <Button type="submit" disabled={isLoading} className="submit-btn">
              {isLoading ? (
                <>
                  <div className="loading-spinner"></div>
                  Matching your grants...
                </>
              ) : (
                <>
                  <Search size={20} />
                  Find My Grants
                </>
              )}
            </Button>
          </form>
        </div>
      </section>

      {/* Results Section */}
      {showResults && (
        <section className="results-section" ref={resultsRef}>
          <div className="container">
            <div className="results-header">
              <h2 className="results-title">Your Top 10 Grant Matches</h2>
              <div className="ai-disclaimer">
                <span className="disclaimer-icon">⚠️</span>
                <p>AI-generated grant matches are templates — please review and rewrite in your own words before submission.</p>
              </div>
            </div>
            
            <div className="grants-grid">
              {mockGrants.map((grant) => (
                <GrantCard key={grant.id} grant={grant} onInteraction={handleInteraction} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <p className="footer-text">
              Built with ❤️ by <span className="brand">CelFund</span> — Powered by Celer Energy
            </p>
            <div className="footer-links">
              <a href="#privacy">Privacy Policy</a>
              <span className="separator">|</span>
              <a href="#terms">Terms</a>
              <span className="separator">|</span>
              <a href="#contact">Contact</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Upgrade Modal */}
      <UpgradeModal isOpen={showUpgradeModal} onClose={() => setShowUpgradeModal(false)} />
    </div>
  );
};

export default LandingPage;