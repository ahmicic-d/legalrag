/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1C2530",
        paper: "#F5F6F8",
        surface: "#FFFFFF",
        line: "#E2E6EC",
        primary: {
          DEFAULT: "#234E70",
          dark: "#18374F",
          light: "#EAF1F7",
        },
        bronze: {
          DEFAULT: "#9A7B2F",
          light: "#F5EEDC",
        },
        confidence: {
          high: "#1E7F4F",
          medium: "#B07D18",
          low: "#B3402E",
        },
      },
      fontFamily: {
        display: ['"Source Serif 4"', "Georgia", "serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
