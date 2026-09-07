/**
 * ECHO OS — Hologram Canvas
 * Animated energy core with JARVIS orange/gold color scheme.
 */

import { useRef, useEffect } from 'react';

interface HologramCanvasProps {
  isSpeaking?: boolean;
}

export default function HologramCanvas({ isSpeaking = false }: HologramCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animFrameRef = useRef<number>(0);

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

    // Particles — orange/gold palette
    const particles: { x: number; y: number; vx: number; vy: number; size: number; alpha: number; hue: number }[] = [];
    for (let i = 0; i < 90; i++) {
      particles.push({
        x: Math.random() * canvas.offsetWidth,
        y: Math.random() * canvas.offsetHeight,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.5 + 0.1,
        hue: Math.random() > 0.5 ? 25 : 45, // orange or gold
      });
    }

    const draw = () => {
      time += 0.016;
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      const cx = w / 2;
      const cy = h / 2;

      ctx.clearRect(0, 0, w, h);

      // Background radial — warm tones
      const bgGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.min(w, h) * 0.6);
      bgGrad.addColorStop(0, 'rgba(255, 94, 0, 0.06)');
      bgGrad.addColorStop(0.4, 'rgba(255, 215, 0, 0.03)');
      bgGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      // Core energy
      const pulse = isSpeaking ? Math.sin(time * 10) * 0.4 + 0.8 : Math.sin(time * 2) * 0.15 + 0.7;
      const coreR = 28 + (isSpeaking ? Math.sin(time * 8) * 8 : Math.sin(time * 1.5) * 3);

      // Outer glow
      const outerGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR * 3);
      outerGlow.addColorStop(0, `rgba(255, 94, 0, ${0.3 * pulse})`);
      outerGlow.addColorStop(0.5, `rgba(255, 215, 0, ${0.15 * pulse})`);
      outerGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = outerGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, coreR * 3, 0, Math.PI * 2);
      ctx.fill();

      // Core
      const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR);
      coreGrad.addColorStop(0, `rgba(255, 255, 255, ${0.9 * pulse})`);
      coreGrad.addColorStop(0.3, `rgba(255, 165, 0, ${0.7 * pulse})`);
      coreGrad.addColorStop(0.7, `rgba(255, 94, 0, ${0.4 * pulse})`);
      coreGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = coreGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
      ctx.fill();

      // Rotating ring arcs — orange/gold
      const drawArc = (radius: number, speed: number, color: string, lw: number, start: number, sweep: number) => {
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(time * speed);
        ctx.strokeStyle = color;
        ctx.lineWidth = lw;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.arc(0, 0, radius, start, start + sweep);
        ctx.stroke();
        ctx.restore();
      };

      drawArc(50, 0.6, `rgba(255, 94, 0, ${0.5 * pulse})`, 1.5, 0, Math.PI * 0.7);
      drawArc(50, 0.6, `rgba(255, 94, 0, ${0.3 * pulse})`, 1.5, Math.PI, Math.PI * 0.5);
      drawArc(65, -0.4, `rgba(255, 215, 0, ${0.4 * pulse})`, 1, 0.5, Math.PI * 0.8);
      drawArc(65, -0.4, `rgba(255, 215, 0, ${0.25 * pulse})`, 1, Math.PI + 0.5, Math.PI * 0.6);
      drawArc(82, 0.25, `rgba(255, 94, 0, ${0.2 * pulse})`, 0.8, 0, Math.PI * 1.2);
      drawArc(97, -0.15, `rgba(255, 215, 0, ${0.15 * pulse})`, 0.5, 1, Math.PI * 0.9);

      // Data tick marks
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(time * 0.1);
      for (let i = 0; i < 36; i++) {
        const angle = (Math.PI * 2 / 36) * i;
        const inner = 95;
        const outer = 100 + (i % 3 === 0 ? 5 : 2);
        ctx.strokeStyle = `rgba(255, 94, 0, ${i % 3 === 0 ? 0.3 : 0.1})`;
        ctx.lineWidth = i % 3 === 0 ? 1 : 0.5;
        ctx.beginPath();
        ctx.moveTo(Math.cos(angle) * inner, Math.sin(angle) * inner);
        ctx.lineTo(Math.cos(angle) * outer, Math.sin(angle) * outer);
        ctx.stroke();
      }
      ctx.restore();

      // Orbital nodes
      const drawNode = (radius: number, speed: number, r: number, g: number, b: number, alpha: number, size: number) => {
        const angle = time * speed;
        const nx = cx + Math.cos(angle) * radius;
        const ny = cy + Math.sin(angle) * radius;

        const glow = ctx.createRadialGradient(nx, ny, 0, nx, ny, size * 5);
        glow.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${alpha * 0.6 * pulse})`);
        glow.addColorStop(1, 'transparent');
        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(nx, ny, size * 5, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(nx, ny, size, 0, Math.PI * 2);
        ctx.fill();
      };

      drawNode(50, 0.6, 255, 165, 0, 0.9, 2.5);   // Orange
      drawNode(65, -0.4, 255, 215, 0, 0.8, 2);      // Gold
      drawNode(82, 0.25, 255, 94, 0, 0.6, 1.8);     // Deep orange

      // Floating particles
      particles.forEach((p) => {
        p.x += p.vx + (isSpeaking ? Math.sin(time * 4 + p.hue) * 0.8 : 0);
        p.y += p.vy + (isSpeaking ? Math.cos(time * 4 + p.hue) * 0.8 : 0);
        if (p.x < 0) p.x = w;
        if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h;
        if (p.y > h) p.y = 0;

        const dist = Math.sqrt((p.x - cx) ** 2 + (p.y - cy) ** 2);
        const maxDist = Math.min(w, h) * 0.5;
        const prox = Math.max(0, 1 - dist / maxDist);

        const col = p.hue === 25 ? '255, 94, 0' : '255, 215, 0';
        ctx.fillStyle = `rgba(${col}, ${p.alpha * prox * (isSpeaking ? 1.8 : 1)})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      });

      // Scanlines
      for (let y = 0; y < h; y += 3) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
        ctx.fillRect(0, y, w, 1);
      }

      animFrameRef.current = requestAnimationFrame(draw);
    };

    animFrameRef.current = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(animFrameRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [isSpeaking]);

  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />;
}
