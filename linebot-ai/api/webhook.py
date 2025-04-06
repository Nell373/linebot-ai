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

def handler(request):
    if request.method == 'GET':
        return {
            "statusCode": 200,
            "body": "Webhook endpoint is active"
        }
    
    if request.method == 'POST':
        # 獲取請求內容
        try:
            body = request.body.decode('utf-8')
            logger.info(f"Request body: {body}")
            
            # 獲取 X-Line-Signature 標頭值
            signature = request.headers.get('X-Line-Signature', '')
            
            # 處理 webhook
            try:
                webhook_handler.handle(body, signature)
            except InvalidSignatureError:
                logger.error("Invalid signature")
                return {
                    "statusCode": 400,
                    "body": "Invalid signature"
                }
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                return {
                    "statusCode": 500,
                    "body": f"Error: {str(e)}"
                }
            
            return {
                "statusCode": 200,
                "body": "OK"
            }
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "statusCode": 500,
                "body": f"Error processing request: {str(e)}"
            }

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