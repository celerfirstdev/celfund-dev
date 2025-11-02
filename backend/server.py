from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import stripe

# Import custom modules
from grant_matcher import GrantMatcher
from database import Database
from airtable_webhook import send_to_airtable

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db_client = client[os.environ['DB_NAME']]

# Initialize services
grant_matcher = GrantMatcher()
database = Database(mongo_url, os.environ['DB_NAME'])

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PRICE_ID = os.environ.get('STRIPE_PRICE_ID', 'price_1234')  # Set your price ID
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://grant-finder-app.preview.emergentagent.com')

# Airtable webhook
AIRTABLE_WEBHOOK_URL = os.environ.get('AIRTABLE_WEBHOOK_URL', '')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class GrantMatchRequest(BaseModel):
    project_summary: str
    organization_type: str
    focus_area: str
    email: EmailStr

class Grant(BaseModel):
    title: str
    funder: str
    description: str
    deadline: str
    amount: str
    url: str

class CheckoutRequest(BaseModel):
    email: EmailStr

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db_client.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db_client.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

@api_router.post("/match")
async def match_grants(request: GrantMatchRequest, req: Request):
    """
    Match grants from 7+ public data sources based on project summary
    """
    try:
        # Get client IP
        client_ip = req.client.host if req.client else None
        
        # Save submission to database
        submission_id = await database.save_submission(
            project_summary=request.project_summary,
            email=request.email,
            organization_type=request.organization_type,
            focus_area=request.focus_area,
            ip_address=client_ip
        )
        
        # Send to Airtable webhook (async, don't wait)
        if AIRTABLE_WEBHOOK_URL:
            webhook_data = {
                'project_summary': request.project_summary,
                'email': request.email,
                'organization_type': request.organization_type,
                'focus_area': request.focus_area,
                'timestamp': datetime.utcnow().isoformat(),
                'submission_id': submission_id
            }
            asyncio.create_task(send_to_airtable(AIRTABLE_WEBHOOK_URL, webhook_data))
        
        # Match grants from multiple sources
        grants = await grant_matcher.match_grants(
            project_summary=request.project_summary,
            focus_area=request.focus_area,
            org_type=request.organization_type
        )
        
        logger.info(f"Matched {len(grants)} grants for submission {submission_id}")
        
        return {
            'success': True,
            'grants': grants,
            'submission_id': submission_id
        }
        
    except Exception as e:
        logger.error(f"Grant matching error: {e}")
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': 'Failed to match grants'}
        )

@api_router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest):
    """
    Create Stripe checkout session for upgrade
    """
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                }
            ],
            mode='subscription',
            success_url=f'{FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{FRONTEND_URL}/',
        )
        
        return {
            'success': True,
            'checkout_url': checkout_session.url
        }
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': 'Failed to create checkout session'}
        )

@api_router.get("/stats")
async def get_stats():
    """Get submission statistics"""
    try:
        stats = await database.get_submission_stats()
        return {'success': True, 'stats': stats}
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': 'Failed to fetch stats'}
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()