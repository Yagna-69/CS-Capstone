# FXTrade

Forex trading platform built with Vue 3, Python FastAPI, and Supabase.

## Features

- Real-time forex currency tracking
- Interactive price charts (TradingView)
- User authentication (login/signup)
- Responsive dark theme UI
- News and AI insights (coming soon)
- **Automated CI/CD deployment with GitHub Actions**

## Tech Stack

- **Frontend:** Vue 3, Tailwind CSS, TradingView Lightweight Charts
- **Backend:** Python FastAPI, Supabase (PostgreSQL)
- **Deployment:** Docker, Google Cloud Platform

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
./setup.sh
```

This will automatically:
- Set up Python virtual environment
- Install all dependencies
- Create environment files from templates

Then edit `backend/.env` with your Supabase credentials and run:

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Option 2: Docker

```bash
# Make sure backend/.env exists with Supabase credentials
docker-compose up --build
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

### Option 3: Manual Setup

See [HELP.md](./help.md) for detailed manual setup instructions.

## Supabase Setup

1. Create a project at https://app.supabase.com
2. Go to Settings > API
3. Copy your Project URL and anon key
4. Add them to `backend/.env`:
   ```env
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   ```

## Documentation

- [README.md](./README.md) - This file (quick start)
- [HELP.md](./help.md) - Comprehensive setup and deployment guide
- [CI_CD_SETUP.md](./CI_CD_SETUP.md) - GitHub Actions automated deployment
- [Frontend README](./frontend/README.md) - Frontend-specific details

## Project Structure

```
CapstoneProject/
├── backend/              # FastAPI backend
│   ├── main.py          # Server entry point
│   ├── routes.py        # API endpoints
│   ├── database.py      # Supabase client
│   └── Dockerfile       # Backend container
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── views/      # Pages
│   │   ├── components/ # UI components
│   │   └── services/   # API calls
│   └── Dockerfile      # Frontend container
├── docker-compose.yml   # Local development setup
└── setup.sh            # Automated setup script
```

## License

MIT
