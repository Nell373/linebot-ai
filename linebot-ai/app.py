"""
LINE Bot Flask 應用程式
這個應用程式處理 LINE Bot 的 webhook 請求。
"""
import os
import sys
import logging
import traceback
from flask import Flask, request, abort, Response, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 設置日誌記錄
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 確保 src 目錄在 Python 路徑中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 初始化 Flask 應用
app = Flask(__name__)

# 檢查環境變數
channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
channel_secret = os.environ.get('LINE_CHANNEL_SECRET', '')

if not channel_access_token or not channel_secret:
    logger.error("環境變數缺失: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_CHANNEL_SECRET 未設置")
    if __name__ == "__main__":
        sys.exit(1)

# 初始化 LINE Bot API
try:
    line_bot_api = LineBotApi(channel_access_token)
    handler = WebhookHandler(channel_secret)
    logger.info("LINE Bot API 初始化成功")
except Exception as e:
    logger.error(f"初始化 LINE Bot API 時發生錯誤: {str(e)}")
    if __name__ == "__main__":
        sys.exit(1)

# 健康檢查路由
@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def home():
    """處理根路徑的 GET 請求"""
    logger.info("根路徑被訪問")
    return Response('LINE Bot is running!', status=200)

@app.route('/api', methods=['GET'])
def api_home():
    """處理 API 根路徑的 GET 請求"""
    logger.info("API 根路徑被訪問")
    return Response('API endpoint is active', status=200)

@app.route('/api/webhook', methods=['GET'])
def webhook_get():
    """處理 webhook 的 GET 請求"""
    logger.info("Webhook GET 路徑被訪問")
    return Response('Webhook endpoint is active', status=200)

@app.route('/api/webhook', methods=['POST'])
def webhook_post():
    """處理 webhook 的 POST 請求"""
    logger.info("Webhook POST 路徑被訪問")
    
    # 檢查環境變數
    if not channel_secret or not channel_access_token:
        logger.error("環境變數缺失")
        abort(500)

    # 獲取 X-Line-Signature 標頭值
    signature = request.headers.get('X-Line-Signature', '')
    if not signature:
        logger.error("缺少 X-Line-Signature 標頭")
        abort(400)

    # 獲取請求內容
    try:
        body = request.get_data(as_text=True)
        logger.info(f"請求內容: {body}")
    except Exception as e:
        logger.error(f"獲取請求內容時發生錯誤: {str(e)}")
        abort(400)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("無效的簽名")
        abort(400)
    except Exception as e:
        logger.error(f"處理 webhook 時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)

    return Response('OK', status=200)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理收到的文字訊息"""
    try:
        text = event.message.text
        logger.info(f"收到訊息: {text}")
        
        # 從 src 目錄導入處理邏輯
        try:
            from src.message_processor import process_message
            logger.info("成功導入 message_processor 模組")
        except ImportError as e:
            logger.error(f"導入 message_processor 模組時發生錯誤: {str(e)}")
            response = "系統錯誤，請稍後再試。"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
            return
        
        # 處理訊息
        try:
            response = process_message(text)
            logger.info(f"生成回覆: {response}")
        except Exception as e:
            logger.error(f"處理訊息時發生錯誤: {str(e)}")
            logger.error(traceback.format_exc())
            response = "處理訊息時發生錯誤，請稍後再試。"
        
        # 回覆訊息
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
            logger.info("成功發送回覆訊息")
        except LineBotApiError as e:
            logger.error(f"LINE API 錯誤: {str(e)}")
        except Exception as e:
            logger.error(f"發送回覆訊息時發生錯誤: {str(e)}")
            logger.error(traceback.format_exc())
            
    except Exception as e:
        logger.error(f"處理訊息事件時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="處理訊息時發生錯誤，請稍後再試。")
            )
        except Exception as reply_error:
            logger.error(f"發送錯誤回覆時發生錯誤: {str(reply_error)}")

if __name__ == "__main__":
    # 獲取 PORT 環境變數（Render 會提供這個）
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 