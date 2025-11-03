# Frontend-Backend Connectivity Fix - Complete Guide

## Summary of Issues Fixed

This document outlines all the connectivity issues between the frontend and backend, and the comprehensive fixes applied.

---

## Issues Identified

### 1. **CORS Middleware Order Bug** (Critical)
**Problem:** In `backend/server.py`, the CORS middleware was added AFTER routes were registered (lines 234-240).

**Impact:** CORS headers were not applied to preflight OPTIONS requests, causing browsers to block API calls with CORS errors.

**Fix:** Moved `app.add_middleware(CORSMiddleware, ...)` to line 48, BEFORE route definitions.

### 2. **Missing Proxy Configuration** (Critical)
**Problem:** No `setupProxy.js` existed for React development server.

**Impact:** During development, the React dev server (localhost:3000) couldn't forward API requests to the backend (localhost:8001).

**Fix:** Created `frontend/src/setupProxy.js` with proper proxy configuration using `http-proxy-middleware`.

### 3. **No Environment Variables** (Critical)
**Problem:**
- No `.env` file in frontend → `REACT_APP_BACKEND_URL` was undefined
- Inconsistent fallback logic across components

**Impact:** Frontend components couldn't determine the correct backend URL.

**Fix:**
- Created `frontend/.env.development` with `REACT_APP_BACKEND_URL=http://localhost:8001`
- Created `frontend/.env.example` as template
- Created `backend/.env.example` with all required variables

### 4. **Inconsistent API URL Handling**
**Problem:** Different components used different fallback strategies:
- `LandingPage.jsx`: `process.env.REACT_APP_BACKEND_URL || window.location.origin`
- `UpgradeModal.jsx`: `process.env.REACT_APP_BACKEND_URL || window.location.origin`
- `ScrapingDashboard.jsx`: `process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'`

**Impact:** Unpredictable behavior in different environments.

**Fix:** Standardized all components to use:
```javascript
const apiUrl = process.env.REACT_APP_BACKEND_URL
  ? `${process.env.REACT_APP_BACKEND_URL}/api/endpoint`
  : '/api/endpoint';
```

---

## Files Modified

### Backend
1. **backend/server.py**
   - Moved CORS middleware before route definitions (line 48-56)
   - Removed duplicate CORS middleware (previously at line 234-240)

### Frontend
2. **frontend/package.json**
   - Added `http-proxy-middleware` to devDependencies

3. **frontend/src/setupProxy.js** (New file)
   - Configured proxy for `/api` routes to backend during development

4. **frontend/.env.development** (New file)
   - Set `REACT_APP_BACKEND_URL=http://localhost:8001`

5. **frontend/.env.example** (New file)
   - Template for environment configuration

6. **frontend/src/pages/LandingPage.jsx**
   - Updated API URL construction to support relative URLs

7. **frontend/src/components/UpgradeModal.jsx**
   - Updated API URL construction to support relative URLs

8. **frontend/src/components/ScrapingDashboard.jsx**
   - Added `getApiBaseUrl()` helper function
   - Standardized API URL handling

### Documentation
9. **backend/.env.example** (New file)
   - Template for backend environment variables

---

## Setup Instructions

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.9+
- MongoDB (local or cloud instance)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create .env file from template:**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables in .env:**
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=celfund
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_PRICE_ID=price_your_price_id
   FRONTEND_URL=http://localhost:3000
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the backend server:**
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

   The backend should now be running on `http://localhost:8001`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Environment file is already configured:**
   - `.env.development` exists with `REACT_APP_BACKEND_URL=http://localhost:8001`
   - For production, create `.env.production` with your production backend URL

3. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

4. **Start the development server:**
   ```bash
   npm start
   # or
   yarn start
   ```

   The frontend should now be running on `http://localhost:3000`

---

## Testing the Fixes

### 1. Test Basic Connectivity

Open your browser to `http://localhost:3000` and open Developer Tools (F12).

**Network Tab:**
- Fill out the grant matching form and submit
- Check the Network tab for the `/api/match` request
- Verify it returns `200 OK` with grant data

**Console Tab:**
- Should see proxy logs like: `[Proxy] POST /api/match -> /api/match`
- No CORS errors should appear

### 2. Test Stripe Checkout

1. Click any grant card to trigger the upgrade modal after 2 interactions
2. Click "Upgrade Now"
3. Check Network tab for `/api/create-checkout-session`
4. Verify it returns a checkout URL or appropriate error message

### 3. Test Admin Dashboard (if applicable)

1. Navigate to `/admin` (if route exists)
2. Verify scraping status, stats, and controls load
3. Check Network tab for `/api/scraping/status` requests

