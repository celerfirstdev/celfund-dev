"""
GrantWatch Scraper with Human-like Behavior
Scrapes grants gradually with realistic browsing patterns
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
import json
import hashlib
from fake_useragent import UserAgent

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

try:
    import undetected_chromedriver as uc
except ImportError:
    uc = None
    logging.warning("undetected_chromedriver not available, using standard Chrome driver")

logger = logging.getLogger(__name__)

class HumanBehaviorSimulator:
    """Simulates human-like browsing behavior"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.last_action_time = time.time()
        self.session_start_time = time.time()
        self.pages_viewed_today = 0
        self.last_break_time = time.time()
        
    async def random_delay(self, min_seconds: float = 3, max_seconds: float = 10):
        """Random delay between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
        logger.debug(f"Waited {delay:.2f} seconds")
        
    def mouse_movements(self, driver):
        """Simulate random mouse movements"""
        try:
            # Get page dimensions
            width = driver.execute_script("return document.body.scrollWidth")
            height = driver.execute_script("return window.innerHeight")
            
            actions = ActionChains(driver)
            
            # Random movements (2-4 movements)
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, min(width - 100, 1200))
                y = random.randint(100, min(height - 100, 700))
                
                # Move with random speed
                duration = random.uniform(0.5, 2)
                actions.move_by_offset(x, y)
                
            actions.perform()
            logger.debug("Performed mouse movements")
        except Exception as e:
            logger.debug(f"Mouse movement failed (non-critical): {e}")
    
    def scroll_patterns(self, driver):
        """Scroll like human reading"""
        try:
            # Get page height
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            # Scroll in chunks like reading
            current_position = 0
            
            while current_position < page_height - viewport_height:
                # Random scroll amount (like reading paragraphs)
                scroll_amount = random.randint(200, 500)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                
                # Random pause as if reading
                time.sleep(random.uniform(0.5, 2))
                
                # Occasionally scroll back up a bit (like re-reading)
                if random.random() < 0.2:
                    scroll_back = random.randint(50, 150)
                    driver.execute_script(f"window.scrollBy(0, -{scroll_back});")
                    time.sleep(random.uniform(0.3, 1))
                
                current_position += scroll_amount
                
            logger.debug("Completed human-like scrolling")
        except Exception as e:
            logger.debug(f"Scrolling failed (non-critical): {e}")
    
    async def session_breaks(self):
        """Take breaks between sessions"""
        current_time = time.time()
        
        # Take a break every 20-40 minutes
        if current_time - self.last_break_time > random.uniform(1200, 2400):
            break_duration = random.uniform(300, 1800)  # 5-30 minutes
            logger.info(f"Taking a break for {break_duration/60:.1f} minutes")
            await asyncio.sleep(break_duration)
            self.last_break_time = current_time
    
    def vary_times(self) -> bool:
        """Check if current time is appropriate for scraping"""
        current_hour = datetime.now().hour
        
        # Avoid scraping during typical sleeping hours (2 AM - 6 AM)
        if 2 <= current_hour <= 6:
            return False
            
        # Higher probability during business hours
        if 9 <= current_hour <= 17:
            return random.random() < 0.8
        
        # Medium probability during evening
        if 18 <= current_hour <= 23:
            return random.random() < 0.6
            
        # Lower probability during other times
        return random.random() < 0.4
    
    def should_continue_today(self) -> bool:
        """Check if daily limit reached"""
        return self.pages_viewed_today < random.randint(50, 100)
    
    async def read_time(self):
        """Simulate time spent reading a page"""
        read_duration = random.uniform(10, 30)
        await asyncio.sleep(read_duration)
        logger.debug(f"Spent {read_duration:.1f} seconds on page")
        self.pages_viewed_today += 1
    
    def get_random_headers(self) -> Dict[str, str]:
        """Get randomized browser headers"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'en-US,en;q=0.8,es;q=0.6'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': random.choice(['1', None]),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

