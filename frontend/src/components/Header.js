import React from 'react';

const Header = ({ 
  onToggleAnalytics, 
  onToggleDarkMode, 
  onToggleHistory,
  darkMode, 
  showHistory 
}) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <h1>🔍 Forensic Sketch Recognition</h1>
          <p>Upload a forensic sketch to find the most similar faces in our database</p>
        </div>
        <div className="header-controls">
          <button 
            className="control-btn analytics-btn"
            onClick={onToggleAnalytics}
            title="View Analytics Dashboard"
          >
            📊 Analytics
          </button>
          <button 
            className={`control-btn ${showHistory ? 'active' : ''}`}
            onClick={onToggleHistory}
            title="View Search History"
          >
            📚 History
          </button>
          <button 
            className={`control-btn ${darkMode ? 'active' : ''}`}
            onClick={onToggleDarkMode}
            title={`Switch to ${darkMode ? 'Light' : 'Dark'} Mode`}
          >
            {darkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
