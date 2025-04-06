from flask import Flask, request, abort
import os
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
webhook_handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))

@app.route('/')
def home():
    return 'LINE Bot is running!'

@app.route('/api/webhook', methods=['POST'])
def webhook():
    # 獲取 X-Line-Signature 標頭值
    signature = request.headers.get('X-Line-Signature', '')
    
    # 獲取請求體
    body = request.get_data(as_text=True)
    logger.info(f"Request body: {body}")
    
    try:
        # 驗證簽名並處理 webhook
        webhook_handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    
    return 'OK'

# 處理文字訊息
@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text
        user_id = event.source.user_id
        logger.info(f"Received message from user {user_id}: {text}")
        
        # 簡單的回應邏輯
        if "你好" in text or "哈囉" in text:
            response = "你好！我是您的 LINE Bot 助手。"
        elif "記事" in text:
            response = f"記事功能測試成功！您輸入的是：{text}"
        elif "午餐" in text:
            response = "午餐預算功能測試成功！"
        else:
            response = f"我收到了您的訊息：{text}\n這是簡化版回應，用於測試 LINE Bot 連接狀態。"
        
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 