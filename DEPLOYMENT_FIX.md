# Production Deployment Fix - Mixed Content Error

## Problem
The deployed frontend is making HTTP requests to the backend, but the frontend is served over HTTPS, causing browsers to block the requests.

## Root Cause
The GitHub Actions workflow uses a secret called `BACKEND_URL` to generate the `.env.production` file at build time. This secret is currently set to HTTP instead of HTTPS.

## Solution

### Step 1: Update GitHub Secret
1. Go to: https://github.com/Yagna-69/CS-Capstone/settings/secrets/actions
2. Find the secret named `BACKEND_URL`
3. Click **Edit** or **Update**
4. Change the value from:
   ```
   http://forextrade-18082002171.us-central1.run.app
   ```
   to:
   ```
   https://forextrade-18082002171.us-central1.run.app
   ```
   (Change `http` to `https`)

### Step 2: Trigger Rebuild
After updating the secret, you need to rebuild the frontend. You can either:

**Option A: Merge the PR**
- Merge PR #6 into main
- This will automatically trigger the `deploy-frontend.yml` workflow
- The new build will use HTTPS

**Option B: Manual Trigger**
- Go to: https://github.com/Yagna-69/CS-Capstone/actions
- Find the "Deploy Frontend to Cloud Run" workflow
- Click "Run workflow" on the main branch (after merging)

### Step 3: Verify
After deployment completes, check the deployed site and verify:
- No more "Mixed Content" errors in console
- News loads correctly
- API calls show HTTPS in Network tab

## Technical Details

The workflow file (`.github/workflows/deploy-frontend.yml`) line 40-41 creates the env file:
```yaml
- name: Create production env file
  run: |
    echo "VITE_API_URL=${{ secrets.BACKEND_URL }}" > ./frontend/.env.production
```

This happens at **build time**, so changing the secret requires a new deployment to take effect.

## Reddit 403 Error (Separate Issue)

The Reddit API 403 error is a different issue - Cloud Run IPs are often rate-limited or blocked by Reddit. This is expected and requires either:
- Better request headers and rate limiting
- Alternative data source
- Accepting it as a limitation for production (works fine locally)
