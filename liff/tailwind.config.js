/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#FFC940',
        'primary-light': '#FFE58F',
        'primary-dark': '#FAAD14',
        'background': '#FFFBE6',
        'text-primary': '#595959',
        'text-secondary': '#8C8C8C',
        'border': '#D9D9D9',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      }
    },
    fontFamily: {
      'sans': ['Noto Sans TC', 'sans-serif'],
    },
  },
  plugins: [],
} 