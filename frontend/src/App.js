import React, { useState, useEffect } from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import ResultsDisplay from './components/ResultsDisplay';
import Header from './components/Header';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import SearchHistory from './components/SearchHistory';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  // Ensemble hidden
  const [darkMode, setDarkMode] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load dark mode preference from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
  }, []);

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // Load search history from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
  }, []);

  const handleSearch = async (imageFile, genderFilter = 'all') => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      
      // Build URL with parameters
      const params = new URLSearchParams();
      if (genderFilter !== 'all') {
        params.append('gender_filter', genderFilter);
      }
      // Ensemble disabled in UI
      
      const url = `/find-match${params.toString() ? '?' + params.toString() : ''}`;

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      
      // Save to search history
      const searchEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        genderFilter,
        useEnsemble: false,
        results: data,
        imageName: imageFile.name
      };
      
      const newHistory = [searchEntry, ...searchHistory.slice(0, 9)]; // Keep last 10 searches
      setSearchHistory(newHistory);
      localStorage.setItem('searchHistory', JSON.stringify(newHistory));
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
  };

  const toggleAnalytics = () => {
    setShowAnalytics(!showAnalytics);
  };

  // Ensemble toggle removed

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const toggleHistory = () => {
    setShowHistory(!showHistory);
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('searchHistory');
  };

  return (
    <div className="App">
      <Header 
        onToggleAnalytics={toggleAnalytics}
        onToggleDarkMode={toggleDarkMode}
        onToggleHistory={toggleHistory}
        darkMode={darkMode}
        showHistory={showHistory}
      />
      <main className="main-content">
        <div className="container">
          <ImageUpload 
            onSearch={handleSearch} 
            loading={loading}
            onReset={handleReset}
          />
          
          {loading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Analyzing sketch and searching database...</p>
              {/* Ensemble hidden */}
            </div>
          )}

          {error && (
            <div className="error-container">
              <h3>Error</h3>
              <p>{error}</p>
              <button onClick={handleReset} className="retry-button">
                Try Again
              </button>
            </div>
          )}

          {results && (
            <ResultsDisplay 
              results={results} 
              onReset={handleReset}
            />
          )}
        </div>
      </main>
      
      {showAnalytics && (
        <AnalyticsDashboard onClose={toggleAnalytics} />
      )}
      
      {showHistory && (
        <SearchHistory 
          history={searchHistory}
          onClose={() => setShowHistory(false)}
          onClear={clearHistory}
          onLoadSearch={(search) => {
            setResults(search.results);
            setShowHistory(false);
          }}
        />
      )}
    </div>
  );
}

export default App;
