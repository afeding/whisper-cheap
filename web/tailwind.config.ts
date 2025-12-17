import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        accent: '#00ff88',
        'accent-hover': '#00dd77',
        'accent-dim': '#00aa55',
        'bg-primary': '#0a0a0a',
        'bg-secondary': '#111111',
        'bg-card': '#161616',
        'bg-input': '#0e0e0e',
        'border-default': '#222222',
        'border-hover': '#333333',
        'text-primary': '#e5e5e5',
        'text-secondary': '#888888',
        'text-dim': '#555555',
      },
    },
  },
  plugins: [],
}

export default config
