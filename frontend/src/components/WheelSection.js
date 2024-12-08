// src/components/WheelSection.js
import React, { useState, useEffect, useRef } from 'react';
import './WheelSection.css'; // Optional: For styling purposes

const WheelSection = () => {
  const canvasRef = useRef(null);
  const [segments, setSegments] = useState([]);
  const [colors, setColors] = useState([]);
  const [isSpinning, setIsSpinning] = useState(false);
  const [result, setResult] = useState('');
  const [nameField, setNameField] = useState('');

  const startAngle = useRef(0);
  const spinTimeout = useRef(null);
  const spinAngleStart = useRef(0);
  const spinTime = useRef(0);
  const spinTimeTotal = useRef(0);
  const arc = useRef(0);

  // Function to generate a unique color using HSL for better distinction
  const getUniqueColor = (index, total) => {
    const hue = index * (360 / total);
    return `hsl(${hue}, 80%, 60%)`;
  };

  // Initialize the wheel
  useEffect(() => {
    drawWheel();
    // Cleanup on unmount
    return () => clearTimeout(spinTimeout.current);
  }, [segments, colors]);

  const addName = () => {
    const name = nameField.trim();
    if (name && !segments.includes(name)) {
      const newSegments = [...segments, name];
      setSegments(newSegments);
      setColors(newSegments.map((_, idx) => getUniqueColor(idx, newSegments.length)));
      setNameField('');
    }
  };

  const clearSegments = () => {
    setSegments([]);
    setColors([]);
    setResult(''); // Clear any result message
    startAngle.current = 0; // Reset the wheel angle if desired
  };

  const drawWheel = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const numSegments = segments.length;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (numSegments === 0) {
      // Draw default wheel if no segments
      const defaultColor = '#cccccc';
      ctx.fillStyle = defaultColor;
      ctx.beginPath();
      ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2 - 5, 0, Math.PI * 2, false);
      ctx.fill();

      // Draw border
      ctx.lineWidth = 5;
      ctx.strokeStyle = '#333';
      ctx.stroke();

      // Draw center circle
      ctx.beginPath();
      ctx.arc(canvas.width / 2, canvas.height / 2, 20, 0, Math.PI * 2, false);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#333';
      ctx.stroke();

      return;
    }

    arc.current = (Math.PI * 2) / numSegments;

    for (let i = 0; i < numSegments; i++) {
      const angle = startAngle.current + i * arc.current;
      ctx.fillStyle = colors[i] || getUniqueColor(i, numSegments);
      ctx.beginPath();
      ctx.moveTo(canvas.width / 2, canvas.height / 2);
      ctx.arc(
        canvas.width / 2,
        canvas.height / 2,
        canvas.width / 2 - 5,
        angle,
        angle + arc.current,
        false
      );
      ctx.lineTo(canvas.width / 2, canvas.height / 2);
      ctx.fill();
    }

    // Draw center circle
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, 20, 0, Math.PI * 2, false);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#333';
    ctx.stroke();

    // Draw outer border
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2 - 5, 0, Math.PI * 2, false);
    ctx.lineWidth = 5;
    ctx.strokeStyle = '#333';
    ctx.stroke();

    // Draw text labels
    for (let i = 0; i < numSegments; i++) {
      const angle = startAngle.current + i * arc.current + arc.current / 2;
      ctx.save();
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate(angle);
      ctx.textAlign = 'right';
      ctx.fillStyle = '#fff';
      ctx.font = '12px Arial';
      ctx.fillText(segments[i], canvas.width / 2 - 15, 5);
      ctx.restore();
    }
  };

  const spin = () => {
    if (isSpinning || segments.length === 0) return;
    setIsSpinning(true);
    spinAngleStart.current = Math.random() * 10 + 10; // Random spin angle between 10-20
    spinTime.current = 0;
    spinTimeTotal.current = Math.random() * 3000 + 4000; // Spin duration between 4-7 seconds
    rotateWheel();
  };

  const rotateWheel = () => {
    spinTime.current += 30;
    if (spinTime.current >= spinTimeTotal.current) {
      stopRotateWheel();
      return;
    }
    const spinAngle =
      spinAngleStart.current - easeOut(spinTime.current, 0, spinAngleStart.current, spinTimeTotal.current);
    startAngle.current += (spinAngle * Math.PI) / 180;
    drawWheel();
    spinTimeout.current = setTimeout(rotateWheel, 30);
  };

  const stopRotateWheel = () => {
    clearTimeout(spinTimeout.current);
    const degrees = (startAngle.current * 180) / Math.PI + 90; // +90 to align with arrow pointing downward
    const arcd = (arc.current * 180) / Math.PI;
    const index = Math.floor((360 - (degrees % 360)) / arcd);
    const selected = segments[index % segments.length];
    setResult(`🎉 You won: ${selected}! 🎉`);
    setIsSpinning(false);
  };

  const easeOut = (t, b, c, d) => {
    const ts = (t /= d) * t;
    const tc = ts * t;
    return b + c * (tc + -3 * ts + 3 * t);
  };

  return (
    <div className="wheel-section">
      <h2>Spin the Wheel</h2>
      <div className="wheel-container">
        <canvas ref={canvasRef} width="200" height="200" />
        <div className="arrow"></div>
      </div>
      <div className="nameInput">
        <input
          type="text"
          value={nameField}
          onChange={(e) => setNameField(e.target.value)}
          placeholder="Enter name"
        />
        <button onClick={addName}>Add</button>
        <button onClick={clearSegments}>Clear</button> {/* The new Clear button */}
      </div>
      <button onClick={spin}>Spin the Wheel!</button>
      <div className="nameList">
        <strong>Participants:</strong> {segments.length > 0 ? segments.join(', ') : 'None'}
      </div>
      <div className="result">{result}</div>
    </div>
  );
};

export default WheelSection;
