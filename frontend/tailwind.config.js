/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Custom breakpoints (using Tailwind defaults, but explicitly defined for clarity)
      screens: {
        'sm': '640px',   // Small tablets
        'md': '768px',   // Tablets, small desktops
        'lg': '1024px',  // Desktops
        'xl': '1280px',  // Large desktops
        '2xl': '1536px', // Extra large desktops
      },
    },
  },
  plugins: [],
}

