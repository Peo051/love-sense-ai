import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        body: ['var(--font-body)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['var(--font-display)', 'serif'],
        mono: ['var(--font-mono)', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        artistic: {
          primary: '#3B82F6',
          secondary: '#8B5CF6',
          success: '#16A34A',
          warning: '#D97706',
          danger: '#DC2626',
          surface: '#FFFFFF',
          text: '#111827',
          ink: '#0F172A',
          muted: '#64748B',
          blueSoft: '#DBEAFE',
          purpleSoft: '#EDE9FE',
          roseSoft: '#FFE4E6',
          warm: '#FFF7ED',
        },
        pink: {
          600: '#db2777',
          700: '#be185d',
        },
      },
    },
  },
  plugins: [],
}
export default config
