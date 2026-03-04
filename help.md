# FXTrade

Forex trading platform using Vue 3, Python FastAPI, and Supabase.

## Tech Stack

- Frontend: Vue 3, Tailwind CSS, TradingView Charts
- Backend: Python FastAPI
- Database: Supabase (PostgreSQL)

## Quick Setup

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` with your Supabase credentials:
```env
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

### Frontend
```bash
cd frontend
npm install
```

## Run Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**URLs:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Get Supabase Credentials

1. Visit https://app.supabase.com
2. Select your project
3. Go to Settings > API
4. Copy "Project URL" and "anon key"
5. Paste into `backend/.env`

## Deploy to Google Cloud Platform

### Initial Setup
```bash
gcloud auth login
gcloud projects create my-fxtrade-project --set-as-default
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### Deploy Backend
```bash
cd backend
gcloud run deploy fxtrade-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key
```

Note the backend URL from the output.

### Deploy Frontend
```bash
cd frontend
echo "VITE_API_URL=https://fxtrade-backend-xxx.run.app" > .env.production
gcloud run deploy fxtrade-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Update CORS
Add your frontend URL to `backend/main.py`:
```python
allow_origins=[
    "http://localhost:5173",
    "https://fxtrade-frontend-xxx.run.app"
]
```

Then redeploy backend:
```bash
cd backend
gcloud run deploy fxtrade-backend --source .
```

## Project Structure

```
CapstoneProject/
├── backend/           # Python FastAPI
│   ├── main.py       # Server entry point
│   ├── routes.py     # API endpoints
│   ├── database.py   # Supabase client
│   └── config.py     # Configuration
├── frontend/         # Vue 3 application
│   └── src/
│       ├── views/    # Pages
│       ├── components/   # UI components
│       └── services/     # API calls
└── README.md         # This file
```

## Available Routes

- `/` - Landing page
- `/login` - Login/signup
- `/dashboard` - Dashboard
- `/trading` - Trading interface
- `/settings` - Settings
- `/ai` - AI assistant
- `/demo` - Demo page (with charts)
- `/about` - About page

## Troubleshooting

**Backend won't start:**
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`
- Check `.env` file exists with Supabase credentials

**Frontend won't start:**
- Reinstall: `npm install`
- Check Node version: `node --version` (need 18+)

**CORS errors in production:**
- Update `allow_origins` in `backend/main.py`
- Redeploy backend

## Notes

- GCP auto-detects and builds your app (no Docker needed)
- Cloud Run free tier: 2M requests/month
- Keep `.env` files secret (never commit)
