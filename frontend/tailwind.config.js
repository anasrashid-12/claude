/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        shopify: {
          DEFAULT: '#008060',
          dark: '#004C3F',
          light: '#C1F0D0',
        },
      },
    },
  },
  plugins: [],
  // Ensure Tailwind doesn't conflict with Polaris
  important: true,
} 