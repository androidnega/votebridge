/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../backend/templates/**/*.html",
    "./index.html",
    "./src/**/*.{js,vue,css}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#1E5F46",
          hover: "#184C38",
          50: "#E8F3EF",
          100: "#C5E0D6",
          200: "#9CC9B8",
          300: "#73B29A",
          400: "#4A9B7C",
          500: "#2E8562",
          600: "#1E5F46",
          700: "#184C38",
          800: "#123A2A",
          900: "#0C251C",
          950: "#061510",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          muted: "#F5F7F9",
        },
        success: {
          50: "#E8F5E9",
          600: "#2E7D32",
          700: "#256628",
        },
        warning: {
          50: "#FEFCE8",
          600: "#CA8A04",
          700: "#A16207",
        },
        danger: {
          50: "#FFEBEE",
          600: "#C62828",
          700: "#B71C1C",
        },
        info: {
          50: "#F0FDFA",
          600: "#0F766E",
          700: "#0D6B64",
        },
        border: {
          DEFAULT: "#E2E8F0",
        },
      },
      fontFamily: {
        sans: [
          "Inter Variable",
          "Inter",
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
      },
      spacing: {
        page: "32px",
        section: "32px",
        card: "24px",
        "input-gap": "16px",
        "button-gap": "16px",
        sidebar: "280px",
        "sidebar-collapsed": "88px",
      },
      borderRadius: {
        input: "10px",
        card: "12px",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(15 23 42 / 0.06), 0 1px 2px -1px rgb(15 23 42 / 0.06)",
      },
      height: {
        input: "48px",
        topbar: "72px",
        "table-row": "56px",
      },
      width: {
        sidebar: "280px",
        "sidebar-collapsed": "88px",
      },
      minHeight: {
        touch: "44px",
      },
      maxWidth: {
        content: "1280px",
        wide: "1600px",
        monitor: "1920px",
      },
      transitionDuration: {
        ui: "200ms",
      },
      screens: {
        xs: "475px",
      },
      gridTemplateColumns: {
        sidebar: "280px minmax(0, 1fr)",
        "sidebar-collapsed": "88px minmax(0, 1fr)",
      },
    },
  },
  safelist: [
    "lg:pl-sidebar",
    "lg:pl-sidebar-collapsed",
    "w-sidebar",
    "w-sidebar-collapsed",
    "lg:grid-cols-sidebar",
    "lg:grid-cols-sidebar-collapsed",
  ],
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
};
