/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-primary': '#0A0A0F',
        'brand-secondary': '#12121A',
        'brand-card': '#1A1A2E',
        'brand-accent': '#E50914',
        'brand-accent-hover': '#FF6B6B',
        'brand-text': '#FFFFFF',
        'brand-muted': '#A0A0B0',
        'brand-placeholder': '#606070',
        'brand-border': '#2A2A3E',
        'brand-success': '#00D4AA',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
