/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "risk-on": "#16a34a",
        "risk-neutral": "#ca8a04",
        "risk-off": "#dc2626",
      },
    },
  },
  plugins: [],
};
