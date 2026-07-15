/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        jarvis: {
          blue: "#00d2ff",
          orange: "#ff5e00",
          gold: "#ffd700",
          dark: "#0b0c10",
        }
      },
      animation: {
        'spin-slow': 'spin 8s linear infinite',
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: 1, textShadow: '0 0 10px #ff5e00' },
          '50%': { opacity: .7, textShadow: '0 0 20px #ffd700' },
        }
      }
    },
  },
  plugins: [],
}
