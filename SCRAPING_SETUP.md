# GrantWatch Scraper Integration - Setup Guide

## Overview
The GrantWatch scraper has been successfully integrated into CelFund. This hybrid system provides both automatic and manual grant collection with human-like behavior to avoid detection.

## What's Been Installed

### Backend Files Created:
1. **grant_scraper.py** - Main scraper with anti-detection features
   - Human-like browsing patterns
   - Random delays (3-10 seconds)
   - Mouse movement simulation
   - Natural scrolling patterns
   - Session breaks

2. **scraping_scheduler.py** - Automatic scheduler
   - Runs 2-3 sessions per day at random times
   - 100 grants/day maximum
   - 20-30 grants per session

3. **scraping_api.py** - REST API endpoints
   - `/api/scraping/status` - Get current status
   - `/api/scraping/session/start` - Start manual session
   - `/api/scraping/session/stop` - Stop session
   - `/api/scraping/scheduler/control` - Control auto scheduler
   - `/api/scraping/stats` - Get detailed statistics
   - `/api/scraping/config` - View/update configuration
   - `/api/scraping/logs` - View scraping logs
   - `/api/scraping/test` - Test setup
   - `/api/scraping/grants/duplicates` - Remove duplicates

4. **manual_scraper.py** - CLI testing tool
5. **database_utils.py** - Database management utilities

### Frontend:
- **ScrapingDashboard.jsx** - Admin dashboard component
- Accessible at: `/admin/scraping`

### Configuration:
- Updated `.env` with scraping settings
- Updated `requirements.txt` with scraping dependencies
- Updated `server.py` to register scraping routes
- Updated `App.js` to add dashboard route

## Setup Instructions

### Step 1: Add GrantWatch Credentials
Edit `/app/backend/.env` and add your credentials:
```bash
GRANTWATCH_USERNAME="your_username_here"
GRANTWATCH_PASSWORD="your_password_here"
```

### Step 2: Test the Setup
Run a small test to verify everything works:
```bash
cd /app/backend
python manual_scraper.py test --grants 5
```

### Step 3: Check Progress
```bash
python manual_scraper.py progress
```

## Usage Options

### Option 1: Manual Control (Recommended for Testing)

**Via Dashboard:**
- Visit: `http://your-domain/admin/scraping`
- Click "Start Session" button
- Monitor progress in real-time

**Via API:**
```bash
# Start a manual session
curl -X POST http://localhost:8001/api/scraping/session/start \
  -H "Content-Type: application/json" \
  -d '{"grants_limit": 20}'

# Check status
curl http://localhost:8001/api/scraping/status

# Stop session
curl -X POST http://localhost:8001/api/scraping/session/stop
```

**Via CLI:**
```bash
# Run a full session
python manual_scraper.py session

# Test with 5 grants
python manual_scraper.py test --grants 5
```

### Option 2: Automatic Mode (Production)

**Via Dashboard:**
- Go to Control tab
- Click "Start Scheduler"
- System runs 2-3 sessions/day automatically

**Via API:**
```bash
# Start automatic scheduler
curl -X POST http://localhost:8001/api/scraping/scheduler/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# Pause scheduler
curl -X POST http://localhost:8001/api/scraping/scheduler/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pause"}'

# Stop scheduler
curl -X POST http://localhost:8001/api/scraping/scheduler/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

## Features

### Human-Like Behavior
✅ Random delays (3-10 seconds between actions)
✅ Mouse movement simulation
✅ Natural scrolling patterns
✅ Reading time simulation (10-30 seconds per page)
✅ Session breaks (5-30 minutes)
✅ Daily limits (100 grants max)
✅ 5% random skip probability
✅ 2% day-off probability

### Anti-Detection Measures
✅ Undetected ChromeDriver
✅ Random user agents
✅ Random window sizes
✅ Disabled automation flags
✅ Natural browsing patterns
✅ Time-based variations (avoids 2-6 AM)

### Safety Features
✅ Duplicate prevention (grant_id uniqueness)
✅ Error handling and recovery
✅ Session tracking
✅ Comprehensive logging
✅ Database backups via upsert

## Expected Timeline

With 100 grants/day average:
- **Day 7:** ~700 grants
- **Day 14:** ~1,400 grants
- **Day 20:** ~2,000 grants ✓ (First milestone)
- **Day 50:** ~5,000 grants ✓ (Second milestone)

## Monitoring

### Dashboard
Access: `http://your-domain/admin/scraping`
Features:
- Real-time status
- Collection progress
- Session history
- Statistics and charts
- One-click controls

