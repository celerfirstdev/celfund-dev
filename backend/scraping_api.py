"""
Scraping API Endpoints for CelFund
Provides REST API control over the grant scraping system
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import os
from enum import Enum
import json

# Import scraping modules
from grant_scraper import GrantWatchScraper
from scraping_scheduler import ScrapingScheduler

# Create API router
scraping_router = APIRouter(prefix="/scraping", tags=["scraping"])

# Global scheduler instance
scheduler_instance = None
scraper_instance = None
scraping_status = {
    "scheduler_running": False,
    "session_active": False,
    "last_session": None,
    "manual_mode": False
}

# Request/Response Models
class ScrapingMode(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    PAUSED = "paused"

class ScrapingConfig(BaseModel):
    mode: ScrapingMode = ScrapingMode.AUTOMATIC
    daily_grant_limit: int = 100
    sessions_per_day: int = 3
    grants_per_session: int = 25
    min_delay_seconds: float = 3
    max_delay_seconds: float = 10
    categories: Optional[list] = None

class SessionRequest(BaseModel):
    grants_limit: Optional[int] = 20
    categories: Optional[list] = None
    test_mode: bool = False

class SchedulerControl(BaseModel):
    action: str  # "start", "stop", "pause", "resume"
    mode: Optional[ScrapingMode] = None

# Utility Functions
async def get_scraper_instance():
    """Get or create scraper instance"""
    global scraper_instance
    if not scraper_instance:
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        scraper_instance = GrantWatchScraper(mongo_url, db_name)
        await scraper_instance.initialize()
    return scraper_instance

# API Endpoints

@scraping_router.get("/status")
async def get_scraping_status() -> Dict[str, Any]:
    """
    Get current scraping system status
    """
    scraper = await get_scraper_instance()
    progress = await scraper.get_progress()
    
    # Get recent sessions
    recent_sessions = await scraper.db.scraping_sessions.find(
        {}, 
        sort=[('start_time', -1)]
    ).limit(5).to_list(5)
    
    # Calculate success rate
    if recent_sessions:
        successful = len([s for s in recent_sessions if s.get('status') == 'completed'])
        success_rate = (successful / len(recent_sessions)) * 100
    else:
        success_rate = 0
    
    return {
        "system_status": {
            "scheduler_running": scraping_status["scheduler_running"],
            "session_active": scraping_status["session_active"],
            "mode": "automatic" if scraping_status["scheduler_running"] else "manual",
            "last_session": scraping_status["last_session"]
        },
        "progress": {
            "total_grants": progress['total_grants'],
            "grants_today": progress['grants_today'],
            "sessions_today": progress['sessions_today'],
            "estimated_days_to_2000": progress['estimated_days_to_2000'],
            "estimated_days_to_5000": progress['estimated_days_to_5000'],
            "success_rate": success_rate
        },
        "recent_sessions": [
            {
                "session_id": str(s.get('session_id', '')),
                "start_time": s.get('start_time').isoformat() if s.get('start_time') else None,
                "status": s.get('status', 'unknown'),
                "grants_scraped": s.get('grants_scraped', 0)
            }
            for s in recent_sessions
        ]
    }

@scraping_router.post("/session/start")
async def start_manual_session(
    request: SessionRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Start a manual scraping session
    """
    if scraping_status["session_active"]:
        raise HTTPException(status_code=400, detail="A session is already running")
    
    scraping_status["session_active"] = True
    scraping_status["manual_mode"] = True
    
    async def run_session():
        try:
            scraper = await get_scraper_instance()
            
            # Login if needed
            username = os.environ.get('GRANTWATCH_USERNAME')
            password = os.environ.get('GRANTWATCH_PASSWORD')
            if username and password and not request.test_mode:
                await scraper.login_to_grantwatch(username, password)
            
            # Run the session
            await scraper.run_scraping_session()
            
            scraping_status["last_session"] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Session error: {e}")
        finally:
            scraping_status["session_active"] = False
    
    background_tasks.add_task(run_session)
    
    return {
        "status": "session_started",
        "message": f"Manual scraping session started with limit of {request.grants_limit} grants",
        "test_mode": request.test_mode
    }

