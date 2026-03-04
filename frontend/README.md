# Frontend

Vue 3 forex trading app with Tailwind CSS & TradingView Charts.

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## Structure

```
src/
├── views/        # Pages (LandingView, TradingView,     DashboardView, SettingsView, LLMView)
├── components/   # UI components (PriceChart, CurrencyCard, etc.)
├── stores/       # Pinia state management
├── services/     # API calls (api.js)
└── router/       # Routes
```

## Tech Stack

- Vue 3 (Composition API)
- Tailwind CSS (Utility-first styling)
- TradingView Lightweight Charts (Real-time price charts)
- Pinia (State management)
- Axios (HTTP client)

## Scripts

- `npm run dev` - Dev server
- `npm run build` - Production build
- `npm run preview` - Preview build
