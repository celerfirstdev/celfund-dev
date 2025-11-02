from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import os

class Database:
    """Database handler for CelFund"""
    
    def __init__(self, mongo_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        self.submissions = self.db.grant_submissions
    
    async def save_submission(
        self,
        project_summary: str,
        email: str,
        organization_type: str,
        focus_area: str,
        ip_address: Optional[str] = None
    ) -> str:
        """Save a grant search submission"""
        
        # Hash IP for privacy
        ip_hash = None
        if ip_address:
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
        
        submission = {
            'project_summary': project_summary,
            'email': email,
            'organization_type': organization_type,
            'focus_area': focus_area,
            'ip_hash': ip_hash,
            'timestamp': datetime.utcnow(),
            'status': 'active'
        }
        
        result = await self.submissions.insert_one(submission)
        return str(result.inserted_id)
    
    async def get_submission_stats(self) -> Dict[str, Any]:
        """Get submission statistics"""
        total = await self.submissions.count_documents({})
        
        # Group by focus area
        pipeline = [
            {
                '$group': {
                    '_id': '$focus_area',
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]
        
        focus_areas = await self.submissions.aggregate(pipeline).to_list(10)
        
        return {
            'total_submissions': total,
            'by_focus_area': focus_areas
        }
    
    async def close(self):
        """Close database connection"""
        self.client.close()
