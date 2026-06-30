/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,jsx}"],
    theme: {
      extend: {
        colors: {
          ink: '#0F1115',
          paper: '#FAFAF7',
          graph: {
            50: '#F3F1FF',
            100: '#E5DFFF',
            400: '#8B7CF6',
            500: '#6D5BF0',
            600: '#5640E0',
            900: '#231966',
          },
          moss: { 400: '#6FA888', 500: '#4D8A6C' },
          rust: { 400: '#D4795A', 500: '#C2603F' },
        },
        fontFamily: {
          display: ['"Fraunces"', 'serif'],
          body: ['"Inter"', 'sans-serif'],
          mono: ['"JetBrains Mono"', 'monospace'],
        },
      },
    },
    plugins: [],
  }