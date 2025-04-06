from http.server import BaseHTTPRequestHandler
import os
import json
import logging
import sys

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
webhook_handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = "Webhook endpoint is active"
        self.wfile.write(message.encode())
        logger.info("GET request received, webhook is active")
        return None
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        logger.info(f"Request body: {post_data}")
        
        # 獲取 X-Line-Signature 標頭值
        signature = self.headers.get('X-Line-Signature', '')
        
        # 設置回應標頭
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        # 處理 webhook
        try:
            logger.info("Processing webhook request")
            webhook_handler.handle(post_data, signature)
            self.wfile.write("OK".encode())
            logger.info("Webhook request processed successfully")
        except InvalidSignatureError:
            logger.error("Invalid signature")
            self.wfile.write("Invalid signature".encode())
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            self.wfile.write(f"Error: {str(e)}".encode())
        
        return None

@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text
        user_id = event.source.user_id
        logger.info(f"Received message from user {user_id}: {text}")
        
        # 直接使用簡化版處理器進行測試
        try:
            # 嘗試導入簡化版處理器
            from src.simplified_processor import process_message
            logger.info("Successfully imported simplified processor")
        except ImportError as e:
            logger.error(f"Import error for simplified processor: {str(e)}")
            
            # 內建簡易處理器作為最後的回退方案
            def process_message(msg, uid):
                logger.info(f"Using fallback message processor for {uid}: {msg}")
                return f"您好！我收到了您的訊息：{msg}\n(使用內建簡易處理器回應)"
        
        # 處理訊息，傳入使用者 ID
        logger.info("Calling process_message function")
        response = process_message(text, user_id)
        logger.info(f"Generated response: {response}")
        
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        logger.info("Message sent to LINE")
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="處理訊息時發生錯誤，請稍後再試。")
            )
        except Exception as reply_error:
            logger.error(f"Failed to send error message: {str(reply_error)}") 