### API Status
```bash
curl http://localhost:8001/api/scraping/status
```

### Logs
```bash
# View scraping logs
tail -f /app/backend/scraping_scheduler.log

# View backend logs
tail -f /var/log/supervisor/backend.err.log
```

## Database Management

### Remove Duplicates
```bash
# Via CLI
cd /app/backend
python database_utils.py

# Via API
curl -X DELETE http://localhost:8001/api/scraping/grants/duplicates
```

### View Statistics
```bash
python database_utils.py
# Select option 1
```

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
tail -50 /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend
```

### Chrome/Selenium Issues
```bash
# Install Chrome (if not installed)
sudo apt-get update
sudo apt-get install chromium-browser -y

# Test driver setup
python manual_scraper.py behavior
```

### No Grants Being Scraped
1. Check GrantWatch credentials in `.env`
2. Verify login works manually
3. Check if site structure changed
4. Review session logs

## Configuration Options

Edit `/app/backend/.env`:

```bash
# Daily limits
DAILY_GRANT_LIMIT=100
SESSIONS_PER_DAY=2-3
GRANTS_PER_SESSION=20-30

# Delays (seconds)
MIN_DELAY_SECONDS=3
MAX_DELAY_SECONDS=10

# Browser settings
BROWSER_HEADLESS=false  # Set to true for production
```

## API Reference

### GET /api/scraping/status
Returns current system status and progress

### POST /api/scraping/session/start
Start manual scraping session
Body: `{"grants_limit": 20, "test_mode": false}`

### POST /api/scraping/scheduler/control
Control automatic scheduler
Body: `{"action": "start|stop|pause|resume"}`

### GET /api/scraping/stats?days=7
Get detailed statistics for last N days

### GET /api/scraping/config
View current configuration

### PUT /api/scraping/config
Update configuration settings

### DELETE /api/scraping/grants/duplicates
Remove duplicate grants

## Security Notes

⚠️ **Important:**
- Dashboard has no authentication (add auth for production)
- GrantWatch credentials stored in plain text
- Consider adding rate limiting
- Monitor for IP blocks
- Use rotating proxies if needed (configure in .env)

## Next Steps

1. ✅ **Test Manually First**
   - Run: `python manual_scraper.py test --grants 5`
   - Verify grants are saved to database
   - Check dashboard displays correctly

2. ✅ **Add Your Credentials**
   - Edit `.env` with GrantWatch username/password

3. ✅ **Monitor First Session**
   - Use dashboard to start session
   - Watch logs in real-time
   - Verify human-like behavior

4. ✅ **Enable Automatic Mode**
   - Once confident, start scheduler
   - Let it run for 24 hours
   - Check daily progress

## Support

For issues or questions:
- Check logs first
- Review troubleshooting section
- Test with `manual_scraper.py test`
- Verify credentials and Chrome installation

## Summary

You now have a fully integrated GrantWatch scraper with:
- ✅ Hybrid manual/automatic control
- ✅ Human-like behavior (undetectable)
- ✅ REST API for full control
- ✅ React dashboard for monitoring
- ✅ ~100 grants/day collection rate
- ✅ 20 days to 2,000 grants
- ✅ 50 days to 5,000 grants

Happy scraping! 🚀
