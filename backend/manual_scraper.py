"""
Manual Scraping Script - For testing and one-off scraping runs
"""
import asyncio
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
import os
from grant_scraper import GrantWatchScraper, HumanBehaviorSimulator
from datetime import datetime

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_scraping(num_grants: int = 5, category: str = None):
    """Test scraping with a small number of grants"""
    logger.info(f"Starting test scraping for {num_grants} grants")
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME') 
    username = os.environ.get('GRANTWATCH_USERNAME')
    password = os.environ.get('GRANTWATCH_PASSWORD')
    
    scraper = GrantWatchScraper(mongo_url, db_name)
    await scraper.initialize()
    
    try:
        # Setup driver
        scraper.setup_driver()
        
        # Login if credentials provided
        if username and password:
            success = await scraper.login_to_grantwatch(username, password)
            if not success:
                logger.error("Login failed, aborting")
                return
        
        # Scrape from specific category or random
        if category:
            categories = [category]
        else:
            import random
            categories = [random.choice(scraper.categories)]
        
        all_grants = []
        for cat in categories:
            logger.info(f"Scraping category: {cat}")
            grants = await scraper.scrape_category(cat, max_pages=1)
            all_grants.extend(grants[:num_grants])
            
            if len(all_grants) >= num_grants:
                break
        
        # Save grants
        saved = await scraper.save_grants(all_grants[:num_grants])
        logger.info(f"Test complete: {saved} grants saved")
        
        # Show sample grant
        if all_grants:
            logger.info(f"Sample grant: {all_grants[0]}")
        
    finally:
        await scraper.close()

async def run_single_session():
    """Run a single full scraping session"""
    logger.info("Running single scraping session")
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    username = os.environ.get('GRANTWATCH_USERNAME')
    password = os.environ.get('GRANTWATCH_PASSWORD')
    
    scraper = GrantWatchScraper(mongo_url, db_name)
    await scraper.initialize()
    
    try:
        # Login if credentials provided
        if username and password:
            await scraper.login_to_grantwatch(username, password)
        
        # Run session
        await scraper.run_scraping_session()
        
        # Show progress
        progress = await scraper.get_progress()
        logger.info("Session complete!")
        logger.info(f"Total grants: {progress['total_grants']}")
        logger.info(f"Grants today: {progress['grants_today']}")
        logger.info(f"Est. days to 2,000: {progress['estimated_days_to_2000']}")
        logger.info(f"Est. days to 5,000: {progress['estimated_days_to_5000']}")
        
    finally:
        await scraper.close()

async def check_progress():
    """Check current scraping progress"""
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    scraper = GrantWatchScraper(mongo_url, db_name)
    await scraper.initialize()
    
    try:
        progress = await scraper.get_progress()
        
        print("\n" + "=" * 50)
        print("SCRAPING PROGRESS REPORT")
        print("=" * 50)
        print(f"Total grants in database: {progress['total_grants']:,}")
        print(f"Grants scraped today: {progress['grants_today']}")
        print(f"Sessions run today: {progress['sessions_today']}")
        print(f"Estimated days to 2,000 grants: ~{progress['estimated_days_to_2000']}")
        print(f"Estimated days to 5,000 grants: ~{progress['estimated_days_to_5000']}")
        
        # Get recent sessions
        sessions = await scraper.db.scraping_sessions.find(
            {}, 
            sort=[('start_time', -1)],
            limit=5
        ).to_list(5)
        
        print("\nRecent Sessions:")
        for session in sessions:
            status = session.get('status', 'unknown')
            grants = session.get('grants_scraped', 0)
            start = session.get('start_time', 'unknown')
            print(f"  - {start}: {status} ({grants} grants)")
        
        print("=" * 50)
        
    finally:
        await scraper.close()

async def test_human_behavior():
    """Test human behavior simulation"""
    logger.info("Testing human behavior simulation")
    
    behavior = HumanBehaviorSimulator()
    
    # Test random delays
    logger.info("Testing random delays...")
    for i in range(3):
        await behavior.random_delay(1, 3)
    
    # Test time variation
    logger.info(f"Should scrape now? {behavior.vary_times()}")
    
    # Test daily limits
    logger.info(f"Should continue today? {behavior.should_continue_today()}")
    
    # Test headers
    headers = behavior.get_random_headers()
    logger.info(f"Random headers: {headers['User-Agent'][:50]}...")
    
    logger.info("Human behavior tests complete")

async def reset_daily_counters():
    """Reset daily counters for testing"""
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    scraper = GrantWatchScraper(mongo_url, db_name)
    await scraper.initialize()
    
    try:
        # Reset today's sessions
        result = await scraper.db.scraping_sessions.delete_many({
            'start_time': {'$gte': datetime.utcnow().replace(hour=0, minute=0, second=0)}
        })
        
        logger.info(f"Reset {result.deleted_count} sessions from today")
        
    finally:
        await scraper.close()

def main():
    parser = argparse.ArgumentParser(description='Manual grant scraping utility')
    parser.add_argument('command', choices=['test', 'session', 'progress', 'behavior', 'reset'],
                       help='Command to run')
    parser.add_argument('--grants', type=int, default=5,
                       help='Number of grants for test mode')
    parser.add_argument('--category', type=str,
                       help='Specific category to scrape')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        asyncio.run(test_scraping(args.grants, args.category))
    elif args.command == 'session':
        asyncio.run(run_single_session())
    elif args.command == 'progress':
        asyncio.run(check_progress())
    elif args.command == 'behavior':
        asyncio.run(test_human_behavior())
    elif args.command == 'reset':
        asyncio.run(reset_daily_counters())

if __name__ == "__main__":
    main()
