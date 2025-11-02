import aiohttp
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def send_to_airtable(webhook_url: str, data: Dict[str, Any]) -> bool:
    """
    Send form submission data to Airtable webhook
    """
    if not webhook_url:
        logger.info("No Airtable webhook URL configured")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in [200, 201, 202]:
                    logger.info("Successfully sent data to Airtable")
                    return True
                else:
                    logger.warning(f"Airtable webhook returned status {response.status}")
                    return False
    
    except Exception as e:
        logger.error(f"Failed to send to Airtable: {e}")
        return False
