import os
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import asyncpg
from contextlib import asynccontextmanager

class PostgresDatabase:
    """PostgreSQL database handler for CelFund (Vercel Postgres)"""
    
    def __init__(self, postgres_url: str):
        self.postgres_url = postgres_url
        self.pool = None
    
    async def initialize(self):
        """Initialize connection pool and create tables"""
        self.pool = await asyncpg.create_pool(self.postgres_url)
        
        # Create submissions table
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS grant_submissions (
                    id SERIAL PRIMARY KEY,
                    project_summary TEXT NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    organization_type VARCHAR(100),
                    focus_area VARCHAR(100),
                    ip_hash VARCHAR(64),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active'
                )
            ''')
            
            # Create index on email for faster lookups
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_submissions_email 
                ON grant_submissions(email)
            ''')
            
            # Create index on focus_area
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_submissions_focus_area 
                ON grant_submissions(focus_area)
            ''')
    
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
        
        async with self.pool.acquire() as conn:
            submission_id = await conn.fetchval('''
                INSERT INTO grant_submissions 
                (project_summary, email, organization_type, focus_area, ip_hash)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            ''', project_summary, email, organization_type, focus_area, ip_hash)
            
            return str(submission_id)
    
    async def get_submission_stats(self) -> Dict[str, Any]:
        """Get submission statistics"""
        async with self.pool.acquire() as conn:
            # Total submissions
            total = await conn.fetchval(
                'SELECT COUNT(*) FROM grant_submissions'
            )
            
            # By focus area
            focus_areas = await conn.fetch('''
                SELECT focus_area, COUNT(*) as count
                FROM grant_submissions
                GROUP BY focus_area
                ORDER BY count DESC
                LIMIT 10
            ''')
            
            return {
                'total_submissions': total,
                'by_focus_area': [
                    {'_id': row['focus_area'], 'count': row['count']}
                    for row in focus_areas
                ]
            }
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
