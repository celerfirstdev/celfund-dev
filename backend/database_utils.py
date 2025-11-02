"""
Database Utilities for Grant Scraping System
Provides tools for managing, analyzing, and maintaining the grants database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any
import json

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GrantDatabaseManager:
    """Utilities for managing the grants database"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME')
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info(f"Connected to database: {self.db_name}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {}
        
        # Total grants
        stats['total_grants'] = await self.db.grants.count_documents({})
        
        # Active grants
        stats['active_grants'] = await self.db.grants.count_documents({'is_active': True})
        
        # Grants by source
        pipeline = [
            {'$group': {'_id': '$source', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        sources = await self.db.grants.aggregate(pipeline).to_list(None)
        stats['by_source'] = sources
        
        # Grants by deadline status
        today = datetime.utcnow()
        stats['rolling_deadline'] = await self.db.grants.count_documents({'deadline': 'Rolling'})
        
        # Recent scraping activity
        last_24h = datetime.utcnow() - timedelta(hours=24)
        stats['last_24h'] = await self.db.grants.count_documents({
            'scraped_at': {'$gte': last_24h}
        })
        
        last_week = datetime.utcnow() - timedelta(days=7)
        stats['last_week'] = await self.db.grants.count_documents({
            'scraped_at': {'$gte': last_week}
        })
        
        # Scraping sessions
        stats['total_sessions'] = await self.db.scraping_sessions.count_documents({})
        stats['successful_sessions'] = await self.db.scraping_sessions.count_documents({'status': 'completed'})
        stats['failed_sessions'] = await self.db.scraping_sessions.count_documents({'status': 'failed'})
        
        return stats
    
    async def remove_duplicates(self) -> int:
        """Remove duplicate grants based on grant_id"""
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
        
        duplicates = await self.db.grants.aggregate(pipeline).to_list(None)
        
        removed_count = 0
        for dup in duplicates:
            # Keep the first one, remove the rest
            ids_to_remove = dup['ids'][1:]
            result = await self.db.grants.delete_many({'_id': {'$in': ids_to_remove}})
            removed_count += result.deleted_count
        
        logger.info(f"Removed {removed_count} duplicate grants")
        return removed_count
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()

async def main():
    """Main utility menu"""
    manager = GrantDatabaseManager()
    await manager.connect()
    
    print("\n" + "="*50)
    print("GRANT DATABASE UTILITIES")
    print("="*50)
    print("1. View Statistics")
    print("2. Remove Duplicates")
    print("0. Exit")
    print("="*50)
    
    while True:
        try:
            choice = input("\nEnter choice (0-2): ")
            
            if choice == '1':
                stats = await manager.get_statistics()
                print("\nDatabase Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            
            elif choice == '2':
                removed = await manager.remove_duplicates()
                print(f"Removed {removed} duplicate grants")
            
            elif choice == '0':
                break
            
            else:
                print("Invalid choice")
        
        except Exception as e:
            print(f"Error: {e}")
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(main())
