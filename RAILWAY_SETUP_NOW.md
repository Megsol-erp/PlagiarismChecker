# 🚀 RAILWAY DEPLOYMENT - FINAL INSTRUCTIONS

## ✅ Status: Ready to Deploy!

**Code pushed to GitHub:** https://github.com/Megsol-erp/PlagiarismChecker

Railway will now automatically rebuild with the fixed dependencies.

---

## 📝 ENVIRONMENT VARIABLES TO ADD IN RAILWAY

Go to: **Railway Dashboard → PlagiarismChecker service → Variables tab**

Copy and paste these EXACT values:

### 1. DATABASE_URL ✅ ALREADY SET
```
${{ Postgres.DATABASE_URL }}
```
**Status:** ✅ Already connected to Railway PostgreSQL

### 2. SECRET_KEY ⚠️ ADD THIS NOW
```
ZA7BxblXrMcqHAK6hGCWlxyypxlYfEtiZLIv1hYx3Uw
```

### 3. JWT_SECRET_KEY ⚠️ ADD THIS NOW
```
sp_H4SHnk5tAe6ImMvk5_0W80w3AssncHfUgXkX7dZE
```

### 4. GROQ_API_KEY ✅ ALREADY SET
```
gsk_YOUR_GROQ_API_KEY_HERE
```
**Status:** ✅ Already added in Railway

### 5. ADMIN_EMAIL ⚠️ ADD THIS NOW
```
admin@resgov.org
```
(You can change this to your preferred admin email)

### 6. ADMIN_PASSWORD ⚠️ ADD THIS NOW
```
SecureAdmin2024!
```
**⚠️ IMPORTANT:** Change this to a strong password you'll remember!

### 7. FLASK_ENV (Optional)
```
production
```

---

## 🎯 QUICK SETUP STEPS

### Step 1: Add the 4 Missing Variables
1. Go to Railway Dashboard → PlagiarismChecker → **Variables** tab
2. Click **+ New Variable** for each:
   - `SECRET_KEY` = `ZA7BxblXrMcqHAK6hGCWlxyypxlYfEtiZLIv1hYx3Uw`
   - `JWT_SECRET_KEY` = `sp_H4SHnk5tAe6ImMvk5_0W80w3AssncHfUgXkX7dZE`
   - `ADMIN_EMAIL` = `admin@resgov.org`
   - `ADMIN_PASSWORD` = `SecureAdmin2024!` (or your own password)

### Step 2: Wait for Deployment
Railway will automatically:
- Detect the new push to GitHub
- Build with the fixed dependencies (Pillow 10.4.0, opencv-python-headless)
- Deploy your application
- Takes 2-4 minutes

### Step 3: Run Database Migration
Once deployment succeeds, run this command:

```bash
# Install Railway CLI if needed
npm i -g @railway/cli

# Login and link project
railway login
railway link

# Run migration
railway run python run_migration.py
```

**Alternative:** You can also run the migration SQL directly using:
```bash
PGPASSWORD=xEmGwpuNlUxFJSmIXfTtSLmtGqzRDZHG psql -h gondola.proxy.rlwy.net -U postgres -p 22683 -d railway
```
Then manually run the SQL commands from `run_migration.py`

### Step 4: Get Your Railway URL
1. Go to Railway Dashboard → PlagiarismChecker service
2. Under **Settings** → **Domains**, you'll see your URL
3. Example: `https://plagiarismchecker-production.up.railway.app`

### Step 5: Update Frontend (IMPORTANT!)
You need to update the `API_URL` in your HTML files:

**Files to update:**
- `static/index.html`
- `static/admin.html`
- `static/candidate.html`
- `static/exam.html`
- `static/apply.html`

**Find this line in each file:**
```javascript
const API_URL = 'http://192.168.29.133:5000/api';
```

**Replace with your Railway URL:**
```javascript
const API_URL = 'https://your-app-name.up.railway.app/api';
```

Then commit and push:
```bash
git add .
git commit -m "Update API URL to Railway production"
git push origin main
```

