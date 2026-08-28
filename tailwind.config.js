/** Build-time only — the site ships the compiled assets/tailwind.css */
module.exports = {
  content: ["./*.html", "./papers/*.html", "./scripts/build_papers.py"],
  theme: {
    extend: {
      colors: {
        'brand-green': '#00FF41',
        'archival-paper': 'rgb(var(--paper-rgb) / <alpha-value>)',
        'archival-ink': 'rgb(var(--ink-rgb) / <alpha-value>)',
        'surface': 'rgb(var(--surface-rgb) / <alpha-value>)',
        'panel': 'rgb(var(--panel-rgb) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['"Libre Baskerville"', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
};
