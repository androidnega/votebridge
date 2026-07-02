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
          muted: "#F9FAFB",
        },
        shell: {
          sidebar: "#F3F4F6",
          "sidebar-border": "#E5E7EB",
          "sidebar-text": "#374151",
          "sidebar-icon": "#6B7280",
          "sidebar-hover": "#E8F5EE",
          active: "#E8F5EE",
          accent: "#166534",
        },
        success: {
          50: "#F0FDF4",
          100: "#DCFCE7",
          200: "#BBF7D0",
          600: "#16A34A",
          700: "#15803D",
          800: "#166534",
        },
        warning: {
          50: "#FFFBEB",
          100: "#FEF3C7",
          200: "#FDE68A",
          600: "#D97706",
          700: "#B45309",
          800: "#92400E",
        },
        danger: {
          50: "#FEF2F2",
          100: "#FEE2E2",
          200: "#FECACA",
          600: "#DC2626",
          700: "#B91C1C",
          800: "#991B1B",
        },
        info: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          200: "#BFDBFE",
          600: "#2563EB",
          700: "#1D4ED8",
          800: "#1E40AF",
        },
        border: {
          DEFAULT: "#E5E7EB",
        },
        ink: {
          primary: "#1F2937",
          secondary: "#6B7280",
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
