# CI/CD Setup Guide

This project uses GitHub Actions to automatically deploy to Google Cloud Run when you push code.

## Workflows

### 1. `ci.yml` - Continuous Integration
- Runs on every push and pull request
- Tests backend (Python linting)
- Tests frontend (build check)

### 2. `deploy-backend.yml` - Backend Deployment
- Triggers when backend code changes
- Builds Docker image
- Pushes to Artifact Registry
- Deploys to Cloud Run

### 3. `deploy-frontend.yml` - Frontend Deployment
- Triggers when frontend code changes
- Builds Docker image with production config
- Pushes to Artifact Registry
- Deploys to Cloud Run

## Setup Instructions

### 1. Create Google Cloud Service Account

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com
```

### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create fxtrade-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="FXTrade Docker images"
```

### 3. Add GitHub Secrets

Go to your GitHub repository settings: `Settings > Secrets and variables > Actions`

Add these secrets:

| Secret Name | Value | How to Get |
|------------|-------|------------|
| `GCP_PROJECT_ID` | Your GCP project ID | From GCP Console |
| `GCP_SA_KEY` | Service account JSON key | Content of `key.json` file |
| `SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard > Settings > API |
| `SUPABASE_KEY` | Your Supabase anon key | Supabase Dashboard > Settings > API |
| `BACKEND_URL` | Your backend URL | After first backend deploy: `https://fxtrade-backend-xxx.run.app` |

**Important:** Delete `key.json` after adding to GitHub secrets!

```bash
rm key.json
```

### 4. Enable Required GCP APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 5. First Deployment

For the first deployment, you need to deploy manually to get the backend URL:

```bash
# Deploy backend first
cd backend
gcloud run deploy fxtrade-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key
```

Take note of the backend URL, then add it as `BACKEND_URL` secret in GitHub.

### 6. Test the Workflow

Push a change to trigger automatic deployment:

```bash
git add .
git commit -m "Test CI/CD deployment"
git push origin main
```

Check the Actions tab on GitHub to see the deployment progress.

## How It Works

1. **You push code** to the `main` branch
2. **GitHub Actions triggers** based on which files changed:
   - Backend changes → Deploys backend only
   - Frontend changes → Deploys frontend only
   - Both → Deploys both (in parallel)
3. **Builds Docker image** with your latest code
4. **Pushes to Artifact Registry** (Google's Docker registry)
5. **Deploys to Cloud Run** automatically
6. **Updates live site** in ~2-5 minutes

## Monitoring Deployments

- **View logs:** GitHub repo → Actions tab
- **View deployments:** GCP Console → Cloud Run
- **Rollback:** Cloud Run console → Select previous revision

## Troubleshooting

### Deployment fails with authentication error
- Verify `GCP_SA_KEY` secret is correct JSON
- Check service account has required permissions

### Backend URL not found
- Deploy backend manually first
- Add the URL to `BACKEND_URL` secret

### Artifact Registry push fails
- Ensure repository exists: `gcloud artifacts repositories list`
- Check service account has `artifactregistry.admin` role

## Cost Considerations

- Cloud Run: Free tier includes 2 million requests/month
- Artifact Registry: First 0.5GB storage free
- GitHub Actions: 2,000 minutes/month free (public repos = unlimited)

## Security Notes

- Never commit `key.json` or secrets to git
- Service account has minimal required permissions
- Secrets are encrypted in GitHub
- Consider adding branch protection rules
