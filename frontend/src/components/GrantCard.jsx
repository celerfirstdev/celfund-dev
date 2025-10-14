import React from 'react';
import { Calendar, DollarSign, Copy, Bookmark, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { useToast } from '../hooks/use-toast';

const GrantCard = ({ grant, onInteraction }) => {
  const { toast } = useToast();

  const handleCopy = () => {
    const text = `${grant.title}\nFunder: ${grant.funder}\n${grant.description}\nDeadline: ${grant.deadline}\nAmount: ${grant.amount}`;
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "Grant details copied successfully"
    });
    onInteraction();
  };

  const handleSave = () => {
    toast({
      title: "Grant saved",
      description: "Added to your saved grants"
    });
    onInteraction();
  };

  const formatDeadline = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <Card className="grant-card">
      <div className="grant-card-header">
        <h3 className="grant-title">{grant.title}</h3>
        <div className="grant-actions">
          <button onClick={handleSave} className="action-btn" title="Save grant">
            <Bookmark size={18} />
          </button>
          <button onClick={handleCopy} className="action-btn" title="Copy details">
            <Copy size={18} />
          </button>
        </div>
      </div>
      
      <p className="grant-funder">{grant.funder}</p>
      
      <p className="grant-description">{grant.description}</p>
      
      <div className="grant-meta">
        <div className="meta-item">
          <Calendar size={16} />
          <span>Deadline: {formatDeadline(grant.deadline)}</span>
        </div>
        <div className="meta-item">
          <DollarSign size={16} />
          <span>{grant.amount}</span>
        </div>
      </div>
      
      <Button className="view-details-btn" onClick={onInteraction}>
        View Full Details
        <ExternalLink size={16} className="ml-2" />
      </Button>
    </Card>
  );
};

export default GrantCard;