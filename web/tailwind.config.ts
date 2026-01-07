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
        sans: ['Manrope', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Sora', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        accent: '#00ff88',
        'accent-hover': '#00dd77',
        'accent-dim': '#00aa55',
        'bg-primary': '#0a0a0a',
        'bg-secondary': '#0f0f0f',
        'bg-card': '#141414',
        'bg-elevated': '#1a1a1a',
        'border-default': '#1f1f1f',
        'border-hover': '#2a2a2a',
        'text-primary': '#f0f0f0',
        'text-secondary': '#8a8a8a',
        'text-dim': '#5a5a5a',
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
      },
      transitionTimingFunction: {
        'out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}

export default config