### Step 6: Test Your Deployment
1. Visit: `https://your-app-name.up.railway.app/static/index.html`
2. Login as admin (use your ADMIN_EMAIL and ADMIN_PASSWORD)
3. Create a test exam
4. Visit: `https://your-app-name.up.railway.app/static/apply.html`
5. Fill out candidate application
6. Assign exam to candidate
7. Test taking the exam

---

## 🔧 WHAT WE FIXED

### 1. Dependency Issues ✅
- **Pillow:** Updated from 10.1.0 → 10.4.0 (Python 3.13 compatibility)
- **OpenCV:** Changed to `opencv-python-headless` 4.10.0.84 (for serverless)
- **NumPy:** Updated to 1.26.4
- **bcrypt:** Set version to 4.1.2
- **pyopenssl:** Set version to 24.0.0

### 2. Database Configuration ✅
- Added Railway DATABASE_URL handling
- Handles `postgres://` → `postgresql://` conversion
- Connected to your Railway PostgreSQL instance

### 3. Deployment Files Created ✅
- `Procfile` - Gunicorn configuration
- `runtime.txt` - Python 3.11.9
- `railway.json` - Railway-specific config
- `nixpacks.toml` - Build configuration
- `DEPLOYMENT_CHECKLIST.md` - Complete guide
- `.env.production` - Environment template

---

## ⚠️ TROUBLESHOOTING

### Build Still Failing?
- Check Railway logs: **Deployments** tab → Latest deployment → **View Logs**
- Verify all environment variables are set correctly
- Ensure PostgreSQL service is running (green status)

### Can't connect to database?
- Verify `DATABASE_URL` is set to `${{ Postgres.DATABASE_URL }}`
- Check PostgreSQL service is online
- Run the migration script

### 502 Bad Gateway?
- Check application logs for Python errors
- Ensure Gunicorn is starting (check "web: gunicorn app:app")
- Verify PORT environment variable (Railway provides this automatically)

### Admin can't login?
- Double-check `ADMIN_EMAIL` and `ADMIN_PASSWORD` variables
- Look for "Admin user created" message in logs
- Ensure migration has run to create users table

---

## 📊 MONITORING YOUR APP

### Check Deployment Status
- **Logs:** Railway Dashboard → Deployments → View Logs
- **Metrics:** Railway Dashboard → Metrics
- **Database:** Railway Dashboard → Postgres → Database tab

### Check Build Progress
Railway will show:
1. ✅ Nixpacks build started
2. ✅ Installing dependencies
3. ✅ Build completed
4. ✅ Deployment successful

---

## 🎉 SUMMARY

**What you already have:**
- ✅ PostgreSQL database created
- ✅ GROQ_API_KEY added
- ✅ DATABASE_URL configured
- ✅ Code pushed to GitHub with fixed dependencies

**What you need to do NOW:**
1. ⚠️ Add SECRET_KEY in Railway Variables
2. ⚠️ Add JWT_SECRET_KEY in Railway Variables
3. ⚠️ Add ADMIN_EMAIL in Railway Variables
4. ⚠️ Add ADMIN_PASSWORD in Railway Variables
5. ⏳ Wait for Railway to rebuild (check current build status)
6. ⏳ Run migration script after deployment
7. ⏳ Update frontend API URLs with Railway domain
8. ✅ Test the application!

**Expected Timeline:**
- Variables setup: 2 minutes
- Railway rebuild: 3-4 minutes
- Migration: 1 minute
- Frontend update: 5 minutes
- **Total: ~15 minutes to production!**

---

## 📞 NEED HELP?

If you encounter issues:
1. Check Railway build logs first
2. Verify all 7 environment variables are set
3. Ensure PostgreSQL service shows "Online"
4. Check that migration completed successfully
5. Verify frontend API_URL points to Railway domain

**Railway Dashboard:** https://railway.app/project/YOUR_PROJECT_ID

Good luck with your deployment! 🚀
