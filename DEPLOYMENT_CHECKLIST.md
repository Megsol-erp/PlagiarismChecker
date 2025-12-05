# 🚀 Railway Deployment Checklist

## ✅ Environment Variables to Add in Railway

Go to: **Railway Dashboard → PlagiarismChecker → Variables**

Add these variables one by one:

### 1. DATABASE_URL (Auto-configured)
```
${{ Postgres.DATABASE_URL }}
```
✅ Already connected! Railway shows: `postgresql://postgres:xEmGwpuNlUxFJSmIXfTtSLmtGqzRDZHG@gondola.proxy.rlwy.net:22683/railway`

### 2. GROQ_API_KEY (You already added this)
```
gsk_YOUR_GROQ_API_KEY_HERE
```
✅ Already set in Railway!

### 3. SECRET_KEY (⚠️ Generate a new one for production!)
```bash
# Run this command to generate a secure key:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output: 8K7vN2mP9wQ5xR3tY6uZ8aB1cD4eF7gH9jK2lM5nP8qR
```
Copy the output and add as `SECRET_KEY` in Railway

### 4. JWT_SECRET_KEY (⚠️ Generate a different one!)
```bash
# Run this again for a DIFFERENT key:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output: 3xY9zA2bC5dE8fG1hJ4kL7mN0pQ3rS6tU9vW2xY5zA8b
```
Copy the output and add as `JWT_SECRET_KEY` in Railway

### 5. ADMIN_EMAIL
```
admin@resgov.org
```
Use your actual admin email

### 6. ADMIN_PASSWORD
```
YourSecurePassword123!
```
⚠️ **IMPORTANT**: Use a strong password, not "admin123"!

### 7. FLASK_ENV (Optional - Railway auto-detects production)
```
production
```

---

## 📋 Deployment Steps

### Step 1: Generate Secure Keys
```bash
echo "SECRET_KEY:"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
echo ""
echo "JWT_SECRET_KEY:"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Add All Variables to Railway
1. Go to your Railway project
2. Click on **PlagiarismChecker** service
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add each variable from the list above

### Step 3: Push Code to GitHub
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 4: Railway Auto-Deploys
- Railway will detect the push and start building
- Wait 2-4 minutes for build to complete
- Check build logs for any errors

### Step 5: Run Database Migration
After first successful deployment:

**Option A: Using Railway CLI**
```bash
# Install Railway CLI if not already installed
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migration
railway run python run_migration.py
```

**Option B: Using direct psql connection**
```bash
# Connect to Railway database
PGPASSWORD=xEmGwpuNlUxFJSmIXfTtSLmtGqzRDZHG psql -h gondola.proxy.rlwy.net -U postgres -p 22683 -d railway

# Then run SQL from run_migration.py manually, or upload and run the script
```

### Step 6: Get Your Deployment URL
1. In Railway dashboard, go to **Settings** tab
2. Under **Domains**, you'll see your Railway URL
3. Example: `https://plagiarismchecker-production.up.railway.app`

### Step 7: Update Frontend API URLs
In your HTML files, update the `API_URL`:

**Files to update:**
- `static/index.html`
- `static/admin.html`
- `static/candidate.html`
- `static/exam.html`
- `static/apply.html`

**Change from:**
```javascript
const API_URL = 'http://192.168.29.133:5000/api';
```

**To:**
```javascript
const API_URL = 'https://your-app-name.up.railway.app/api';
```

### Step 8: Test the Deployment
1. Visit: `https://your-app-name.up.railway.app/static/index.html`
2. Login as admin with your `ADMIN_EMAIL` and `ADMIN_PASSWORD`
3. Create a test exam
4. Test candidate application at `/static/apply.html`

---

## 🔍 Verification Checklist

- [ ] PostgreSQL database connected in Railway
- [ ] All 6-7 environment variables added
- [ ] Code pushed to GitHub
- [ ] Build completed successfully (check Railway logs)
- [ ] Database migration completed
- [ ] Frontend API_URL updated with Railway domain
- [ ] Admin login works
- [ ] Candidate application form works
- [ ] Exam creation works
- [ ] Exam assignment works
- [ ] Screen recording and proctoring features work

---

## 🐛 Troubleshooting

### Build fails with Pillow error
✅ **Fixed!** Updated `requirements.txt` with Pillow 10.4.0

### Database connection error
- Check that `DATABASE_URL` variable is set to `${{ Postgres.DATABASE_URL }}`
- Verify PostgreSQL service is running (should show "Online")

### 502 Bad Gateway
- Check Railway logs: **Deployments** tab → Click latest deployment → **View Logs**
- Look for Python errors or startup issues
- Ensure PORT is not hardcoded (Railway provides it automatically)

### Static files not loading
- Ensure files are committed to Git
- Update API_URL in all HTML files to Railway domain
- Check CORS settings in `app.py`

### Admin can't login
- Check `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables
- Look for admin creation message in Railway logs
- Database migration might not have run

---

## 📊 Post-Deployment

### Monitor Your App
- **Logs**: Railway Dashboard → Deployments → View Logs
- **Metrics**: Railway Dashboard → Metrics tab
- **Database**: Railway Dashboard → Postgres → Database tab

### Custom Domain (Optional)
1. Go to Railway Dashboard → Settings
2. Under **Domains**, click **Add Custom Domain**
3. Follow DNS configuration instructions
4. Update `API_URL` in frontend files

---

## 🎯 Quick Start Commands

```bash
# Generate secure keys
echo "Copy these to Railway Variables:"
echo ""
echo "SECRET_KEY:"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
echo ""
echo "JWT_SECRET_KEY:"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Push to GitHub (Railway auto-deploys)
git add .
git commit -m "Deploy to Railway"
git push origin main

# Run migration after deployment
railway login
railway link
railway run python run_migration.py
```

---

## ✅ Environment Variables Summary

| Variable | Value | Status |
|----------|-------|--------|
| DATABASE_URL | `${{ Postgres.DATABASE_URL }}` | ✅ Auto-configured |
| GROQ_API_KEY | `gsk_1C6D...` | ✅ Already added |
| SECRET_KEY | Generate with command above | ⚠️ **Need to add** |
| JWT_SECRET_KEY | Generate with command above | ⚠️ **Need to add** |
| ADMIN_EMAIL | `admin@resgov.org` | ⚠️ **Need to add** |
| ADMIN_PASSWORD | Strong password | ⚠️ **Need to add** |
| FLASK_ENV | `production` | ⏭️ Optional |

**Next Step**: Generate and add the 4 missing variables in Railway! 🚀
