/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        emeraldCorp: {
          950: "#052e24"
        }
      }
    }
  },
  plugins: []
};

