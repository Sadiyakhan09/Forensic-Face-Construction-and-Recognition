import React, { useRef, useState, useEffect } from 'react';

const SketchPad = ({ onClose, onExport, initialStrokeColor = '#000000', initialStrokeWidth = 4 }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const ctxRef = useRef(null);
  const drawingRef = useRef(false);
  const lastPosRef = useRef({ x: 0, y: 0 });

  const [strokeColor, setStrokeColor] = useState(initialStrokeColor);
  const [strokeWidth, setStrokeWidth] = useState(initialStrokeWidth);
  const [eraserMode, setEraserMode] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const dpr = window.devicePixelRatio || 1;
    const width = Math.min(600, container.clientWidth - 32);
    const height = Math.min(600, Math.max(300, Math.floor(width * 0.75)));

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = strokeWidth;
    ctxRef.current = ctx;
  }, []);

  useEffect(() => {
    const ctx = ctxRef.current;
    if (!ctx) return;
    ctx.strokeStyle = eraserMode ? '#ffffff' : strokeColor;
    ctx.lineWidth = strokeWidth;
  }, [strokeColor, strokeWidth, eraserMode]);

  const getPos = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  };

  const handlePointerDown = (e) => {
    e.preventDefault();
    drawingRef.current = true;
    lastPosRef.current = getPos(e);
  };

  const handlePointerMove = (e) => {
    if (!drawingRef.current) return;
    const ctx = ctxRef.current;
    const current = getPos(e);
    const last = lastPosRef.current;
    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    ctx.lineTo(current.x, current.y);
    ctx.stroke();
    lastPosRef.current = current;
  };

  const handlePointerUp = (e) => {
    drawingRef.current = false;
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    const ctx = ctxRef.current;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = eraserMode ? '#ffffff' : strokeColor;
  };

  const handleExport = async () => {
    const canvas = canvasRef.current;
    // Export as PNG Blob
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], 'sketch.png', { type: 'image/png' });
      onExport(file);
      onClose();
    }, 'image/png', 1.0);
  };

  return (
    <div className="webcam-modal">
      <div className="webcam-container" ref={containerRef}>
        <div className="webcam-header">
          <h3>Draw Sketch</h3>
          <button className="close-btn" onClick={onClose} aria-label="Close">×</button>
        </div>
        <div className="sketch-controls" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            Color
            <input type="color" value={strokeColor} onChange={(e) => setStrokeColor(e.target.value)} />
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            Width
            <input type="range" min="1" max="24" value={strokeWidth} onChange={(e) => setStrokeWidth(parseInt(e.target.value))} />
          </label>
          <button className={`btn ${eraserMode ? 'btn-secondary' : 'btn-outline'}`} onClick={() => setEraserMode(!eraserMode)}>
            {eraserMode ? 'Eraser On' : 'Eraser Off'}
          </button>
          <button className="btn btn-secondary" onClick={handleClear}>Clear</button>
          <button className="btn btn-primary" onClick={handleExport}>Use This Sketch</button>
        </div>
        <div className="sketch-canvas-wrapper" style={{ display: 'flex', justifyContent: 'center' }}>
          <canvas
            ref={canvasRef}
            style={{ borderRadius: '12px', border: '2px solid #e9ecef', background: '#ffffff', touchAction: 'none' }}
            onMouseDown={handlePointerDown}
            onMouseMove={handlePointerMove}
            onMouseUp={handlePointerUp}
            onMouseLeave={handlePointerUp}
            onTouchStart={handlePointerDown}
            onTouchMove={handlePointerMove}
            onTouchEnd={handlePointerUp}
          />
        </div>
      </div>
    </div>
  );
};

export default SketchPad;



