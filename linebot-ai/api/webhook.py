from http.server import BaseHTTPRequestHandler
import os
import json
import logging

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 LINE Bot API
try:
    from linebot import LineBotApi, WebhookHandler
    from linebot.exceptions import InvalidSignatureError
    from linebot.models import MessageEvent, TextMessage, TextSendMessage
    
    line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
    webhook_handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))
    logger.info("Successfully initialized LINE Bot API")
except Exception as e:
    logger.error(f"Error initializing LINE Bot API: {str(e)}")
    raise

# 簡易訊息處理函數
def process_message(message_text, user_id):
    """
    簡化版訊息處理器，直接內嵌在 webhook.py 中
    """
    logger.info(f"Processing message from {user_id}: {message_text}")
    
    # 簡單的回應邏輯
    if "你好" in message_text or "哈囉" in message_text:
        return "你好！我是您的 LINE Bot 助手。"
    
    elif "記事" in message_text:
        return f"記事功能測試成功！您輸入的是：{message_text}"
    
    elif "午餐" in message_text:
        return "午餐預算功能測試成功！"
    
    else:
        return f"我收到了您的訊息：{message_text}\n這是一個簡化版的回應，用於測試 LINE Bot 的連接狀態。"

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
        
        # 使用內嵌的訊息處理器
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