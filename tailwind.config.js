/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'lotto': {
          'purple': '#6B21A8',
          'purple-dark': '#4C1D95',
          'purple-light': '#A855F7',
          'gold': '#D97706',
          'gold-light': '#FCD34D',
          'blue': '#1E3A5F',
          'blue-dark': '#0F172A',
        },
        'ball': {
          'yellow': '#FFC107',
          'blue': '#2196F3',
          'red': '#F44336',
          'gray': '#9E9E9E',
          'green': '#4CAF50',
        }
      },
      fontFamily: {
        'display': ['Pretendard Variable', 'system-ui', 'sans-serif'],
      },
    }
  },
  plugins: [],
}
