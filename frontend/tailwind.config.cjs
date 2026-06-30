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
        navy: {
          DEFAULT: "#1E293B",
          border: "#334155",
          muted: "#475569",
          600: "#1E293B",
          700: "#172033",
          800: "#0F172A",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          muted: "#F8FAFC",
        },
        success: {
          50: "#F0FDF4",
          600: "#16A34A",
          700: "#15803D",
        },
        warning: {
          50: "#FFFBEB",
          600: "#D97706",
          700: "#B45309",
        },
        danger: {
          50: "#FEF2F2",
          600: "#DC2626",
          700: "#B91C1C",
        },
        info: {
          50: "#EFF6FF",
          600: "#2563EB",
          700: "#1D4ED8",
        },
        border: {
          DEFAULT: "#E2E8F0",
        },
        ink: {
          primary: "#0F172A",
          secondary: "#64748B",
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
