#!/bin/bash
# Script to update backend/.env with your Vercel environment variables
#
# INSTRUCTIONS:
# 1. Go to https://vercel.com/dashboard → Your Project → Settings → Environment Variables
# 2. Click the eye icon to reveal each value
# 3. Replace the placeholder values below with your actual values
# 4. Run: bash UPDATE_ENV.sh

cat > .env << 'EOF'
# MongoDB Configuration (from Vercel)
MONGO_URL=PASTE_YOUR_MONGO_URL_HERE
DB_NAME=PASTE_YOUR_DB_NAME_HERE

# Stripe Configuration (from Vercel + Stripe Dashboard)
STRIPE_SECRET_KEY=PASTE_YOUR_STRIPE_SECRET_KEY_HERE
STRIPE_PRICE_ID=PASTE_YOUR_STRIPE_PRICE_ID_HERE

# Frontend URL (from Vercel)
FRONTEND_URL=http://localhost:3000

# CORS Origins (allow both local and production)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,PASTE_YOUR_VERCEL_FRONTEND_URL_HERE

# Airtable Webhook (optional - from Vercel if you have it)
AIRTABLE_WEBHOOK_URL=PASTE_YOUR_AIRTABLE_WEBHOOK_URL_OR_LEAVE_EMPTY

# Scraping credentials (from Vercel)
GRANTWATCH_PASSWORD=PASTE_YOUR_GRANTWATCH_PASSWORD_HERE
EOF

echo "✅ .env file updated!"
echo "⚠️  Make sure you replaced all PASTE_YOUR_* placeholders with actual values"
echo ""
echo "Next steps:"
echo "1. Edit .env and replace all placeholder values"
echo "2. Restart the backend server"
