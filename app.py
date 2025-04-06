"""
主應用入口點
創建並配置 Flask 應用
"""
import os
import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 獲取環境變數
channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
channel_secret = os.environ.get('LINE_CHANNEL_SECRET', '')

if not channel_secret or not channel_access_token:
    logger.error("環境變數缺失: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_CHANNEL_SECRET 未設置")
    raise ValueError("LINE API 憑證未設置")

# 初始化 LINE API
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# 導入訊息處理模組
from message_handler import handle_message, handle_postback

# 創建應用
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    """首頁路由"""
    return "LINE Bot Server is Running! Your token is working."

@app.route("/webhook", methods=["POST"])
def webhook():
    """LINE 的 Webhook 接收端點"""
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    logger.info("收到 Webhook 請求")
    logger.debug("請求內容: %s", body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("無效的簽名")
        abort(400)
    
    return "OK"

# 運行應用
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 