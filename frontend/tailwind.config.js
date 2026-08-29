/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0A0D0B",
        surface: "#12171A",
        "surface-glass": "rgba(18, 23, 20, 0.55)",
        hairline: "#2A332E",
        ink: "#E8ECE9",
        "ink-muted": "#8B968F",
        risk: {
          low: "#4ADE80",
          moderate: "#FBBF24",
          high: "#FB923C",
          critical: "#F43F5E",
        },
        sage: "#7FB069",
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backdropBlur: {
        glass: "16px",
      },
    },
  },
  plugins: [],
};
