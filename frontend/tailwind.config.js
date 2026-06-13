/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: {
          DEFAULT: "#FAF6EE",
          dark: "#F1E9D2",
          border: "#E8DFC9",
        },
        sage: {
          DEFAULT: "#6B8E5A",
          dark: "#4F6B43",
          light: "#A8C190",
        },
        terracotta: "#C7613A",
        gold: "#D4A24C",
        soil: {
          DEFAULT: "#3D2E20",
          light: "#6B5742",
        },
      },
      fontFamily: {
        display: ["'Plus Jakarta Sans'", "system-ui", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
      },
      borderRadius: { bubble: "18px" },
      boxShadow: {
        soft: "0 2px 12px rgba(61, 46, 32, 0.06)",
        lift: "0 8px 24px rgba(61, 46, 32, 0.10)",
      },
      maxWidth: { conv: "680px" },
    },
  },
  plugins: [],
};
