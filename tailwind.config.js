/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'space-dark': '#0a0e1a',
        'space-blue': '#1a2332',
        'space-accent': '#3b82f6',
        'space-gold': '#fbbf24',
      },
    },
  },
  plugins: [],
}
