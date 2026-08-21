/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        judicial: {
          900: '#0B1325', // Deepest judicial navy
          800: '#111C35', // Card background / dark slate
          700: '#1C2B4B', // Border / elevated panel
          600: '#2A3E68', // Subtle highlight
          500: '#3B5284',
          accent: '#D4AF37', // Gold emblem accent
          gold: '#E6C200',
          emerald: '#10B981', // High relevance badge
          badge: '#1E293B',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'Georgia', 'serif']
      }
    },
  },
  plugins: [],
}
