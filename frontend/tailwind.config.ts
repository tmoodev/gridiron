import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#080c10",
          50: "#0d1117",
          100: "#111820",
          200: "#162030",
          300: "#1a2332",
          400: "#1e2a3a",
          500: "#243044",
        },
        teal: {
          DEFAULT: "#2dd4bf",
          dim: "#14b8a6",
          bright: "#5eead4",
          muted: "#0d9488",
        },
        surface: "#0d1117",
        border: "#1a2332",
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "sans-serif"],
        mono: ['"DM Mono"', "monospace"],
        display: ['"Syne"', "system-ui", "sans-serif"],
      },
      gridTemplateColumns: {
        dashboard: "280px 1fr 320px",
      },
    },
  },
  plugins: [],
} satisfies Config;
