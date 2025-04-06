"""
主要的訊息處理模組
用於接收和處理 LINE Bot 的訊息
"""
import os
import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, MessageAction
)

# 導入服務模組
from services.finance_service import FinanceService
from services.note_service import NoteService

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))

def process_message(event):
    """處理收到的訊息"""
    try:
        user_id = event.source.user_id
        message_text = event.message.text
        logger.info(f"收到訊息: {message_text} 從用戶: {user_id}")
        
        # 處理幫助命令
        if message_text.lower() in ['help', '幫助', '說明']:
            return handle_help_command(user_id)
        
        # 處理初始化命令
        if message_text.lower() in ['初始化', 'init']:
            return FinanceService.initialize_user(user_id)
        
        # 嘗試處理財務相關命令
        finance_response = FinanceService.process_finance_command(message_text, user_id)
        if finance_response:
            return finance_response
        
        # 嘗試處理筆記相關命令
        note_response = NoteService.process_note_command(message_text, user_id)
        if note_response:
            return note_response
        
        # 如果沒有匹配的命令格式，返回幫助信息
        return "抱歉，我無法理解您的命令。請嘗試使用以下格式：\n" + get_help_text()
    
    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {str(e)}")
        return "處理您的請求時發生錯誤，請稍後再試。"

def handle_help_command(user_id):
    """處理幫助命令，返回使用說明"""
    return get_help_text()

def get_help_text():
    """獲取幫助文本"""
    help_text = [
        "📝 使用說明 📝",
        "=== 記帳功能 ===",
        "記錄支出：早餐50 或 午餐120 麥當勞",
        "記錄收入：收入5000 薪資",
        "查詢記錄：今天 或 本週 或 本月",
        "查看統計：月報 或 月報2023-5",
        "",
        "=== 筆記功能 ===",
        "添加筆記：筆記 標題\n內容 #標籤1 #標籤2",
        "查看列表：筆記列表 或 筆記列表 #標籤",
        "查看詳情：筆記 ID",
        "更新筆記：筆記更新 ID 新標題\n新內容 #新標籤",
        "刪除筆記：筆記刪除 ID",
        "",
        "=== 提醒功能 ===",
        "添加提醒：提醒 內容 2023-5-20 14:30 每週",
        "查看提醒：提醒列表 或 所有提醒",
        "完成提醒：提醒完成 ID",
        "刪除提醒：提醒刪除 ID",
        "",
        "初始化功能：初始化"
    ]
    return "\n".join(help_text)

def create_monthly_report_flex(report_data, year, month):
    """創建月度報告的 Flex 訊息"""
    total_expense = report_data['total_expense']
    total_income = report_data['total_income']
    expense_by_category = report_data['expense_by_category']
    income_by_category = report_data['income_by_category']
    
    # 構建支出分類列表
    expense_items = []
    for category in expense_by_category:
        expense_items.append(
            BoxComponent(
                layout="horizontal",
                spacing="sm",
                contents=[
                    TextComponent(text=f"{category['name']}", size="sm", color="#555555", flex=0),
                    TextComponent(text=f"${category['amount']}", size="sm", color="#111111", align="end")
                ]
            )
        )
    
    # 構建收入分類列表
    income_items = []
    for category in income_by_category:
        income_items.append(
            BoxComponent(
                layout="horizontal",
                spacing="sm",
                contents=[
                    TextComponent(text=f"{category['name']}", size="sm", color="#555555", flex=0),
                    TextComponent(text=f"${category['amount']}", size="sm", color="#111111", align="end")
                ]
            )
        )
    
    # 創建 Flex 訊息
    bubble = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                # 標題
                TextComponent(text=f"{year}年{month}月財務報告", weight="bold", size="xl"),
                # 分隔線
                BoxComponent(layout="vertical", margin="md", height="1px", backgroundColor="#CCCCCC"),
                # 總計
                BoxComponent(
                    layout="vertical",
                    margin="md",
                    spacing="sm",
                    contents=[
                        BoxComponent(
                            layout="horizontal",
                            contents=[
                                TextComponent(text="總支出", size="md", color="#555555"),
                                TextComponent(text=f"${total_expense}", size="md", color="#dd0000", align="end")
                            ]
                        ),
                        BoxComponent(
                            layout="horizontal",
                            contents=[
                                TextComponent(text="總收入", size="md", color="#555555"),
                                TextComponent(text=f"${total_income}", size="md", color="#00dd00", align="end")
                            ]
                        ),
                        BoxComponent(
                            layout="horizontal",
                            contents=[
                                TextComponent(text="結餘", size="md", color="#555555", weight="bold"),
                                TextComponent(
                                    text=f"${total_income - total_expense}", 
                                    size="md", 
                                    color="#0000dd" if total_income >= total_expense else "#dd0000", 
                                    align="end",
                                    weight="bold"
                                )
                            ]
                        )
                    ]
                ),
                # 分隔線
                BoxComponent(layout="vertical", margin="md", height="1px", backgroundColor="#CCCCCC"),
                # 支出詳情
                TextComponent(text="支出明細", weight="bold", size="md", margin="md"),
                BoxComponent(
                    layout="vertical",
                    margin="sm",
                    spacing="sm",
                    contents=expense_items
                ),
                # 分隔線
                BoxComponent(layout="vertical", margin="md", height="1px", backgroundColor="#CCCCCC"),
                # 收入詳情
                TextComponent(text="收入明細", weight="bold", size="md", margin="md"),
                BoxComponent(
                    layout="vertical",
                    margin="sm",
                    spacing="sm",
                    contents=income_items
                )
            ]
        ),
        footer=BoxComponent(
            layout="vertical",
            spacing="sm",
            contents=[
                ButtonComponent(
                    style="primary",
                    action=MessageAction(label="查看本月交易", text="本月"),
                    color="#1DB446"
                )
            ]
        )
    )
    
    return FlexSendMessage(alt_text=f"{year}年{month}月財務報告", contents=bubble)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理 LINE 平台的訊息事件"""
    response = process_message(event)
    
    # 檢查是否為 FlexSendMessage 類型
    if isinstance(response, FlexSendMessage):
        line_bot_api.reply_message(event.reply_token, response)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

def create_app(test_config=None):
    """創建 Flask 應用"""
    app = Flask(__name__, instance_relative_config=True)
    
    @app.route("/", methods=["GET"])
    def home():
        """首頁路由"""
        return "Financial Bot Server is running!"
    
    @app.route("/webhook", methods=["POST"])
    def webhook():
        """LINE 的 Webhook 接收端點"""
        signature = request.headers.get("X-Line-Signature", "")
        body = request.get_data(as_text=True)
        logger.info("收到 Webhook 請求：%s", body)
        
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error("無效的簽名")
            abort(400)
        
        return "OK"
    
    return app 