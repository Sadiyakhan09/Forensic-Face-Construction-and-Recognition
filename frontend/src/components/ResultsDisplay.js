import React from 'react';

const ResultsDisplay = ({ results, onReset }) => {
  if (!results) return null;

  const { input_sketch, top_matches, detected_attributes, filter_applied, sketch2photo_preview } = results;

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Search Results</h2>
        <p>Top {top_matches.length} most similar faces found</p>
      </div>

      <div className="input-sketch" style={{ display: 'grid', gap: '1rem', gridTemplateColumns: sketch2photo_preview ? '1fr 1fr' : '1fr' }}>
        <div>
          <h3>Your Sketch</h3>
          <img 
            src={`data:image/jpeg;base64,${input_sketch}`} 
            alt="Input sketch" 
          />
          {detected_attributes && (
            <div className="detected-attributes">
              <h4>Detected Attributes:</h4>
              <div className="attribute-tags">
                <span className="attribute-tag gender">
                  {detected_attributes.gender}
                </span>
                <span className="attribute-tag age">
                  Age: {detected_attributes.age}
                </span>
              </div>
            </div>
          )}
          {filter_applied && filter_applied !== 'all' && (
            <div className="filter-info">
              <p>Filtered by: <strong>{filter_applied}</strong></p>
            </div>
          )}
        </div>
        {sketch2photo_preview && (
          <div>
            <h3>Generated Photo</h3>
            <img 
              src={`data:image/jpeg;base64,${sketch2photo_preview}`} 
              alt="Generated from sketch" 
              style={{ maxWidth: '200px', maxHeight: '200px', borderRadius: '10px', boxShadow: '0 5px 15px rgba(0,0,0,0.1)' }}
            />
          </div>
        )}
      </div>

      <div className="matches-grid">
        {top_matches.map((match, index) => (
          <div key={index} className="match-card">
            <div className="rank-badge">{index + 1}</div>
            <h4>Match #{index + 1}</h4>
            <img 
              src={`data:image/jpeg;base64,${match.photo_base64}`} 
              alt={`Match ${index + 1}`}
              className="match-image"
            />
            <div className="similarity-score">
              {(match.similarity * 100).toFixed(1)}% Similar
            </div>
            <p style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
              {match.image_name}
            </p>
          </div>
        ))}
      </div>

      <div className="button-group" style={{ marginTop: '2rem' }}>
        <button className="btn btn-secondary" onClick={onReset}>
          Search Another Sketch
        </button>
      </div>
    </div>
  );
};

export default ResultsDisplay;
