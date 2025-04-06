from http.server import BaseHTTPRequestHandler
import json
import os
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Configure logging
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.info(f"GET request to {self.path}")
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('LINE Bot is running!'.encode())
        return

    def do_POST(self):
        logger.info(f"POST request to {self.path}")
        
        # 檢查環境變數
        if not os.environ.get('LINE_CHANNEL_SECRET') or not os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'):
            logger.error("Missing environment variables")
            self.send_response(500)
            self.end_headers()
            return

        # 獲取 X-Line-Signature 標頭值
        signature = self.headers.get('X-Line-Signature', '')
        if not signature:
            logger.error("Missing X-Line-Signature header")
            self.send_response(400)
            self.end_headers()
            return

        # 獲取請求內容
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        logger.info(f"Request body: {body}")

        try:
            handler.handle(body, signature)
            self.send_response(200)
            self.end_headers()
            self.wfile.write('OK'.encode())
        except InvalidSignatureError:
            logger.error("Invalid signature")
            self.send_response(400)
            self.end_headers()
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}", exc_info=True)
            self.send_response(500)
            self.end_headers()
        return

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        logger.info(f"Received message: {event.message.text}")
        logger.info(f"Event type: {event.type}")
        logger.info(f"Message type: {event.message.type}")
        
        # 從 src 目錄導入處理邏輯
        from src.message_processor import process_message
        
        # 處理訊息
        response = process_message(event.message.text)
        logger.info(f"Generated response: {response}")
        
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        logger.info("Reply message sent successfully")
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="處理訊息時發生錯誤，請稍後再試。")
            )
            logger.info("Error message sent successfully")
        except Exception as reply_error:
            logger.error(f"Error sending error message: {str(reply_error)}", exc_info=True) 