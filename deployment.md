# Deploy to GCP

## Setup

```bash
gcloud auth login
gcloud projects create my-fxtrade --set-as-default
gcloud services enable run.googleapis.com
```

## Deploy

```bash
# Backend
cd backend
gcloud run deploy fxtrade-backend --source . --region us-central1 --allow-unauthenticated --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key

# Frontend
cd frontend
echo "VITE_API_URL=https://fxtrade-backend-xxx.run.app" > .env.production
gcloud run deploy fxtrade-frontend --source . --region us-central1 --allow-unauthenticated
```

## Update CORS

Add frontend URL to `backend/main.py`:
```python
allow_origins=["http://localhost:5173", "https://fxtrade-frontend-xxx.run.app"]
```

Redeploy backend.

GCP auto-builds and deploys (no Docker needed).