### 4. Test "Continue Free" Button

1. Submit a grant search
2. Click a grant card (triggers interaction count)
3. Click another grant card (should show upgrade modal)
4. Click "Continue Free"
5. Verify all 10 grants are displayed (previously only 5)

---

## Common Issues & Troubleshooting

### Issue: "Proxy error: Unable to connect to backend server"

**Cause:** Backend is not running on port 8001

**Solution:**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Issue: CORS errors still appearing

**Cause:** Browser cache or environment variables not loaded

**Solution:**
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Restart frontend dev server
3. Verify `.env.development` exists and is loaded
4. Check backend CORS_ORIGINS includes `http://localhost:3000`

### Issue: "Cannot find module 'http-proxy-middleware'"

**Cause:** Dependencies not installed after package.json update

**Solution:**
```bash
cd frontend
npm install
# or
yarn install
```

### Issue: Environment variables not loading

**Cause:** `.env` files must be named exactly and placed correctly

**Solution:**
- Frontend: `.env.development` must be in `frontend/` directory
- Backend: `.env` must be in `backend/` directory
- Restart both servers after creating/modifying .env files

---

## Production Deployment

### Frontend Configuration

Create `frontend/.env.production`:
```env
REACT_APP_BACKEND_URL=https://your-backend-domain.com
```

Build for production:
```bash
cd frontend
npm run build
```

### Backend Configuration

Update `backend/.env`:
```env
FRONTEND_URL=https://your-frontend-domain.com
CORS_ORIGINS=https://your-frontend-domain.com
```

### Deployment Options

**Option 1: Same Domain (Recommended)**
- Deploy frontend and backend on same domain using reverse proxy
- Frontend: `https://yourdomain.com`
- Backend: `https://yourdomain.com/api`
- No CORS issues, no REACT_APP_BACKEND_URL needed

**Option 2: Different Domains**
- Frontend: `https://app.yourdomain.com`
- Backend: `https://api.yourdomain.com`
- Set `REACT_APP_BACKEND_URL=https://api.yourdomain.com`
- Set `CORS_ORIGINS=https://app.yourdomain.com` in backend

---

## Technical Explanation

### How the Proxy Works

In development:
1. React dev server runs on `http://localhost:3000`
2. Backend runs on `http://localhost:8001`
3. `setupProxy.js` intercepts requests to `/api/*`
4. Proxy forwards them to `http://localhost:8001/api/*`
5. Response is sent back to browser
6. **No CORS issues** because browser thinks request is same-origin

### How CORS Middleware Works

1. Browser sends preflight OPTIONS request
2. **CORS middleware must be BEFORE routes** to intercept it
3. Middleware adds headers:
   - `Access-Control-Allow-Origin: http://localhost:3000`
   - `Access-Control-Allow-Methods: POST, GET, OPTIONS, ...`
   - `Access-Control-Allow-Headers: Content-Type, ...`
4. Browser receives headers and allows actual request

### Environment Variable Precedence

```javascript
const apiUrl = process.env.REACT_APP_BACKEND_URL
  ? `${process.env.REACT_APP_BACKEND_URL}/api/endpoint`
  : '/api/endpoint';
```

- **If `REACT_APP_BACKEND_URL` is set:** Use absolute URL (production or custom config)
- **If not set:** Use relative URL `/api/endpoint` (development with proxy)

---

## Verification Checklist

Before deploying to production, verify:

- [ ] Backend starts without errors on port 8001
- [ ] Frontend starts without errors on port 3000
- [ ] Grant search form submits successfully
- [ ] Grants are displayed on the page
- [ ] "Continue Free" button shows all 10 grants
- [ ] Stripe checkout opens (or shows appropriate error if not configured)
- [ ] Admin dashboard loads (if applicable)
- [ ] No CORS errors in browser console
- [ ] Network tab shows successful API responses (200 OK)
- [ ] Proxy logs appear in terminal during API calls

---

## Files Created

```
backend/
  ├── .env.example          # Template for backend environment variables

frontend/
  ├── .env.development      # Development environment variables
  ├── .env.example          # Template for environment variables
  └── src/
      └── setupProxy.js     # Development proxy configuration
```

---

## Summary

All frontend-backend connectivity issues have been resolved through:

1. **Fixing CORS middleware order** - Ensures proper CORS headers
2. **Adding development proxy** - Enables seamless local development
3. **Standardizing environment variables** - Consistent configuration across environments
4. **Updating API URL logic** - Smart handling of development vs production

The application should now work correctly in both development and production environments.

For questions or issues, please refer to the troubleshooting section or check the browser console and network tab for specific error messages.
