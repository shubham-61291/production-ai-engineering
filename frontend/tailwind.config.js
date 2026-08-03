/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        magnetar: {
          dark: '#05070f',
          card: 'rgba(15, 23, 42, 0.75)',
          cyan: '#00f2fe',
          purple: '#7928ca',
          pink: '#ff0080',
          accent: '#38bdf8'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'JetBrains Mono', 'monospace']
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 15px rgba(56, 189, 248, 0.3)' },
          '100%': { boxShadow: '0 0 30px rgba(121, 40, 202, 0.6)' },
        }
      }
    },
  },
  plugins: [],
}
