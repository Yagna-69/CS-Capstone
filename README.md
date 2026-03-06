# FXTrade

A forex trading platform built with Vue 3, FastAPI, and Supabase.

## Features

- Live forex ticker banner with real-time rates (powered by yfinance)
- Currency exchange at live market rates
- User-to-user currency transfers by email
- Portfolio management — deposit and withdraw currencies
- Detailed transaction history (type, amounts, sender/receiver, TX ID, timestamp)
- User authentication (signup / login / logout via Supabase)
- Responsive dark theme UI
- Automated CI/CD deployment with GitHub Actions

## Tech Stack

- **Frontend:** Vue 3, Vite, Pinia, Tailwind CSS
- **Backend:** Python FastAPI, yfinance (live rates), Supabase (PostgreSQL + Auth)
- **Deployment:** Docker, Google Cloud Platform

## Project Structure

```
CS-Capstone/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Settings (pydantic-settings)
│   ├── database.py           # Supabase client helpers
│   ├── auth.py               # JWT / get_current_user dependency
│   ├── models.py             # Pydantic request/response models
│   ├── forex_service.py      # Live rate fetching via yfinance (cached)
│   ├── routes/
│   │   ├── auth.py           # POST /api/auth/login|signup|logout, GET /api/auth/me
│   │   ├── portfolio.py      # GET/POST /api/portfolio/, deposit, withdraw
│   │   ├── trading.py        # POST /api/trade/exchange|transfer, GET /api/trade/history|rate
│   │   ├── forex.py          # GET /api/forex/rate/{from}/{to}, GET /api/forex/rates
│   │   ├── preferences.py    # GET/PUT /api/preferences/
│   │   ├── news.py           # GET /api/news/
│   │   └── insight.py        # GET /api/insight/
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/            # DashboardView, TradingView, LoginView, SignupView, LandingView
│   │   ├── components/       # UI components
│   │   ├── stores/           # Pinia stores (auth, portfolio)
│   │   └── services/api.js   # Axios client + all API helpers
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
└── requirements.txt          # Root-level pip requirements (mirrors backend/)
```

## Quick Start

### Manual (recommended for development)

**Prerequisites:** Python 3.11+, Node 18+

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
cp .env.example .env            # fill in your Supabase credentials
uvicorn main:app --reload --port 8000

# 2. Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env.local      # set VITE_API_URL=http://localhost:8000
npm run dev
```

Frontend runs at http://localhost:5173, backend at http://localhost:8000.

### Docker

```bash
# Copy and fill in backend/.env first
cp backend/.env.example backend/.env

docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

> Note: `VITE_API_URL` is set to `http://backend:8000` inside Docker (service-to-service networking). If you need to change the backend URL for local dev, edit `frontend/.env.local`.

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (required for admin operations) |
| `BROKER_USER_ID` | UUID of the broker Supabase auth user (exchange counterparty) |
| `FRONTEND_URL` | Frontend origin for CORS (default: `http://localhost:5173`) |
| `GEMINI_API_KEY` | Reserved for future AI insight feature |

## Supabase Setup

1. Create a project at https://app.supabase.com
2. Go to **Settings > API** — copy the Project URL, anon key, and service role key
3. Required tables:
   - `portfolio` — columns: `id` (uuid, FK auth.users), `currency-ticker-symbol` (text), `amount` (numeric)
   - `transaction-log` — columns: `transaction_id` (uuid PK), `sender_id`, `receiver_id`, `sender_currency_ticker_symbol`, `receiver_currency_ticker_symbol`, `sender-amount`, `receiver-amount`, `timestamp`, `type` (enum: EXCHANGE, DEPOSIT, WITHDRAW, OTHER)
4. Create a regular Supabase auth user to act as the broker/exchange account and set its UUID as `BROKER_USER_ID`

## API Routes

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/signup` | Signup |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Current user |
| GET | `/api/portfolio/` | Get holdings |
| POST | `/api/portfolio/deposit` | Deposit currency |
| POST | `/api/portfolio/withdraw` | Withdraw currency |
| POST | `/api/trade/exchange` | Exchange currencies at live rate |
| POST | `/api/trade/transfer` | Transfer currency to another user by email |
| GET | `/api/trade/history` | Transaction history |
| GET | `/api/trade/rate` | Live rate (no trade executed) |
| GET | `/api/forex/rate/{from}/{to}` | Single pair live rate |
| GET | `/api/forex/rates` | Multiple pairs (default: 10 standard pairs) |

## License

MIT
