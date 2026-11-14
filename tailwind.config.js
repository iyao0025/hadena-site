/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./showcase/**/*.py",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        hadena: {
          blue: "#304B9B",
          dark: "#0F172A",
          deep: "#0A192F",
          grey: "#423E3C",
          light: "#F8FAFC",
          amber: "#F59E0B",
          cyan: "#06B6D4",
          sky: "#38BDF8"
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        heading: ['Outfit', '"Plus Jakarta Sans"', 'sans-serif']
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        hadena: {
          "primary": "#304B9B",
          "primary-content": "#ffffff",
          "secondary": "#423E3C",
          "secondary-content": "#ffffff",
          "accent": "#F59E0B",
          "accent-content": "#0F172A",
          "neutral": "#0F172A",
          "neutral-content": "#ffffff",
          "base-100": "#ffffff",
          "base-200": "#F8FAFC",
          "base-300": "#E2E8F0",
          "base-content": "#1E293B",
          "info": "#0284C7",
          "success": "#16A34A",
          "warning": "#D97706",
          "error": "#DC2626",
        },
      },
      "light",
    ],
    defaultTheme: "hadena",
  },
}

