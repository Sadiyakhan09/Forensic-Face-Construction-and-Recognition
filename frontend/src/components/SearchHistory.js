import React from 'react';
import './SearchHistory.css';

const SearchHistory = ({ history, onClose, onClear, onLoadSearch }) => {
  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getGenderIcon = (gender) => {
    return gender === 'male' ? '👨' : gender === 'female' ? '👩' : '👤';
  };

  const getEnsembleIcon = (useEnsemble) => {
    return useEnsemble ? '🧠' : '🤖';
  };

  return (
    <div className="search-history-overlay">
      <div className="search-history-modal">
        <div className="search-history-header">
          <h2>🔍 Search History</h2>
          <div className="search-history-actions">
            <button 
              className="clear-history-btn"
              onClick={onClear}
              disabled={history.length === 0}
            >
              🗑️ Clear All
            </button>
            <button className="close-btn" onClick={onClose}>
              ✕
            </button>
          </div>
        </div>
        
        <div className="search-history-content">
          {history.length === 0 ? (
            <div className="no-history">
              <p>No search history yet</p>
              <p>Start searching to see your history here!</p>
            </div>
          ) : (
            <div className="history-list">
              {history.map((search) => (
                <div key={search.id} className="history-item">
                  <div className="history-item-header">
                    <div className="history-item-info">
                      <span className="history-image-name">
                        📷 {search.imageName}
                      </span>
                      <span className="history-timestamp">
                        {formatDate(search.timestamp)}
                      </span>
                    </div>
                    <div className="history-item-badges">
                      {getGenderIcon(search.genderFilter)}
                      {getEnsembleIcon(search.useEnsemble)}
                    </div>
                  </div>
                  
                  <div className="history-item-details">
                    <div className="history-results-preview">
                      {search.results.matches && search.results.matches.length > 0 ? (
                        <div className="preview-matches">
                          <span className="preview-text">
                            Found {search.results.matches.length} matches
                          </span>
                          <div className="preview-scores">
                            {search.results.matches.slice(0, 3).map((match, index) => (
                              <span key={index} className="preview-score">
                                {Math.round(match.similarity * 100)}%
                              </span>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <span className="preview-text">No matches found</span>
                      )}
                    </div>
                    
                    <button 
                      className="load-search-btn"
                      onClick={() => onLoadSearch(search)}
                    >
                      🔄 Load Results
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchHistory;
