import React, { useState, useRef } from 'react';
import WebcamCapture from './WebcamCapture';
import SketchPad from './SketchPad';

const ImageUpload = ({ onSearch, loading, onReset }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [genderFilter, setGenderFilter] = useState('all');
  const [showWebcam, setShowWebcam] = useState(false);
  const fileInputRef = useRef(null);
  const [showSketchPad, setShowSketchPad] = useState(false);

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    } else {
      alert('Please select a valid image file.');
    }
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleSearch = () => {
    if (selectedFile) {
      onSearch(selectedFile, genderFilter);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setGenderFilter('all');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onReset();
  };

  const handleUploadAreaClick = () => {
    fileInputRef.current?.click();
  };

  const handleWebcamCapture = (file) => {
    handleFileSelect(file);
    setShowWebcam(false);
  };

  const handleWebcamClose = () => {
    setShowWebcam(false);
  };

  const handleSketchExport = (file) => {
    handleFileSelect(file);
    setShowSketchPad(false);
  };

  return (
    <div className="upload-container">
      <h2>Upload Forensic Sketch</h2>
      {/* Ensemble hidden */}
      
      <div
        className={`upload-area ${dragActive ? 'dragover' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleUploadAreaClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInputChange}
          className="file-input"
        />
        
        {preview ? (
          <div>
            <img src={preview} alt="Preview" className="preview-image" />
            <p className="upload-text">Click to change image</p>
          </div>
        ) : (
          <div>
            <div className="upload-icon">📁</div>
            <p className="upload-text">Drag & drop your sketch here</p>
            <p className="upload-subtext">or click to browse files</p>
          </div>
        )}
      </div>

        {preview && (
          <div>
            <div className="filter-section">
              <label htmlFor="gender-filter" className="filter-label">
                Filter by Gender:
              </label>
              <select
                id="gender-filter"
                value={genderFilter}
                onChange={(e) => setGenderFilter(e.target.value)}
                className="filter-select"
                disabled={loading}
              >
                <option value="all">All Genders</option>
                <option value="male">Male Only</option>
                <option value="female">Female Only</option>
              </select>
            </div>
            
            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={handleSearch}
                disabled={loading}
              >
                {loading ? 'Searching...' : 'Find Similar Faces'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={handleReset}
                disabled={loading}
              >
                Reset
              </button>
            </div>
          </div>
        )}

        {!preview && (
          <div className="upload-options">
            <p className="upload-or">or</p>
            <button
              className="btn btn-outline"
              onClick={() => setShowWebcam(true)}
              disabled={loading}
            >
              📷 Capture from Webcam
            </button>
            <div style={{ height: '12px' }}></div>
            <button
              className="btn btn-outline"
              onClick={() => setShowSketchPad(true)}
              disabled={loading}
            >
              ✍️ Draw a Sketch
            </button>
          </div>
        )}

        {showWebcam && (
          <WebcamCapture
            onCapture={handleWebcamCapture}
            onClose={handleWebcamClose}
          />
        )}

        {showSketchPad && (
          <SketchPad
            onExport={handleSketchExport}
            onClose={() => setShowSketchPad(false)}
          />
        )}
    </div>
  );
};

export default ImageUpload;
