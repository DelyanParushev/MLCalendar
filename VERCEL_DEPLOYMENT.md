# Vercel Deployment Guide for AI Calendar

## 🚀 Deploy to Vercel (Frontend + Backend + Database)

### Prerequisites
- Vercel account (free): https://vercel.com
- GitHub account
- Your code pushed to GitHub

---

## 📦 Step 1: Prepare the Code

All necessary files are already created! Here's what was added:

✅ `vercel.json` - Main Vercel configuration (backend routing)
✅ `api/index.py` - Serverless function entry point
✅ `frontend/vercel.json` - Frontend configuration

---

## 🗄️ Step 2: Set Up Vercel Postgres Database

### Option A: Use Vercel Dashboard (Easiest)

1. Go to https://vercel.com/dashboard
2. Click "Storage" → "Create Database"
3. Choose "Postgres"
4. Name it: `calendar-db`
5. Select region closest to you
6. Click "Create"
7. Copy the connection string (you'll add it as env var)

### Option B: Use Neon (Alternative)

1. Go to https://neon.tech
2. Create free account
3. Create new project: `calendar-db`
4. Copy the connection string

---

## 🚀 Step 3: Deploy Backend to Vercel

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Add Google OAuth and Vercel deployment config"
   git push origin main
   ```

2. **Import to Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - **Root Directory:** Leave as `.` (root)
   - **Framework Preset:** Other
   - Click "Deploy"

3. **Add Environment Variables:**
   
   After deployment, go to Project Settings → Environment Variables and add:

   ```
   # Database
   POSTGRES_URL=<your-vercel-postgres-connection-string>
   DATABASE_URL=<your-vercel-postgres-connection-string>
   
   # JWT
   SECRET_KEY=<generate-a-random-secret-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # CORS (update with your actual Vercel domain)
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
   
   # Google OAuth
   GOOGLE_CLIENT_ID=<your-google-client-id>.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=<your-google-client-secret>
   
   # ML Model (if using HuggingFace)
   ENABLE_ML_MODEL=true
   USE_HF_SPACE=true
   HF_SPACE_URL=https://dex7er999-calendar-nlp-api.hf.space
   ```

   **To generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Redeploy:**
   - Click "Deployments" → Latest deployment → "Redeploy"
   - This picks up the new environment variables

---

## 🎨 Step 4: Deploy Frontend to Vercel

### Option A: Separate Frontend Project (Recommended)

1. **Create new Vercel project:**
   - Go to https://vercel.com/new
   - Import same GitHub repository
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
   - Click "Deploy"

2. **Add Frontend Environment Variables:**
   ```
   VITE_API_BASE=https://your-backend-app.vercel.app/api
   VITE_GOOGLE_CLIENT_ID=<your-google-client-id>.apps.googleusercontent.com
   ```

3. **Update CORS:**
   - Go back to backend project settings
   - Update `CORS_ORIGINS` to include your frontend URL:
   ```
   CORS_ORIGINS=https://your-frontend-app.vercel.app,http://localhost:5173
   ```

### Option B: Monorepo (Frontend + Backend in one project)

Update `vercel.json` in root to handle both. (More complex, Option A is easier)

---

## 🔐 Step 5: Update Google OAuth

Add your Vercel URLs to Google Cloud Console:

1. Go to https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client
3. **Authorized JavaScript origins:**
   - Add: `https://your-frontend-app.vercel.app`
   - Add: `https://your-backend-app.vercel.app`
4. **Authorized redirect URIs:**
   - Add: `https://your-frontend-app.vercel.app`
5. Save

---

## ✅ Step 6: Test Your Deployment

1. Visit your frontend URL: `https://your-frontend-app.vercel.app`
2. Try signing in with Google
3. Create an event with natural language
4. Check that it persists (stored in Vercel Postgres)

---

## 🔧 Common Issues & Solutions

### Backend 500 Error
- Check Vercel logs: Project → Deployments → Click deployment → "View Function Logs"
- Verify all environment variables are set
- Ensure DATABASE_URL is correct

### CORS Error
- Update `CORS_ORIGINS` in backend environment variables
- Include both frontend and backend URLs

### Database Connection Error
- Verify Vercel Postgres connection string
- Check if database was created properly
- Try using Neon instead if issues persist

### Google OAuth Not Working
- Verify Google Cloud Console has correct URLs
- Check that GOOGLE_CLIENT_ID matches in both backend and frontend
- Ensure frontend URL is in authorized origins

---

## 📊 Monitoring & Logs

- **Backend logs:** Vercel Dashboard → Your Project → Deployments → Function Logs
- **Frontend logs:** Browser console
- **Database:** Vercel Dashboard → Storage → Your Postgres database

---

## 💰 Costs

✅ **Everything is FREE:**
- Vercel: Free tier (100GB bandwidth, unlimited projects)
- Vercel Postgres: Free tier (256 MB storage, 60 hours compute)
- Google OAuth: Free
- HuggingFace Spaces: Free

**No credit card required!**

---

## 🎯 Summary

**You now have:**
- ⚡ Near-instant backend (no cold starts!)
- 🗄️ Cloud PostgreSQL database (free tier)
- 🎨 Frontend on CDN (fast worldwide)
- 🔐 Google OAuth working
- 🤖 ML-powered event parsing

**Total setup time:** ~15 minutes
**Cost:** $0/month
