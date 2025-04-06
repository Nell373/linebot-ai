from http.server import BaseHTTPRequestHandler
import os
import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
webhook_handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = "Webhook endpoint is active"
        self.wfile.write(message.encode())
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
            webhook_handler.handle(post_data, signature)
            self.wfile.write("OK".encode())
        except InvalidSignatureError:
            logger.error("Invalid signature")
            self.wfile.write("Invalid signature".encode())
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            self.wfile.write(f"Error: {str(e)}".encode())
        
        return None

@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text
        logger.info(f"Received message: {text}")
        
        # 從 src 目錄導入處理邏輯
        from src.message_processor import process_message
        
        # 處理訊息
        response = process_message(text)
        logger.info(f"Generated response: {response}")
        
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="處理訊息時發生錯誤，請稍後再試。")
            )
        except Exception:
            pass 