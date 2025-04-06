"""
Message processing module.
Handles the analysis and processing of user messages.
"""
import json
import logging
from typing import Dict, Any, Tuple, Optional

from .config import DEFAULT_RESPONSES
from .services.ai_service import analyze_message
from .services.storage_service import save_message_result

# Configure logging
logger = logging.getLogger(__name__)

class MessageProcessor:
    """Handles processing and analysis of user messages."""
    
    @staticmethod
    def process_message(text: str, user_id: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Process a user message using AI analysis.
        
        Args:
            text: The message text from the user
            user_id: The LINE user ID
            
        Returns:
            Tuple containing the reply message and the parsed result (if successful)
        """
        try:
            # Analyze the message using AI
            result = analyze_message(text)
            
            # Parse the result
            parsed_result = json.loads(result)
            
            # Save the result to storage
            save_message_result(user_id, parsed_result)
            
            # Generate reply based on message type
            reply = MessageProcessor._generate_reply(parsed_result)
            
            # Log for debugging
            logger.info(f"User: {user_id} | Input: {text} | Type: {parsed_result.get('type')}")
            logger.debug(f"Full analysis: {result}")
            
            return reply, parsed_result
            
        except json.JSONDecodeError:
            logger.error(f"JSON parse error for input: {text}")
            return DEFAULT_RESPONSES['error'], None
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return DEFAULT_RESPONSES['error'], None
    
    @staticmethod
    def _generate_reply(parsed_result: Dict[str, Any]) -> str:
        """Generate a reply message based on the parsed result."""
        msg_type = parsed_result.get("type")
        details = parsed_result.get("details", {})
        
        if msg_type == "accounting":
            return DEFAULT_RESPONSES['accounting'].format(
                item=details.get('item', ''),
                amount=details.get('amount', 0),
                category=details.get('category', '其他')
            )
        
        elif msg_type == "reminder":
            time_info = ""
            if details.get("date"):
                time_info += details.get("date", "")
            if details.get("time"):
                time_info += f" {details.get('time', '')}"
            
            return DEFAULT_RESPONSES['reminder'].format(
                time_info=time_info.strip() or "未指定時間",
                event=details.get('event', '')
            )
        
        elif msg_type == "task":
            return DEFAULT_RESPONSES['task'].format(
                description=details.get('description', ''),
                priority=details.get('priority', '中')
            )
        
        else:
            return DEFAULT_RESPONSES['unknown']