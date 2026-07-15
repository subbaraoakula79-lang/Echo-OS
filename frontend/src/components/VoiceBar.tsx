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
    let t = 0;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = canvas.offsetWidth * dpr;
      canvas.height = canvas.offsetHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);

    const draw = () => {
      t += 0.03;
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      const cy = h / 2;

      ctx.clearRect(0, 0, w, h);

      const bars = 60;
      const barW = w / bars;

      for (let i = 0; i < bars; i++) {
        const x = i * barW;
        const norm = i / bars;
        const center = Math.abs(norm - 0.5) * 2; // 0 at center, 1 at edges

        let amplitude: number;
        if (isActive) {
          amplitude = (1 - center * 0.6) * (
            Math.sin(t * 4 + i * 0.3) * 0.4 +
            Math.sin(t * 7 + i * 0.15) * 0.3 +
            Math.sin(t * 2 + i * 0.5) * 0.3 +
            0.3
          );
        } else {
          amplitude = (1 - center * 0.8) * (Math.sin(t + i * 0.2) * 0.1 + 0.15);
        }

        const barH = Math.max(2, amplitude * h * 0.8);

        // Gradient per bar
        const grad = ctx.createLinearGradient(x, cy - barH / 2, x, cy + barH / 2);
        if (isActive) {
          grad.addColorStop(0, 'rgba(255, 0, 128, 0.8)');
          grad.addColorStop(0.5, 'rgba(0, 153, 255, 0.9)');
          grad.addColorStop(1, 'rgba(255, 0, 128, 0.8)');
        } else {
          grad.addColorStop(0, 'rgba(0, 153, 255, 0.2)');
          grad.addColorStop(0.5, 'rgba(0, 153, 255, 0.3)');
          grad.addColorStop(1, 'rgba(0, 153, 255, 0.2)');
        }

        ctx.fillStyle = grad;
        ctx.fillRect(x + 1, cy - barH / 2, barW - 2, barH);
      }

      animRef.current = requestAnimationFrame(draw);
    };

    animRef.current = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [isActive]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: '100%', height: '100%', display: 'block' }}
    />
  );
}