class GrantWatchScraper:
    """Main scraper for GrantWatch with anti-detection measures"""
    
    def __init__(self, mongo_url: str, db_name: str):
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.client = None
        self.db = None
        self.behavior = HumanBehaviorSimulator()
        self.driver = None
        self.session_grants_scraped = 0
        self.total_grants_scraped = 0
        self.categories_scraped_today = []
        
        # Categories to scrape (randomized each session)
        self.categories = [
            'grants-for-small-business',
            'grants-for-nonprofits',
            'grants-for-women',
            'grants-for-minorities',
            'grants-for-veterans',
            'grants-for-education',
            'grants-for-arts',
            'grants-for-health',
            'grants-for-environment',
            'grants-for-technology',
            'grants-for-community',
            'grants-for-youth'
        ]
        
    async def initialize(self):
        """Initialize database connection"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        
        # Create indexes
        await self.db.grants.create_index([('grant_id', 1)], unique=True)
        await self.db.grants.create_index([('title', 'text'), ('description', 'text')])
        await self.db.scraping_sessions.create_index([('session_id', 1)])
        
        logger.info("Database initialized")
    
    def setup_driver(self):
        """Setup Selenium driver with anti-detection measures"""
        options = None
        
        # Use undetected_chromedriver if available
        if uc:
            options = uc.ChromeOptions()
        else:
            options = Options()
        
        # Randomize window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')
        
        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        options.add_argument(f'user-agent={self.behavior.ua.random}')
        
        # Headless mode and other settings
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        
        # Initialize driver
        try:
            if uc:
                self.driver = uc.Chrome(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            # Additional anti-detection JavaScript
            try:
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    '''
                })
            except Exception:
                pass  # CDP commands may not work in all configurations
            
            logger.info("Browser driver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}")
    
    async def login_to_grantwatch(self, username: str, password: str):
        """Login to GrantWatch account"""
        try:
            self.driver.get("https://www.grantwatch.com/login")
            
            # Wait for page load
            await self.behavior.random_delay(3, 5)
            
            # Find and fill username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Type like a human (with delays)
            for char in username:
                username_field.send_keys(char)
                await asyncio.sleep(random.uniform(0.05, 0.2))
            
            await self.behavior.random_delay(1, 2)
            
            # Find and fill password
            password_field = self.driver.find_element(By.NAME, "password")
            for char in password:
                password_field.send_keys(char)
                await asyncio.sleep(random.uniform(0.05, 0.2))
            
            await self.behavior.random_delay(1, 3)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            await self.behavior.random_delay(3, 5)
            
            logger.info("Successfully logged in to GrantWatch")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def scrape_grant_details(self, grant_element) -> Optional[Dict[str, Any]]:
        """Extract grant details from a grant element"""
        try:
            grant_data = {}
            
            # Extract title
            title_elem = grant_element.find_element(By.CSS_SELECTOR, "h3, h4, .grant-title")
            grant_data['title'] = title_elem.text.strip()
            
            # Extract description
            desc_elem = grant_element.find_element(By.CSS_SELECTOR, ".grant-description, .summary")
            grant_data['description'] = desc_elem.text.strip()
            
            # Extract deadline if available
            try:
                deadline_elem = grant_element.find_element(By.CSS_SELECTOR, ".deadline, .due-date")
                grant_data['deadline'] = deadline_elem.text.strip()
            except:
                grant_data['deadline'] = 'Rolling'
            
            # Extract amount if available
            try:
                amount_elem = grant_element.find_element(By.CSS_SELECTOR, ".amount, .funding-amount")
                grant_data['amount'] = amount_elem.text.strip()
            except:
                grant_data['amount'] = 'Varies'
            
            # Extract funder if available
            try:
                funder_elem = grant_element.find_element(By.CSS_SELECTOR, ".funder, .organization")
                grant_data['funder'] = funder_elem.text.strip()
            except:
                grant_data['funder'] = 'Multiple Funders'
            
            # Extract URL
            try:
                link_elem = grant_element.find_element(By.CSS_SELECTOR, "a")
                grant_data['url'] = link_elem.get_attribute('href')
            except:
                grant_data['url'] = ''
            
            # Generate unique ID
            grant_data['grant_id'] = hashlib.md5(
                f"{grant_data['title']}_{grant_data['funder']}".encode()
            ).hexdigest()[:16]
            
            # Add metadata
            grant_data['source'] = 'GrantWatch'
            grant_data['scraped_at'] = datetime.utcnow()
            grant_data['is_active'] = True
            
            return grant_data
            
        except Exception as e:
            logger.error(f"Failed to extract grant details: {e}")
            return None
    
    async def scrape_page(self, url: str) -> List[Dict[str, Any]]:
        """Scrape grants from a single page"""
        grants = []
        
        try:
            # Navigate to page
            self.driver.get(url)
            
            # Wait for page load
            await self.behavior.random_delay(2, 4)
            
            # Simulate human behavior
            self.behavior.mouse_movements(self.driver)
            await self.behavior.random_delay(1, 2)
            self.behavior.scroll_patterns(self.driver)
            
            # Wait for grants to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "grant-item"))
            )
            
            # Read the page
            await self.behavior.read_time()
            
            # Find all grant elements
            grant_elements = self.driver.find_elements(By.CSS_SELECTOR, ".grant-item, .grant-listing")
            
            for element in grant_elements:
                grant_data = await self.scrape_grant_details(element)
                if grant_data:
                    grants.append(grant_data)
                
                # Random micro-delay between grants
                await self.behavior.random_delay(0.5, 1.5)
            
            logger.info(f"Scraped {len(grants)} grants from {url}")
            
        except Exception as e:
            logger.error(f"Failed to scrape page {url}: {e}")
        
        return grants
    
    async def scrape_category(self, category: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Scrape grants from a specific category"""
        all_grants = []
        
        # Randomize starting page (not always from page 1)
        start_page = random.randint(1, 3)
        
        for page_num in range(start_page, start_page + max_pages):
            # Check if should continue
            if not self.behavior.should_continue_today():
                logger.info("Daily limit reached, stopping")
                break
            
            url = f"https://www.grantwatch.com/{category}/{page_num}"
            
            # Scrape the page
            grants = await self.scrape_page(url)
            all_grants.extend(grants)
            
            # Random delay between pages
            await self.behavior.random_delay(5, 15)
            
            # Occasionally take longer breaks
            if random.random() < 0.3:
                await self.behavior.random_delay(30, 60)
        
        return all_grants
    
    async def save_grants(self, grants: List[Dict[str, Any]]) -> int:
        """Save grants to database"""
        saved_count = 0
        
        for grant in grants:
            try:
                # Use upsert to avoid duplicates
                result = await self.db.grants.update_one(
                    {'grant_id': grant['grant_id']},
                    {'$set': grant},
                    upsert=True
                )
                
                if result.upserted_id:
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to save grant: {e}")
        
        logger.info(f"Saved {saved_count} new grants to database")
        return saved_count
    
    async def run_scraping_session(self):
        """Run a single scraping session (20-30 grants)"""
        session_id = hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:8]
        logger.info(f"Starting scraping session {session_id}")
        
        # Record session start
        await self.db.scraping_sessions.insert_one({
            'session_id': session_id,
            'start_time': datetime.utcnow(),
            'status': 'running'
        })
        
        try:
            # Setup driver
            self.setup_driver()
            
            # Random selection of categories (2-3 per session)
            available_categories = [c for c in self.categories if c not in self.categories_scraped_today]
            if not available_categories:
                available_categories = self.categories
                self.categories_scraped_today = []
            
            session_categories = random.sample(
                available_categories, 
                min(random.randint(2, 3), len(available_categories))
            )
            
            all_grants = []
            
            for category in session_categories:
                logger.info(f"Scraping category: {category}")
                
                # Scrape 7-10 grants per category
                grants = await self.scrape_category(category, max_pages=2)
                all_grants.extend(grants)
                
                self.categories_scraped_today.append(category)
                
                # Break if we have enough grants
                if len(all_grants) >= random.randint(20, 30):
                    break
                
                # Random delay between categories
                await self.behavior.random_delay(30, 60)
            
            # Save grants
            saved_count = await self.save_grants(all_grants)
            self.session_grants_scraped = saved_count
            self.total_grants_scraped += saved_count
            
            # Update session record
            await self.db.scraping_sessions.update_one(
                {'session_id': session_id},
                {
                    '$set': {
                        'end_time': datetime.utcnow(),
                        'status': 'completed',
                        'grants_scraped': saved_count,
                        'categories': session_categories
                    }
                }
            )
            
            logger.info(f"Session {session_id} completed: {saved_count} grants scraped")
            
        except Exception as e:
            logger.error(f"Session {session_id} failed: {e}")
            
            # Update session as failed
            await self.db.scraping_sessions.update_one(
                {'session_id': session_id},
                {
                    '$set': {
                        'end_time': datetime.utcnow(),
                        'status': 'failed',
                        'error': str(e)
                    }
                }
            )
        
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    async def get_progress(self) -> Dict[str, Any]:
        """Get scraping progress statistics"""
        total_grants = await self.db.grants.count_documents({})
        today_grants = await self.db.grants.count_documents({
            'scraped_at': {'$gte': datetime.utcnow().replace(hour=0, minute=0, second=0)}
        })
        
        sessions_today = await self.db.scraping_sessions.count_documents({
            'start_time': {'$gte': datetime.utcnow().replace(hour=0, minute=0, second=0)}
        })
        
        return {
            'total_grants': total_grants,
            'grants_today': today_grants,
            'sessions_today': sessions_today,
            'estimated_days_to_2000': max(0, (2000 - total_grants) // 100),
            'estimated_days_to_5000': max(0, (5000 - total_grants) // 100)
        }
    
    async def close(self):
        """Close connections"""
        if self.driver:
            self.driver.quit()
        if self.client:
            self.client.close()
