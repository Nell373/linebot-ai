"""
LINE Bot Webhook Handler.
Main entry point for processing LINE webhook requests.
"""
import json
import logging
import os
from typing import Dict, Any
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Configure logging
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 Flask 應用
app = Flask(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

@app.route("/api/webhook", methods=['POST'])
def callback():
    logger.info("Received webhook request")
    
    # 檢查環境變數
    channel_secret = os.environ.get('LINE_CHANNEL_SECRET')
    channel_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    
    if not channel_secret or not channel_token:
        logger.error("Missing environment variables: LINE_CHANNEL_SECRET or LINE_CHANNEL_ACCESS_TOKEN")
        abort(500)
    
    # 獲取 X-Line-Signature 標頭值
    signature = request.headers.get('X-Line-Signature', '')
    if not signature:
        logger.error("Missing X-Line-Signature header")
        abort(400)

    # 獲取請求內容
    body = request.get_data(as_text=True)
    logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}", exc_info=True)
        abort(500)

    return 'OK'

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)