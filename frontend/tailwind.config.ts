import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Paleta "Baía de Maputo": navy profundo do oceano ao entardecer + dourado do sol + teal da maré
        ocean: {
          950: "#081420",
          900: "#0B1B2B",
          800: "#12283D",
          700: "#1B3A54",
          600: "#274F6E",
        },
        tide: {
          400: "#3FCBAC",
          500: "#1FA98C",
          600: "#158571",
        },
        sunset: {
          300: "#F0C088",
          400: "#E0A458",
          500: "#C98A3E",
        },
        sand: {
          100: "#F5F1E8",
          200: "#E8E1D0",
          400: "#B8AF9C",
        },
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "serif"],
        body: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backgroundImage: {
        "wallet-card": "linear-gradient(135deg, #12283D 0%, #0B1B2B 55%, #081420 100%)",
        "sunset-line": "linear-gradient(90deg, #E0A458 0%, #1FA98C 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
