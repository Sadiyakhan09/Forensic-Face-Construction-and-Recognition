import React, { useState, useEffect } from 'react';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = ({ onClose }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  // Auto-refresh functionality
  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchAnalyticsData, 5000); // Refresh every 5 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const API = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
      const response = await fetch(`${API}/analytics/dashboard`);
      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Simple chart component for visualizations
  const SimpleBarChart = ({ data, title, color = '#4299e1' }) => {
    const maxValue = Math.max(...Object.values(data));
    return (
      <div className="chart-container">
        <h4>{title}</h4>
        <div className="bar-chart">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="bar-item">
              <div className="bar-label">{key}</div>
              <div className="bar-wrapper">
                <div 
                  className="bar-fill" 
                  style={{ 
                    width: `${(value / maxValue) * 100}%`,
                    backgroundColor: color
                  }}
                />
                <span className="bar-value">{value}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const exportData = async (format) => {
    try {
      const API = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
      const response = await fetch(`${API}/analytics/export?format=${format}`);
      if (!response.ok) {
        throw new Error('Failed to export data');
      }
      const data = await response.json();
      
      // Create download link
      const blob = new Blob([data.data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_export.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="analytics-modal">
        <div className="analytics-container">
          <div className="analytics-header">
            <h2>Analytics Dashboard</h2>
            <button className="close-btn" onClick={onClose}>&times;</button>
          </div>
          <div className="loading">Loading analytics data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-modal">
        <div className="analytics-container">
          <div className="analytics-header">
            <h2>Analytics Dashboard</h2>
            <button className="close-btn" onClick={onClose}>&times;</button>
          </div>
          <div className="error">Error: {error}</div>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="analytics-modal">
        <div className="analytics-container">
          <div className="analytics-header">
            <h2>Analytics Dashboard</h2>
            <button className="close-btn" onClick={onClose}>&times;</button>
          </div>
          <div className="no-data">No analytics data available</div>
        </div>
      </div>
    );
  }

  const { overview = {}, gender_distribution = {}, hourly_usage = {}, similarity_distribution = {}, performance_trends = {} } = analyticsData || {};

  return (
    <div className="analytics-modal">
      <div className="analytics-container">
        <div className="analytics-header">
          <h2>Analytics Dashboard</h2>
          <div className="header-actions">
            <button 
              className={`btn ${autoRefresh ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              {autoRefresh ? '⏸️ Pause' : '▶️ Auto-Refresh'}
            </button>
            <button className="btn btn-secondary" onClick={() => exportData('json')}>
              Export JSON
            </button>
            <button className="btn btn-secondary" onClick={() => exportData('csv')}>
              Export CSV
            </button>
            <button className="close-btn" onClick={onClose}>&times;</button>
          </div>
        </div>

        <div className="analytics-tabs">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${activeTab === 'usage' ? 'active' : ''}`}
            onClick={() => setActiveTab('usage')}
          >
            Usage Patterns
          </button>
          <button 
            className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            Performance
          </button>
        </div>

        <div className="analytics-content">
          {activeTab === 'overview' && (
            <div className="overview-tab">
              <div className="metrics-grid">
                <div className="metric-card">
                  <h3>Total Searches</h3>
                  <div className="metric-value">{overview.total_searches}</div>
                </div>
                <div className="metric-card">
                  <h3>Success Rate</h3>
                  <div className="metric-value">{overview.accuracy_percentage}%</div>
                </div>
                <div className="metric-card">
                  <h3>Avg Response Time</h3>
                  <div className="metric-value">{overview.average_response_time}s</div>
                </div>
                <div className="metric-card">
                  <h3>Avg Similarity</h3>
                  <div className="metric-value">{overview.average_similarity}</div>
                </div>
              </div>

              <div className="charts-grid">
                <div className="chart-card">
                  <SimpleBarChart 
                    data={gender_distribution} 
                    title="Gender Distribution" 
                    color="#4299e1"
                  />
                </div>
                
                <div className="chart-card">
                  <SimpleBarChart 
                    data={hourly_usage} 
                    title="Hourly Usage Pattern" 
                    color="#48bb78"
                  />
                </div>

                <div className="chart-card">
                  <h3>Similarity Distribution</h3>
                  <div className="similarity-chart">
                    {Object.entries(similarity_distribution).map(([range, count]) => (
                      <div key={range} className="similarity-bar">
                        <span className="similarity-label">{range}</span>
                        <div className="bar-container">
                          <div 
                            className="bar similarity-bar-fill" 
                            style={{ width: `${(count / Math.max(...Object.values(similarity_distribution))) * 100}%` }}
                          ></div>
                        </div>
                        <span className="similarity-count">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'usage' && (
            <div className="usage-tab">
              <div className="chart-card">
                <h3>Hourly Usage Pattern</h3>
                <div className="hourly-chart">
                  {Object.entries(hourly_usage).map(([hour, count]) => (
                    <div key={hour} className="hourly-bar">
                      <span className="hour-label">{hour}:00</span>
                      <div className="bar-container">
                        <div 
                          className="bar hourly-bar-fill" 
                          style={{ height: `${(count / Math.max(...Object.values(hourly_usage))) * 100}%` }}
                        ></div>
                      </div>
                      <span className="hour-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="performance-tab">
              <div className="chart-card">
                <h3>Daily Performance Trends</h3>
                <div className="trends-chart">
                  <div className="trend-line">
                    <h4>Daily Searches</h4>
                    <div className="trend-data">
                      {performance_trends.daily_searches?.map((value, index) => (
                        <div key={index} className="trend-point">
                          <span className="trend-value">{value}</span>
                          <span className="trend-day">Day {index + 1}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="trend-line">
                    <h4>Daily Accuracy</h4>
                    <div className="trend-data">
                      {performance_trends.daily_accuracy?.map((value, index) => (
                        <div key={index} className="trend-point">
                          <span className="trend-value">{value.toFixed(1)}%</span>
                          <span className="trend-day">Day {index + 1}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
