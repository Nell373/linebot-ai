"""
LINE Handler module.
Manages interactions with the LINE Messaging API.
"""
import json
import logging
from typing import Dict, Any, List
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    FlexSendMessage
)

from .config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from .message_processor import MessageProcessor

# Configure logging
logger = logging.getLogger(__name__)

# Initialize LINE API clients
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(LINE_CHANNEL_SECRET)

class LineHandler:
    """Handles LINE platform interactions."""
    
    @staticmethod
    def validate_signature(body: str, signature: str) -> bool:
        """
        Validate the LINE request signature.
        
        Args:
            body: The request body as string
            signature: The X-Line-Signature header
            
        Returns:
            True if valid, False otherwise
        """
        try:
            webhook_handler.validate_signature(body, signature)
            return True
        except InvalidSignatureError:
            logger.warning("Invalid LINE signature")
            return False
    
    @staticmethod
    def handle_webhook_events(events: List[Dict[str, Any]]) -> None:
        """
        Process LINE webhook events.
        
        Args:
            events: List of LINE event objects
        """
        for event in events:
            try:
                event_type = event.get("type")
                
                # Handle message events
                if event_type == "message":
                    LineHandler._handle_message_event(event)
                    
                # Handle follow/unfollow events
                elif event_type == "follow":
                    LineHandler._handle_follow_event(event)
                elif event_type == "unfollow":
                    LineHandler._handle_unfollow_event(event)
                    
            except Exception as e:
                logger.error(f"Error handling event: {str(e)}", exc_info=True)
    
    @staticmethod
    def _handle_message_event(event: Dict[str, Any]) -> None:
        """Handle LINE message events."""
        try:
            message_type = event.get("message", {}).get("type")
            
            # Currently we only support text messages
            if message_type == "text":
                user_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                message_text = event["message"]["text"]
                
                # Process the message
                reply_message, parsed_result = MessageProcessor.process_message(
                    message_text, user_id
                )
                
                # Send simple text reply
                line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text=reply_message)
                )
                
        except Exception as e:
            logger.error(f"Error handling message event: {str(e)}", exc_info=True)
    
    @staticmethod
    def _handle_follow_event(event: Dict[str, Any]) -> None:
        """Handle LINE follow (add friend) events."""
        try:
            user_id = event["source"]["userId"]
            reply_token = event["replyToken"]
            
            # Welcome message
            welcome_message = (
                "您好！我是您的小日助手，可以協助您記錄支出、設定提醒和管理任務。\n\n"
                "例如，您可以這樣使用我：\n"
                "• 「午餐120元」- 記帳\n"
                "• 「提醒我明天早上9點開會」- 設定提醒\n"
                "• 「買牛奶」- 新增任務\n\n"
                "請試著傳送訊息給我吧！"
            )
            
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=welcome_message)
            )
            
            logger.info(f"New user followed: {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling follow event: {str(e)}", exc_info=True)
    
    @staticmethod
    def _handle_unfollow_event(event: Dict[str, Any]) -> None:
        """Handle LINE unfollow (block/unfriend) events."""
        try:
            user_id = event["source"]["userId"]
            logger.info(f"User unfollowed: {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling unfollow event: {str(e)}", exc_info=True)