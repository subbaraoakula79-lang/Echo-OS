/**
 * ECHO OS — Voice Waveform Bar
 * Animated audio waveform that responds to voice input.
 */

import { useRef, useEffect } from 'react';

interface VoiceBarProps {
  isActive: boolean;
}

export default function VoiceBar({ isActive }: VoiceBarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let time = 0;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = canvas.offsetWidth * dpr;
      canvas.height = canvas.offsetHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);

    const draw = () => {
      time += 0.02;
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      const mid = h / 2;

      ctx.clearRect(0, 0, w, h);

      const segments = 120;
      const segW = w / segments;

      for (let i = 0; i < segments; i++) {
        const x = i * segW;
        const nx = i / segments;

        let amplitude;
        if (isActive) {
          amplitude = (
            Math.sin(time * 4 + nx * 8) * 0.4 +
            Math.sin(time * 7 + nx * 12) * 0.2 +
            Math.sin(time * 11 + nx * 20) * 0.15 +
            Math.random() * 0.05
          ) * h * 0.35;
        } else {
          amplitude = (
            Math.sin(time * 1.5 + nx * 6) * 0.08 +
            Math.sin(time * 0.7 + nx * 3) * 0.05
          ) * h * 0.3;
        }

        const barH = Math.abs(amplitude);
        const alpha = isActive ? 0.6 + Math.abs(amplitude / (h * 0.35)) * 0.4 : 0.15;

        // Orange/gold gradient for bars
        const grad = ctx.createLinearGradient(x, mid - barH, x, mid + barH);
        grad.addColorStop(0, `rgba(255, 94, 0, ${alpha})`);
        grad.addColorStop(0.5, `rgba(255, 165, 0, ${alpha * 0.8})`);
        grad.addColorStop(1, `rgba(255, 94, 0, ${alpha * 0.3})`);

        ctx.fillStyle = grad;
        ctx.fillRect(x, mid - barH, segW - 1, barH * 2);
      }

      // Center line
      ctx.strokeStyle = `rgba(255, 94, 0, ${isActive ? 0.3 : 0.08})`;
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(0, mid);
      ctx.lineTo(w, mid);
      ctx.stroke();

      animRef.current = requestAnimationFrame(draw);
    };

    animRef.current = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [isActive]);

  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />;
}
