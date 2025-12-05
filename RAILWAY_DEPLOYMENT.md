# ResGov - Railway Deployment Guide

## Fixed Issues

1. **Updated Pillow**: Changed from 10.1.0 to 10.4.0 for Python 3.13 compatibility
2. **Updated opencv-python**: Changed to `opencv-python-headless` 4.10.0.84 (required for serverless environments)
3. **Updated numpy**: Changed to 1.26.4 for better compatibility
4. **Added version numbers**: Fixed `pyopenssl` version and `bcrypt` version
5. **Python runtime**: Set to Python 3.11.9 for stability

## Deployment Steps on Railway

### 1. Prerequisites
- GitHub account with your code pushed
- Railway account (sign up at https://railway.app/)

### 2. Create Railway Project

1. Go to https://railway.app/ and login
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `Megsol-erp/PlagiarismChecker`
5. Railway will automatically detect the configuration

### 3. Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a `DATABASE_URL` variable

### 4. Configure Environment Variables

In Railway project settings, add these variables:

```env
SECRET_KEY=your-super-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this
GROQ_API_KEY=your-groq-api-key-here
ADMIN_EMAIL=admin@resgov.org
ADMIN_PASSWORD=your-secure-admin-password
```

**Important**: 
- Generate strong random keys for `SECRET_KEY` and `JWT_SECRET_KEY`
- Keep `GROQ_API_KEY` from your .env file
- `DATABASE_URL` is automatically set by Railway's PostgreSQL service

### 5. Deploy

1. Railway will automatically deploy when you push to GitHub
2. Wait for the build to complete (2-3 minutes)
3. Click on your deployment to get the public URL

### 6. Run Database Migration

After first deployment, you need to initialize the database:

**Option A: Using Railway CLI**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migration
railway run python run_migration.py
```

**Option B: Using Railway Dashboard**
1. Go to your service in Railway dashboard
2. Open "Settings" → "Service Variables"
3. Add a one-time deployment command in the dashboard or manually connect to the database
4. Use the provided connection string to run migrations locally

### 7. Update Frontend URLs

After deployment, update the `API_URL` in all your HTML files to point to your Railway URL:

In `static/admin.html`, `static/candidate.html`, `static/exam.html`, `static/apply.html`, `static/index.html`:

```javascript
// Change from:
const API_URL = 'http://192.168.29.133:5000/api';

// To your Railway URL:
const API_URL = 'https://your-app-name.railway.app/api';
```

### 8. Verify Deployment

1. Visit your Railway URL: `https://your-app-name.railway.app/static/index.html`
2. Try logging in as admin
3. Create a test exam
4. Test the candidate application flow

## Files Created for Railway

- **Procfile**: Tells Railway how to start the app with Gunicorn
- **runtime.txt**: Specifies Python 3.11.9
- **railway.json**: Railway-specific configuration
- **nixpacks.toml**: Build configuration for Railway's Nixpacks

## Troubleshooting

### Build Failures
- Check Railway build logs for specific errors
- Ensure all environment variables are set
- Verify requirements.txt has updated package versions

### Database Connection Issues
- Ensure PostgreSQL service is running in Railway
- Check that `DATABASE_URL` environment variable is set
- Run the migration script after first deployment

### Static Files Not Loading
- Ensure your frontend API_URL points to your Railway domain
- Check CORS settings in app.py
- Verify static files are committed to Git

### 502 Bad Gateway
- Check Railway logs for Python errors
- Ensure Gunicorn is starting properly
- Verify PORT environment variable is being used

## Monitoring

- Check Railway logs: Dashboard → Your Service → Logs
- Monitor resource usage: Dashboard → Your Service → Metrics
- Set up alerts for downtime in Railway settings

## Scaling (If Needed)

Railway auto-scales based on usage. For manual scaling:
1. Go to your service settings
2. Adjust "Replicas" count
3. Increase memory/CPU limits if needed

## Support

For issues:
- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Create an issue in your repository
