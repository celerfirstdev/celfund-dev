"""
Scraping Scheduler - Runs scraping sessions 2-3 times per day at random times
"""
import asyncio
import random
from datetime import datetime, timedelta, time
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import schedule
import time as time_module
from grant_scraper import GrantWatchScraper

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScrapingScheduler:
    """Manages scheduled scraping sessions with human-like patterns"""
    
    def __init__(self):
        self.sessions_run_today = 0
        self.last_session_time = None
        self.daily_sessions_target = random.randint(2, 3)
        self.scraper = None
        
        # Define time windows for scraping (more likely during certain hours)
        self.time_windows = [
            {'start': time(8, 0), 'end': time(11, 0), 'weight': 0.25},    # Morning
            {'start': time(11, 0), 'end': time(14, 0), 'weight': 0.20},   # Lunch
            {'start': time(14, 0), 'end': time(17, 0), 'weight': 0.25},   # Afternoon
            {'start': time(19, 0), 'end': time(22, 0), 'weight': 0.20},   # Evening
            {'start': time(22, 0), 'end': time(23, 30), 'weight': 0.10},  # Late evening
        ]
    
    def get_random_times_for_today(self) -> list:
        """Generate random times for today's scraping sessions"""
        times = []
        sessions_count = random.randint(2, 3)
        
        for _ in range(sessions_count):
            # Select time window based on weights
            window = random.choices(
                self.time_windows,
                weights=[w['weight'] for w in self.time_windows],
                k=1
            )[0]
            
            # Generate random time within window
            start_minutes = window['start'].hour * 60 + window['start'].minute
            end_minutes = window['end'].hour * 60 + window['end'].minute
            
            random_minutes = random.randint(start_minutes, end_minutes)
            random_time = time(random_minutes // 60, random_minutes % 60)
            
            times.append(random_time)
        
        # Sort times and ensure minimum gap
        times.sort()
        
        # Ensure at least 2 hours between sessions
        for i in range(1, len(times)):
            prev_minutes = times[i-1].hour * 60 + times[i-1].minute
            curr_minutes = times[i].hour * 60 + times[i].minute
            
            if curr_minutes - prev_minutes < 120:  # Less than 2 hours
                # Adjust current time
                new_minutes = prev_minutes + random.randint(120, 180)
                if new_minutes < 24 * 60:
                    times[i] = time(new_minutes // 60, new_minutes % 60)
        
        return times
    
    async def run_scraping_session(self):
        """Execute a scraping session"""
        try:
            # Add some randomness to actual execution time (+/- 15 minutes)
            delay = random.randint(-15, 15) * 60
            if delay > 0:
                logger.info(f"Adding random delay of {delay/60:.0f} minutes before starting")
                await asyncio.sleep(delay)
            
            # Check if we should skip (random chance to skip occasionally)
            if random.random() < 0.05:  # 5% chance to skip
                logger.info("Randomly skipping this session (human behavior simulation)")
                return
            
            # Initialize scraper if needed
            if not self.scraper:
                mongo_url = os.environ.get('MONGO_URL')
                db_name = os.environ.get('DB_NAME')
                self.scraper = GrantWatchScraper(mongo_url, db_name)
                await self.scraper.initialize()
            
            # Log in if credentials available
            username = os.environ.get('GRANTWATCH_USERNAME')
            password = os.environ.get('GRANTWATCH_PASSWORD')
            
            if username and password:
                await self.scraper.login_to_grantwatch(username, password)
            
            # Run the session
            logger.info(f"Starting scraping session {self.sessions_run_today + 1}/{self.daily_sessions_target}")
            await self.scraper.run_scraping_session()
            
            self.sessions_run_today += 1
            self.last_session_time = datetime.now()
            
            # Get and log progress
            progress = await self.scraper.get_progress()
            logger.info(f"Progress update: {progress}")
            
            # Occasionally take a day off (2% chance)
            if random.random() < 0.02:
                logger.info("Taking a day off (human behavior simulation)")
                self.sessions_run_today = self.daily_sessions_target
                
        except Exception as e:
            logger.error(f"Session failed: {e}")
    
    def schedule_daily_sessions(self):
        """Schedule sessions for the current day"""
        # Reset daily counter
        self.sessions_run_today = 0
        self.daily_sessions_target = random.randint(2, 3)
        
        # Get random times for today
        session_times = self.get_random_times_for_today()
        
        logger.info(f"Scheduling {len(session_times)} sessions for today at: {session_times}")
        
        # Schedule each session
        for session_time in session_times:
            schedule.every().day.at(session_time.strftime("%H:%M")).do(
                lambda: asyncio.create_task(self.run_scraping_session())
            )
    
    async def monitor_and_report(self):
        """Monitor scraping progress and send reports"""
        while True:
            try:
                if self.scraper:
                    progress = await self.scraper.get_progress()
                    
                    # Log daily summary at midnight
                    if datetime.now().hour == 0 and datetime.now().minute < 5:
                        logger.info("=" * 50)
                        logger.info("DAILY SUMMARY")
                        logger.info(f"Total grants in database: {progress['total_grants']}")
                        logger.info(f"Grants scraped today: {progress['grants_today']}")
                        logger.info(f"Sessions run today: {progress['sessions_today']}")
                        logger.info(f"Days to 2,000 grants: ~{progress['estimated_days_to_2000']}")
                        logger.info(f"Days to 5,000 grants: ~{progress['estimated_days_to_5000']}")
                        logger.info("=" * 50)
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(3600)
    
    async def run(self):
        """Main scheduler loop"""
        logger.info("Starting scraping scheduler")
        
        # Schedule initial sessions
        self.schedule_daily_sessions()
        
        # Start monitoring task
        monitor_task = asyncio.create_task(self.monitor_and_report())
        
        # Main loop
        while True:
            try:
                # Run pending scheduled tasks
                schedule.run_pending()
                
                # Check if it's a new day (reset at 12:01 AM)
                if datetime.now().hour == 0 and datetime.now().minute == 1:
                    # Clear old schedules
                    schedule.clear()
                    
                    # Schedule new sessions for the day
                    await asyncio.sleep(60)  # Wait a minute to avoid re-scheduling
                    self.schedule_daily_sessions()
                
                # Sleep for a minute
                await asyncio.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
        
        # Cleanup
        monitor_task.cancel()
        if self.scraper:
            await self.scraper.close()
