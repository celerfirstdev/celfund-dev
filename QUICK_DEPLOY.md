# 🚀 CelFund Quick Deploy to Vercel

## Step-by-Step Instructions (5 Minutes)

### ✅ Prerequisites Checklist
- [ ] Vercel account created (vercel.com)
- [ ] GitHub account with repo: celerfirstdev/celfund-dev
- [ ] Stripe account with production keys
- [ ] Code pushed to GitHub

---

## 🎯 Deploy in 3 Steps

### Step 1: Import to Vercel (2 minutes)

1. Go to: https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select: `celerfirstdev/celfund-dev`
4. Click **"Import"**
5. **Framework:** Create React App
6. **Root Directory:** Leave empty
7. Click **"Deploy"**

✅ Your app will be live at: `https://celfund.vercel.app`

---

### Step 2: Add Database (1 minute)

1. In Vercel project, click **"Storage"** tab
2. Click **"Create Database"**
3. Select **"Postgres"**
4. Choose your region
5. Click **"Create"**

✅ Database URL automatically added to environment variables

---

### Step 3: Add Environment Variables (2 minutes)

Go to **Settings → Environment Variables** and paste these:

```bash
# Copy your Vercel app URL after deployment
FRONTEND_URL=https://celfund.vercel.app
REACT_APP_BACKEND_URL=https://celfund.vercel.app

# Your Stripe Keys (replace with your actual keys)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_PRICE_ID=price_xxx

# Airtable
AIRTABLE_WEBHOOK_URL=https://hooks.airtable.com/workflows/v1/genericWebhook/appm8zgsZ3r90PBrs/wflIYX3L8jgwHupRC/wtrQDd2Nchl5ptqK9

# Other
CORS_ORIGINS=*
```

Click **"Save"** and then **"Redeploy"**

---

## 🎨 Custom Domain (Optional)

### Want celfund.com instead of celfund.vercel.app?

1. Go to **Settings → Domains**
2. Click **"Add Domain"**
3. Enter: `celfund.com`
4. Follow DNS instructions
5. Wait 5-10 minutes for SSL

---

## ✅ Verify Deployment

### Test 1: Visit Your App
Open: https://celfund.vercel.app

### Test 2: Submit Form
1. Fill in project details
2. Click "Find My Grants"
3. Should see 10 real grants

### Test 3: Check Database
In Vercel dashboard → Storage → Postgres → Data
Should see new entries in `grant_submissions` table

### Test 4: Test Stripe (Test Mode)
1. Interact with grants twice
2. Click "Upgrade Now"
3. Use test card: 4242 4242 4242 4242

---

## 🚨 If Something Goes Wrong

### Deployment Failed?
- Check **Deployments** → **Build Logs** for errors
- Verify all files are pushed to GitHub

### API Not Working?
- Verify environment variables are set
- Check **Functions** → **Logs** for errors

### Database Errors?
- Ensure Postgres database is created
- Check `POSTGRES_URL` is in environment variables

### Need Help?
Open issue: https://github.com/celerfirstdev/celfund-dev/issues

---

## 📊 What Happens After Deployment

✅ **Live URL:** https://celfund.vercel.app  
✅ **SSL:** Automatically enabled  
✅ **Auto-deploy:** Every push to `main` branch  
✅ **Zero downtime:** Seamless updates  
✅ **Global CDN:** Fast worldwide  
✅ **Analytics:** Built-in monitoring  

---

## 🎉 You're Done!

Your CelFund app is now live with:
- ✅ Real grant matching from 7+ sources
- ✅ Stripe payment integration
- ✅ Postgres database
- ✅ Airtable sync
- ✅ SSL/HTTPS
- ✅ Professional domain

**Share your app:** `https://celfund.vercel.app`

---

## 📞 Quick Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **GitHub Repo:** https://github.com/celerfirstdev/celfund-dev
- **Stripe Dashboard:** https://dashboard.stripe.com
- **Airtable:** https://airtable.com

---

**Total Time:** 5-10 minutes  
**Cost:** Free tier available (Vercel + Postgres)  
**Next:** Get production Stripe keys and switch from test mode
