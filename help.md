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

## Run Locally (Without Docker)

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

**Using Docker Compose (recommended):**
```bash
# Make sure backend/.env exists first
docker-compose up --build
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

**Individual containers:**
```bash
# Backend
cd backend
docker build -t fxtrade-backend .
docker run -p 8000:8000 --env-file .env fxtrade-backend

# Frontend
cd frontend
docker build -t fxtrade-frontend .
docker run -p 3000:80 fxtrade-frontend
```

**Stop containers:**
```bash
docker-compose down
```

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
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

### Option 1: Deploy with Buildpacks (No Docker)

**Deploy Backend:**
```bash
cd backend
gcloud run deploy fxtrade-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key
```

**Deploy Frontend:**
```bash
cd frontend
echo "VITE_API_URL=https://fxtrade-backend-xxx.run.app" > .env.production
gcloud run deploy fxtrade-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 2: Deploy with Docker

**1. Create Artifact Registry repository:**
```bash
gcloud artifacts repositories create fxtrade-repo \
  --repository-format=docker \
  --location=us-central1
```

**2. Configure Docker authentication:**
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

**3. Build and push Backend:**
```bash
cd backend
docker build -t us-central1-docker.pkg.dev/my-fxtrade-project/fxtrade-repo/backend:latest .
docker push us-central1-docker.pkg.dev/my-fxtrade-project/fxtrade-repo/backend:latest

gcloud run deploy fxtrade-backend \
  --image us-central1-docker.pkg.dev/my-fxtrade-project/fxtrade-repo/backend:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key
```

**4. Build and push Frontend:**
```bash
cd frontend
echo "VITE_API_URL=https://fxtrade-backend-xxx.run.app" > .env.production
docker build -t us-central1-docker.pkg.dev/my-fxtrade-project/fxtrade-repo/frontend:latest .
docker push us-central1-docker.pkg.dev/my-fxtrade-project/fxtrade-repo/frontend:latest

gcloud run deploy fxtrade-frontend \
  --image us-central1-docker.pkg.dev/my-fxtrade-project/fxtrade-repo/frontend:latest \
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

Redeploy backend with your chosen method.

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

- Option 1 (Buildpacks): GCP auto-detects and builds your app
- Option 2 (Docker): More control over build process
- Keep `.env` files secret
- Docker Compose simplifies local development