@scraping_router.post("/session/stop")
async def stop_current_session() -> Dict[str, Any]:
    """
    Stop the current scraping session
    """
    if not scraping_status["session_active"]:
        return {"status": "no_session", "message": "No active session to stop"}
    
    # Set flag to stop session
    scraping_status["session_active"] = False
    
    # Close scraper
    if scraper_instance:
        await scraper_instance.close()
    
    return {
        "status": "session_stopped",
        "message": "Scraping session stop signal sent"
    }

@scraping_router.post("/scheduler/control")
async def control_scheduler(
    control: SchedulerControl,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Control the automatic scheduler (start/stop/pause/resume)
    """
    global scheduler_instance
    
    if control.action == "start":
        if scraping_status["scheduler_running"]:
            return {"status": "already_running", "message": "Scheduler is already running"}
        
        async def run_scheduler():
            global scheduler_instance
            try:
                scheduler_instance = ScrapingScheduler()
                scraping_status["scheduler_running"] = True
                await scheduler_instance.run()
            except Exception as e:
                print(f"Scheduler error: {e}")
            finally:
                scraping_status["scheduler_running"] = False
        
        background_tasks.add_task(run_scheduler)
        
        return {
            "status": "scheduler_started",
            "message": "Automatic scheduler started",
            "mode": control.mode or "automatic"
        }
    
    elif control.action == "stop":
        if not scraping_status["scheduler_running"]:
            return {"status": "not_running", "message": "Scheduler is not running"}
        
        scraping_status["scheduler_running"] = False
        
        # Clean up scheduler
        if scheduler_instance and scheduler_instance.scraper:
            await scheduler_instance.scraper.close()
        
        return {
            "status": "scheduler_stopped",
            "message": "Automatic scheduler stopped"
        }
    
    elif control.action == "pause":
        scraping_status["scheduler_running"] = False
        return {"status": "paused", "message": "Scheduler paused"}
    
    elif control.action == "resume":
        scraping_status["scheduler_running"] = True
        return {"status": "resumed", "message": "Scheduler resumed"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@scraping_router.get("/config")
async def get_scraping_config() -> Dict[str, Any]:
    """
    Get current scraping configuration
    """
    return {
        "mode": "automatic" if scraping_status["scheduler_running"] else "manual",
        "daily_grant_limit": int(os.environ.get('DAILY_GRANT_LIMIT', 100)),
        "sessions_per_day": os.environ.get('SESSIONS_PER_DAY', '2-3'),
        "grants_per_session": os.environ.get('GRANTS_PER_SESSION', '20-30'),
        "min_delay_seconds": float(os.environ.get('MIN_DELAY_SECONDS', 3)),
        "max_delay_seconds": float(os.environ.get('MAX_DELAY_SECONDS', 10)),
        "browser_headless": os.environ.get('BROWSER_HEADLESS', 'false').lower() == 'true'
    }

@scraping_router.put("/config")
async def update_scraping_config(config: ScrapingConfig) -> Dict[str, Any]:
    """
    Update scraping configuration
    """
    # Update environment variables (in memory only)
    os.environ['DAILY_GRANT_LIMIT'] = str(config.daily_grant_limit)
    os.environ['SESSIONS_PER_DAY'] = str(config.sessions_per_day)
    os.environ['GRANTS_PER_SESSION'] = str(config.grants_per_session)
    os.environ['MIN_DELAY_SECONDS'] = str(config.min_delay_seconds)
    os.environ['MAX_DELAY_SECONDS'] = str(config.max_delay_seconds)
    
    # Save to config file for persistence
    config_data = {
        "mode": config.mode,
        "daily_grant_limit": config.daily_grant_limit,
        "sessions_per_day": config.sessions_per_day,
        "grants_per_session": config.grants_per_session,
        "min_delay_seconds": config.min_delay_seconds,
        "max_delay_seconds": config.max_delay_seconds,
        "categories": config.categories,
        "updated_at": datetime.now().isoformat()
    }
    
    with open('scraping_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    
    return {
        "status": "config_updated",
        "config": config_data
    }

@scraping_router.get("/stats")
async def get_scraping_statistics(
    days: int = Query(7, description="Number of days for statistics")
) -> Dict[str, Any]:
    """
    Get detailed scraping statistics
    """
    scraper = await get_scraper_instance()
    
    # Get grants by day
    grants_by_day = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        count = await scraper.db.grants.count_documents({
            'scraped_at': {'$gte': start, '$lt': end}
        })
        
        grants_by_day.append({
            'date': start.date().isoformat(),
            'grants': count
        })
    
    # Session analytics
    week_ago = datetime.utcnow() - timedelta(days=7)
    sessions = await scraper.db.scraping_sessions.find({
        'start_time': {'$gte': week_ago}
    }).to_list(None)
    
    successful_sessions = len([s for s in sessions if s.get('status') == 'completed'])
    failed_sessions = len([s for s in sessions if s.get('status') == 'failed'])
    
    # Average grants per session
    grants_per_session = [s.get('grants_scraped', 0) for s in sessions if s.get('status') == 'completed']
    avg_grants = sum(grants_per_session) / len(grants_per_session) if grants_per_session else 0
    
    return {
        "grants_by_day": grants_by_day,
        "session_analytics": {
            "total_sessions": len(sessions),
            "successful": successful_sessions,
            "failed": failed_sessions,
            "success_rate": (successful_sessions / len(sessions) * 100) if sessions else 0,
            "avg_grants_per_session": avg_grants
        }
    }

@scraping_router.get("/logs")
async def get_scraping_logs(
    lines: int = Query(100, description="Number of log lines to return")
) -> Dict[str, Any]:
    """
    Get recent scraping logs
    """
    try:
        with open('scraping_scheduler.log', 'r') as f:
            log_lines = f.readlines()[-lines:]
        
        return {
            "logs": log_lines,
            "total_lines": len(log_lines)
        }
    except FileNotFoundError:
        return {
            "logs": [],
            "message": "No log file found"
        }

@scraping_router.post("/test")
async def test_scraping_setup(
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Test scraping setup with a minimal session
    """
    async def test_session():
        try:
            scraper = await get_scraper_instance()
            
            # Test database connection
            db_connected = await scraper.db.grants.count_documents({}) >= 0
            
            # Test browser setup
            scraper.setup_driver()
            browser_working = scraper.driver is not None
            scraper.driver.quit() if scraper.driver else None
            
            return {
                "database": "connected" if db_connected else "failed",
                "browser": "working" if browser_working else "failed"
            }
        except Exception as e:
            return {"error": str(e)}
    
    result = await test_session()
    
    return {
        "status": "test_complete",
        "results": result
    }

@scraping_router.delete("/grants/duplicates")
async def remove_duplicate_grants() -> Dict[str, Any]:
    """
    Remove duplicate grants from database
    """
    scraper = await get_scraper_instance()
    
    # Find and remove duplicates
    pipeline = [
        {
            '$group': {
                '_id': '$grant_id',
                'count': {'$sum': 1},
                'ids': {'$push': '$_id'}
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}
            }
        }
    ]
    
    duplicates = await scraper.db.grants.aggregate(pipeline).to_list(None)
    
    removed_count = 0
    for dup in duplicates:
        ids_to_remove = dup['ids'][1:]  # Keep first, remove rest
        result = await scraper.db.grants.delete_many({'_id': {'$in': ids_to_remove}})
        removed_count += result.deleted_count
    
    return {
        "status": "duplicates_removed",
        "removed_count": removed_count,
        "duplicate_groups_found": len(duplicates)
    }

# Integration with main FastAPI app
def register_scraping_routes(app):
    """
    Register scraping routes with the main FastAPI app
    """
    app.include_router(scraping_router, prefix="/api")
