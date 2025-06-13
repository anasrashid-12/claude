/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
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
  important: true, // ✔ Helps avoid Polaris conflict
};
