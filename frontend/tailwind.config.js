/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'goldman': ['Goldman', 'sans-serif'],
      },
      colors: {
        'primary': '#FFD700',
        'primary-dark': '#FFA500',
        'bg-primary': '#000000',
        'bg-secondary': '#0a0a0a',
        'bg-card': '#121212',
        'border': '#1e1e1e',
        'success': '#FFD700',
        'danger': '#ff4444',
      }
    },
  },
  plugins: [],
}
