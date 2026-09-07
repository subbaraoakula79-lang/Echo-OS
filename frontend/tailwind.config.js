/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'echo-dark': '#0a0e15',
        'echo-card': '#0d1117',
        'echo-orange': '#ff5e00',
        'echo-gold': '#ffd700',
      },
    },
  },
  plugins: [],
}
