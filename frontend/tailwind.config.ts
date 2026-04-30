import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        field: {
          950: "#020c04",
          900: "#041a07",
          800: "#072b0c",
          700: "#0d4018",
          600: "#166534",
          500: "#16a34a",
          400: "#4ade80",
          300: "#86efac",
        },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
