# 🚀 Deploy Your AI Calendar to Render + Vercel (Free!)

This guide will help you deploy your calendar app for free using Render (backend) + Vercel (frontend).

## 📋 Prerequisites

- GitHub account
- Render account (free) - https://render.com
- Vercel account (free) - https://vercel.com

## 🗄️ Step 1: Prepare for Production

### 1.1 Update Requirements for Production

Add to `requirements.txt`:
```
gunicorn>=21.0.0
```

### 1.2 Create Production Environment File

Create `.env.production`:
```bash
# Database (Render will provide this)
DATABASE_URL=postgresql://user:pass@host:port/database

# JWT Configuration
SECRET_KEY=your-super-secret-production-key-change-this-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Update with your Vercel domain)
CORS_ORIGINS=https://your-app-name.vercel.app,http://localhost:5173
```

### 1.3 Create Render Build Script

Create `render-build.sh` in root directory:
```bash
#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migration
python migrate_simple.py
```

Make it executable:
```bash
chmod +x render-build.sh
```

## 🔧 Step 2: Deploy Backend to Render

### 2.1 Push Code to GitHub
```bash
git add .
git commit -m "Prepare for production deployment"
git push origin master
```

### 2.2 Create Render Web Service

1. Go to https://render.com/dashboard
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `your-calendar-api` (or any name)
   - **Runtime**: `Python 3`
   - **Build Command**: `./render-build.sh`
   - **Start Command**: `gunicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### 2.3 Add Environment Variables

In Render dashboard, add these environment variables:
```
SECRET_KEY=your-super-secret-production-key-change-this-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2.4 Create PostgreSQL Database

1. In Render dashboard: "New" → "PostgreSQL"
2. **Name**: `your-calendar-db`
3. **Plan**: `Free`
4. After creation, copy the "External Database URL"
5. Add to your web service environment variables:
   ```
   DATABASE_URL=<paste-the-database-url-here>
   ```

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Update Frontend Environment

Create `frontend/.env.production`:
```bash
VITE_API_BASE=https://your-calendar-api.onrender.com
```

### 3.2 Deploy to Vercel

1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.3 Add Environment Variables

In Vercel project settings → Environment Variables:
```
VITE_API_BASE=https://your-calendar-api.onrender.com
```

## 🔒 Step 4: Update CORS Settings

After both deployments, update your backend's CORS settings:

1. In Render dashboard → your web service → Environment Variables
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-app-name.vercel.app
   ```

## ✅ Step 5: Test Your Deployed App

1. Visit your Vercel URL: `https://your-app-name.vercel.app`
2. Create an account and test creating events
3. Your app is now live and accessible worldwide! 🌍

## 🔧 Troubleshooting

### Backend Issues:
- Check Render logs in dashboard
- Ensure environment variables are set
- Database connection issues: Check DATABASE_URL format

### Frontend Issues:
- Check browser console for API errors
- Ensure VITE_API_BASE points to your Render URL
- CORS errors: Update CORS_ORIGINS in Render

### Database Issues:
- Run migration manually in Render shell
- Check PostgreSQL connection string

## 📊 Free Tier Limits

**Render Free:**
- 750 hours/month (enough for 24/7 if you have only one service)
- 512 MB RAM
- Sleeps after 15 minutes of inactivity (wakes up on request)

**Vercel Free:**
- Unlimited deployments
- 100 GB bandwidth/month
- Custom domains supported

## 🚀 Going Further

### Custom Domain:
- Add custom domain in Vercel dashboard
- Update CORS_ORIGINS accordingly

### Performance Optimization:
- Enable Redis caching (Redis Labs free tier)
- Optimize database queries
- Add error monitoring (Sentry free tier)

### Scaling:
- Upgrade to Render's paid plans ($7/month) for always-on
- Use Vercel Pro for advanced features

---

**🎉 Congratulations! Your AI Calendar is now deployed and accessible worldwide for FREE!**

## 📞 Support

If you encounter issues during deployment:
1. Check the logs in both Render and Vercel dashboards
2. Ensure all environment variables are correctly set
3. Test API endpoints directly using curl or Postman

Your app URL: `https://your-app-name.vercel.app`
Your API URL: `https://your-calendar-api.onrender.com`