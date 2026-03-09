import React, { useState, useRef, useEffect } from 'react';

const WebcamCapture = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    startWebcam();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startWebcam = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      });
      
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      setError('Unable to access webcam. Please check permissions.');
      console.error('Webcam error:', err);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
        onCapture(file);
      }
    }, 'image/jpeg', 0.8);

    setIsCapturing(true);
    setTimeout(() => setIsCapturing(false), 1000);
  };

  const stopWebcam = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    onClose();
  };

  return (
    <div className="webcam-modal">
      <div className="webcam-container">
        <div className="webcam-header">
          <h3>Capture from Webcam</h3>
          <button className="close-btn" onClick={stopWebcam}>×</button>
        </div>
        
        {error ? (
          <div className="webcam-error">
            <p>{error}</p>
            <button className="btn btn-secondary" onClick={startWebcam}>
              Try Again
            </button>
          </div>
        ) : (
          <div className="webcam-content">
            <div className="video-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="webcam-video"
              />
              <canvas
                ref={canvasRef}
                style={{ display: 'none' }}
              />
              {isCapturing && (
                <div className="capture-overlay">
                  <div className="capture-animation">📸</div>
                </div>
              )}
            </div>
            
            <div className="webcam-controls">
              <button
                className="btn btn-primary"
                onClick={capturePhoto}
                disabled={!stream}
              >
                📸 Capture Photo
              </button>
              <button
                className="btn btn-secondary"
                onClick={stopWebcam}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WebcamCapture;
