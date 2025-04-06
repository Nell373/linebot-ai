"""
Storage Service module.
Handles data persistence operations.
"""
import json
import logging
import os
import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Local storage path for development
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_message_result(user_id: str, result: Dict[str, Any]) -> bool:
    """
    Save message processing result to storage.
    
    Args:
        user_id: The LINE user ID
        result: The processed message result
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Add timestamp and user ID
        result['timestamp'] = datetime.datetime.now().isoformat()
        result['user_id'] = user_id
        
        # Determine storage file based on message type
        msg_type = result.get('type', 'unknown')
        filename = f"{msg_type}_{datetime.date.today().strftime('%Y%m')}.json"
        filepath = os.path.join(STORAGE_DIR, filename)
        
        # Read existing data
        existing_data = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse existing data in {filepath}, starting fresh")
        
        # Append new data
        existing_data.append(result)
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Saved result to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving message result: {str(e)}", exc_info=True)
        return False