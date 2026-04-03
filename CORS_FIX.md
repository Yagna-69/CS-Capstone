# CORS Configuration for Production

## Problem
The backend is rejecting requests from the production frontend due to CORS (Cross-Origin Resource Sharing) policy.

## Solution

You need to add GitHub Secrets for the backend deployment to allow the production frontend URL.

### Required GitHub Secrets

Go to: https://github.com/Yagna-69/CS-Capstone/settings/secrets/actions

Add or update these secrets:

1. **FRONTEND_URL** (if not exists)
   - Value: `https://cs-capstone-git-18082002171.us-central1.run.app`
   - Or your main production frontend URL

2. **ADDITIONAL_ORIGINS** (new)
   - Value: Comma-separated list of additional allowed origins
   - Example: `https://cs-capstone-git-18082002171.us-central1.run.app,https://cs-capstone.us-central1.run.app`
   - This allows preview deployments and multiple frontend URLs

3. **SUPABASE_SERVICE_ROLE_KEY** (if not exists)
   - Value: Your Supabase service role key

4. **NEWSAPI_KEY** (if not exists)
   - Value: Your NewsAPI key

### Alternative: Wildcard CORS (Development Only)

For testing, you could temporarily allow all origins by setting:
```
FRONTEND_URL=*
```

⚠️ **Warning**: Never use `*` in production with `allow_credentials=True` - it's a security risk!

### After Updating Secrets

1. Merge the PR to trigger backend deployment
2. The backend will rebuild with the new CORS configuration
3. Your frontend will be able to make API calls

### Environment Variables Structure

**Local (.env):**
```
FRONTEND_URL=http://localhost:5173
ADDITIONAL_ORIGINS=
```

**Production (GitHub Secrets → Cloud Run):**
```
FRONTEND_URL=https://your-main-frontend.run.app
ADDITIONAL_ORIGINS=https://preview-1.run.app,https://preview-2.run.app
```
