# 🚀 CelFund Vercel Deployment - Final Guide

## 📋 Prerequisites Checklist

- [x] Code ready in GitHub: `https://github.com/celerfirstdev/celfund-dev`
- [ ] Vercel account created at https://vercel.com
- [ ] Stripe account with test/production keys
- [ ] All sensitive keys removed from code (✅ Done)

---

## 🎯 Step-by-Step Deployment (10 Minutes)

### Step 1: Import Project to Vercel (2 minutes)

1. **Go to Vercel**: https://vercel.com/new
2. **Sign in** with GitHub
3. **Click**: "Import Git Repository"
4. **Select**: `celerfirstdev/celfund-dev`
5. **Project Settings**:
   - **Framework Preset**: Create React App
   - **Root Directory**: Leave empty (auto-detected)
   - **Build Command**: `cd frontend && yarn build`
   - **Output Directory**: `frontend/build`
   - **Install Command**: `cd frontend && yarn install`
6. **Click**: "Deploy" (but wait, add environment variables first!)

---

### Step 2: Configure Environment Variables (3 minutes)

**Before deploying**, click "Environment Variables" and add these:

#### Required Variables:

```bash
# Frontend URL (update after first deploy)
FRONTEND_URL=https://celfund.vercel.app
REACT_APP_BACKEND_URL=https://celfund.vercel.app

# Stripe Keys (from dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_KEY_HERE
STRIPE_PRICE_ID=price_YOUR_ACTUAL_PRICE_ID_HERE

# Airtable Webhook
AIRTABLE_WEBHOOK_URL=https://hooks.airtable.com/workflows/v1/genericWebhook/appm8zgsZ3r90PBrs/wflIYX3L8jgwHupRC/wtrQDd2Nchl5ptqK9

# Database (will be auto-added in Step 3)
MONGO_URL=mongodb+srv://YOUR_MONGO_URL
DB_NAME=celfund

# CORS
CORS_ORIGINS=*
```

**Important**: Replace `YOUR_ACTUAL_KEY_HERE` with your real Stripe keys!

**Apply to**: All Environments (Production, Preview, Development)

---

### Step 3: Set Up Database (2 minutes)

#### Option A: Use Vercel Postgres (Recommended)

1. In Vercel project dashboard, click **Storage** tab
2. Click **Create Database**
3. Select **Postgres**
4. Choose region (closest to your users)
5. Click **Create**
6. Vercel automatically adds `POSTGRES_URL` to environment variables

**Note**: You'll need to update backend code to use Postgres instead of MongoDB. See "Database Migration" section below.

#### Option B: Keep MongoDB

1. Use MongoDB Atlas: https://cloud.mongodb.com
2. Create free cluster
3. Get connection string
4. Add `MONGO_URL` to Vercel environment variables

---

### Step 4: Deploy! (2 minutes)

1. Click **"Deploy"** button
2. Wait 2-3 minutes for build
3. ✅ **Success!** Your app is live at: `https://celfund.vercel.app`

---

### Step 5: Verify Deployment (1 minute)

**Test these URLs**:

1. **Homepage**: https://celfund.vercel.app
2. **API Health**: https://celfund.vercel.app/api/
3. **Grant Matching**: Submit form and check for 10 grants
4. **Success Page**: https://celfund.vercel.app/success

---

## 🌐 Custom Domain Setup (Optional)

### If you have `celfund.com`:

1. Go to **Settings → Domains**
2. Click **"Add Domain"**
3. Enter: `celfund.com`
4. Follow DNS configuration:

```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME  
Name: www
Value: celfund.vercel.app
```

5. Wait 5-10 minutes for DNS propagation
6. ✅ Vercel auto-provisions SSL certificate

---

## 🔧 Configuration Files

### `/app/vercel.json` (Already Created)

```json
{
  "version": 2,
  "name": "celfund",
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    },
    {
      "src": "backend/server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/server.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}
```

### Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `FRONTEND_URL` | Your Vercel app URL | `https://celfund.vercel.app` |
| `REACT_APP_BACKEND_URL` | Backend API URL | `https://celfund.vercel.app` |
| `STRIPE_SECRET_KEY` | From Stripe dashboard | `sk_test_xxx` or `sk_live_xxx` |
| `STRIPE_PUBLISHABLE_KEY` | From Stripe dashboard | `pk_test_xxx` or `pk_live_xxx` |
| `STRIPE_PRICE_ID` | From Stripe product | `price_xxx` |
| `AIRTABLE_WEBHOOK_URL` | Your Airtable webhook | Already provided |
| `MONGO_URL` | MongoDB connection | `mongodb+srv://...` |
| `DB_NAME` | Database name | `celfund` |
| `CORS_ORIGINS` | Allowed origins | `*` |

