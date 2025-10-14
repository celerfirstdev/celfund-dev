import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';

const TypingBadge = () => {
  const words = ['Fast.', 'Accurate.', 'Effortless.'];
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentWord = words[currentWordIndex];
    const typingSpeed = isDeleting ? 50 : 100;
    const pauseTime = 2000;

    const timeout = setTimeout(() => {
      if (!isDeleting && currentText === currentWord) {
        // Pause before deleting
        setTimeout(() => setIsDeleting(true), pauseTime);
      } else if (isDeleting && currentText === '') {
        // Move to next word
        setIsDeleting(false);
        setCurrentWordIndex((prev) => (prev + 1) % words.length);
      } else {
        // Type or delete character
        setCurrentText(
          isDeleting
            ? currentWord.substring(0, currentText.length - 1)
            : currentWord.substring(0, currentText.length + 1)
        );
      }
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, currentWordIndex, words]);

  return (
    <div className="hero-badge">
      <Sparkles size={16} />
      <span>AI-Powered Grant Matching — {currentText}<span className="typing-cursor">|</span></span>
    </div>
  );
};

export default TypingBadge;