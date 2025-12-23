export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        'neon-blue': '#00f0ff',
        'neon-purple': '#bf00ff',
        'neon-pink': '#ff006e',
        'dark-bg': '#0a0a0f',
        'darker-bg': '#050508',
        'card-bg': 'rgba(20, 20, 35, 0.8)'
      },
      fontFamily: {
        'orbitron': ['Orbitron', 'sans-serif'],
        'rajdhani': ['Rajdhani', 'sans-serif']
      },
      animation: {
        'twinkle': 'twinkle 3s infinite',
        'grid-move': 'gridMove 20s linear infinite',
        'logo-glow': 'logoGlow 3s ease-in-out infinite',
        'banner-pulse': 'bannerPulse 10s ease-in-out infinite',
        'particle-float': 'particleFloat 15s linear infinite',
        'badge-pulse': 'badgePulse 2s ease-in-out infinite'
      },
      keyframes: {
        twinkle: {
          '0%, 100%': { opacity: 0.3 },
          '50%': { opacity: 1 }
        },
        gridMove: {
          '0%': { transform: 'perspective(500px) rotateX(60deg) translateY(0)' },
          '100%': { transform: 'perspective(500px) rotateX(60deg) translateY(50px)' }
        },
        logoGlow: {
          '0%, 100%': { filter: 'drop-shadow(0 0 10px #00f0ff)' },
          '50%': { filter: 'drop-shadow(0 0 20px #bf00ff)' }
        },
        bannerPulse: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' }
        },
        particleFloat: {
          '0%': { transform: 'translateY(100vh) rotate(0deg)', opacity: 0 },
          '10%': { opacity: 0.6 },
          '90%': { opacity: 0.6 },
          '100%': { transform: 'translateY(-100vh) rotate(720deg)', opacity: 0 }
        },
        badgePulse: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(255, 0, 110, 0.5)' },
          '50%': { boxShadow: '0 0 20px rgba(255, 0, 110, 0.8)' }
        }
      }
    }
  },
  plugins: [
    require('tailwindcss-animate')
  ]
};