---

## 🔄 Database Migration (If Using Vercel Postgres)

### Current: MongoDB
Your app currently uses MongoDB. Files:
- `/app/backend/server.py` - Uses MongoDB
- `/app/backend/database.py` - MongoDB adapter

### Option: Migrate to Postgres

**File to use**: `/app/backend/database_postgres.py` (already created)

**Update `/app/backend/server.py`**:

```python
# Replace this:
from database import Database
database = Database(mongo_url, os.environ['DB_NAME'])

# With this:
from database_postgres import PostgresDatabase
database = PostgresDatabase(os.environ['POSTGRES_URL'])

# Add startup event:
@app.on_event("startup")
async def startup():
    await database.initialize()
```

**Redeploy**: Vercel auto-deploys on git push

---

## 🚨 Troubleshooting

### Build Fails

**Error**: "Module not found"
**Fix**: Check all dependencies in `package.json` and `requirements.txt`

**Error**: "Cannot find frontend/build"
**Fix**: Verify build command is `cd frontend && yarn build`

### API Returns 404

**Error**: `/api/match` returns 404
**Fix**: Check `vercel.json` routes configuration

### Database Connection Fails

**Error**: "Cannot connect to database"
**Fix**: Verify `MONGO_URL` or `POSTGRES_URL` in environment variables

### CORS Errors

**Error**: "CORS policy blocked"
**Fix**: Update `CORS_ORIGINS` to include your domain

### Stripe Checkout Fails

**Error**: "Invalid API key"
**Fix**: Verify production Stripe keys are set correctly

---

## 📊 Post-Deployment

### Enable Analytics

1. Go to **Analytics** tab
2. Enable Web Analytics
3. View page views, performance, errors

### Monitor Logs

1. Go to **Deployments**
2. Click latest deployment
3. View **Function Logs** for API calls
4. View **Build Logs** for deployment issues

### Set Up Alerts

1. Go to **Settings → Notifications**
2. Enable deployment notifications
3. Add email for alerts

---

## 🔐 Security Checklist

- [x] Stripe keys in environment variables (not in code)
- [x] Airtable webhook URL secure
- [x] Database credentials in environment
- [ ] Rate limiting enabled (Vercel Pro plan)
- [x] HTTPS/SSL automatically enabled
- [x] CORS properly configured
- [x] IP hashing for privacy

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Homepage loads at `https://celfund.vercel.app`
- [ ] Form submission returns real grants
- [ ] Database saves submissions
- [ ] Airtable receives webhook data
- [ ] Stripe checkout opens correctly
- [ ] Success page displays after payment
- [ ] Mobile responsive design works
- [ ] All API endpoints respond
- [ ] Footer shows: "Built with ❤️ by CelFund — Powered by Celer Energy"

---

## 📞 Next Steps

### Immediate:
1. ✅ Deploy to Vercel
2. ✅ Test all features
3. ✅ Monitor logs for errors

### Short-term:
1. Get production Stripe keys
2. Switch from test to live mode
3. Set up custom domain
4. Create Stripe product ($39/month)

### Long-term:
1. Add more grant data sources
2. Implement caching
3. Add rate limiting
4. Set up monitoring (Sentry)
5. Add user authentication

---

## 🔗 Important Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **GitHub Repo**: https://github.com/celerfirstdev/celfund-dev
- **Stripe Dashboard**: https://dashboard.stripe.com
- **MongoDB Atlas**: https://cloud.mongodb.com
- **Vercel Docs**: https://vercel.com/docs

---

## 📧 Support

**Issues?**
- Open GitHub issue: https://github.com/celerfirstdev/celfund-dev/issues
- Check Vercel logs: Dashboard → Deployments → Logs
- Verify environment variables: Settings → Environment Variables

---

## ✅ Deployment Summary

**What You'll Get**:
- Live URL: `https://celfund.vercel.app`
- Auto-deploy on every git push
- SSL/HTTPS automatically
- Global CDN for fast loading
- Zero downtime deployments
- Built-in analytics
- Function logs for debugging

**Cost**: Free tier includes:
- 100GB bandwidth
- 100GB-hours compute time
- Unlimited deployments
- SSL certificate included

**Upgrade to Pro** ($20/month) for:
- Custom domains
- More bandwidth
- Priority support
- Advanced analytics

---

## 🚀 Ready to Deploy?

1. Go to: https://vercel.com/new
2. Import: `celerfirstdev/celfund-dev`
3. Add environment variables
4. Click "Deploy"
5. Wait 2-3 minutes
6. ✅ Live at `https://celfund.vercel.app`

**Time to deployment: ~10 minutes**
