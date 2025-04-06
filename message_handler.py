"""
主要的訊息處理模組
用於接收和處理 LINE Bot 的訊息
"""
import os
import logging
import urllib.parse
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, MessageAction,
    PostbackEvent, PostbackAction
)

# 導入服務模組
from services.finance_service import FinanceService
from services.note_service import NoteService
from services.flex_message_service import FlexMessageService

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))

# 用於暫存用戶的輸入狀態
user_states = {}

def process_message(event):
    """處理收到的訊息"""
    try:
        user_id = event.source.user_id
        message_text = event.message.text
        logger.info(f"收到訊息: {message_text} 從用戶: {user_id}")
        
        # 檢查用戶是否處於特定狀態（例如等待輸入金額）
        if user_id in user_states:
            state = user_states[user_id]
            if state.get('waiting_for') == 'amount':
                # 用戶正在輸入金額
                try:
                    amount = int(message_text)
                    return handle_amount_input(user_id, amount, state)
                except ValueError:
                    return "請輸入有效的數字金額。"
            elif state.get('waiting_for') == 'note':
                # 用戶正在輸入備註
                return handle_note_input(user_id, message_text, state)
            elif state.get('waiting_for') == 'custom_category':
                # 用戶正在輸入自定義類別
                return handle_custom_category(user_id, message_text, state)
            elif state.get('waiting_for') == 'new_account':
                # 用戶正在輸入新帳戶名稱
                return handle_new_account(user_id, message_text, state)
            elif state.get('waiting_for') == 'keypad_input':
                # 用戶已在使用數字鍵盤，直接將輸入作為完整金額
                try:
                    amount = int(message_text)
                    transaction_type = state.get('type')
                    category = state.get('category')
                    # 清除用戶狀態
                    del user_states[user_id]
                    # 繼續到帳戶選擇
                    return FlexMessageService.create_account_selection(user_id, transaction_type, category, amount)
                except ValueError:
                    return "請輸入有效的數字金額。"
        
        # 處理特殊命令
        if message_text.lower() == 'flex':
            # 顯示 Flex 記帳選單
            return FlexMessageService.create_main_menu()
        
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

def handle_amount_input(user_id, amount, state):
    """處理用戶輸入的金額"""
    transaction_type = state.get('type')
    category = state.get('category')
    
    # 清除用戶狀態
    del user_states[user_id]
    
    # 繼續到帳戶選擇
    return FlexMessageService.create_account_selection(user_id, transaction_type, category, amount)

def handle_note_input(user_id, note, state):
    """處理用戶輸入的備註"""
    transaction_type = state.get('type')
    category = state.get('category')
    amount = state.get('amount')
    account = state.get('account')
    
    # 清除用戶狀態
    del user_states[user_id]
    
    # 添加交易記錄
    is_expense = transaction_type == 'expense'
    response = FinanceService.add_transaction(
        user_id=user_id,
        amount=amount,
        category_name=category,
        note=note,
        account_name=account,
        is_expense=is_expense
    )
    
    # 返回確認訊息
    return FlexMessageService.create_confirmation(transaction_type, category, amount, account, note)

def handle_custom_category(user_id, category_name, state):
    """處理用戶輸入的自定義類別"""
    transaction_type = state.get('type')
    is_expense = transaction_type == 'expense'
    
    # 添加類別到資料庫
    from models import db, Category
    new_category = Category(
        user_id=user_id,
        name=category_name,
        icon="📝" if is_expense else "💴",
        is_expense=is_expense
    )
    db.session.add(new_category)
    db.session.commit()
    
    # 清除用戶狀態
    del user_states[user_id]
    
    # 繼續到金額輸入
    return FlexMessageService.create_amount_input(transaction_type, category_name)

def handle_new_account(user_id, account_name, state):
    """處理用戶輸入的新帳戶名稱"""
    # 添加帳戶到資料庫
    from models import db, Account
    new_account = Account(
        user_id=user_id,
        name=account_name,
        balance=0,
        currency="TWD",
        account_type="cash"
    )
    db.session.add(new_account)
    db.session.commit()
    
    # 檢查狀態類型
    if state.get('type') == 'transfer':
        # 如果是轉帳，返回轉帳選單
        del user_states[user_id]
        return FlexMessageService.create_transfer_menu(user_id)
    else:
        # 繼續交易流程
        transaction_type = state.get('type')
        category = state.get('category')
        amount = state.get('amount')
        
        # 清除用戶狀態
        del user_states[user_id]
        
        if amount:
            # 如果已有金額，顯示帳戶選擇
            return FlexMessageService.create_account_selection(user_id, transaction_type, category, amount)
        else:
            # 如果在類別選擇階段添加帳戶，返回主選單
            return FlexMessageService.create_main_menu()

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
        "互動記帳：輸入 flex 啟動互動式記帳",
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

@handler.add(PostbackEvent)
def handle_postback(event):
    """處理 Postback 事件"""
    user_id = event.source.user_id
    data = event.postback.data
    logger.info(f"Postback: {data} 從用戶: {user_id}")
    
    # 解析 postback 數據
    parsed_data = {}
    for pair in data.split('&'):
        key, value = pair.split('=')
        parsed_data[key] = urllib.parse.unquote(value)
    
    action = parsed_data.get('action')
    
    if action == 'main_menu':
        # 顯示主選單
        response = FlexMessageService.create_main_menu()
    
    elif action == 'record':
        # 開始記帳流程，顯示類別選擇
        transaction_type = parsed_data.get('type')
        if transaction_type == 'transfer':
            response = FlexMessageService.create_transfer_menu(user_id)
        else:
            response = FlexMessageService.create_category_selection(user_id, transaction_type)
    
    elif action == 'category':
        # 選擇了類別，顯示金額輸入
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category')
        response = FlexMessageService.create_amount_input(transaction_type, category)
    
    elif action == 'custom_category':
        # 等待用戶輸入自定義類別
        transaction_type = parsed_data.get('type')
        user_states[user_id] = {
            'waiting_for': 'custom_category',
            'type': transaction_type
        }
        response = TextSendMessage(text="請輸入自定義類別名稱：")
    
    elif action == 'keypad':
        # 處理數字鍵盤輸入
        key = parsed_data.get('key')
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category')
        
        # 獲取當前金額（如果有）
        current_amount = user_states.get(user_id, {}).get('current_amount', '')
        
        if key == 'backspace':
            # 刪除最後一個字符
            if current_amount:
                current_amount = current_amount[:-1]
        else:
            # 添加數字
            current_amount += key
        
        # 更新用戶狀態
        user_states[user_id] = {
            'waiting_for': 'keypad_input',
            'type': transaction_type,
            'category': category,
            'current_amount': current_amount
        }
        
        # 創建一個顯示當前金額的 Flex 訊息
        if not current_amount:
            # 如果金額為空，返回數字鍵盤
            response = FlexMessageService.create_amount_input(transaction_type, category)
        else:
            # 自定義金額顯示訊息
            is_expense = transaction_type == "expense"
            type_text = "支出" if is_expense else "收入"
            type_color = "#FF6B6E" if is_expense else "#27ACB2"
            
            bubble = BubbleContainer(
                header=BoxComponent(
                    layout="vertical",
                    backgroundColor=type_color,
                    paddingAll="10px",
                    contents=[
                        TextComponent(
                            text=f"{type_text}金額",
                            color="#FFFFFF",
                            weight="bold",
                            size="lg",
                            align="center"
                        ),
                        TextComponent(
                            text=f"類別：{category}",
                            color="#FFFFFF",
                            size="sm",
                            align="center",
                            margin="xs"
                        )
                    ]
                ),
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(
                            text=f"目前輸入: ${current_amount}",
                            size="xl",
                            weight="bold",
                            align="center",
                            margin="md",
                            color=type_color
                        ),
                        TextComponent(
                            text="繼續輸入，或直接發送數字以確認金額",
                            size="sm",
                            color="#888888",
                            align="center",
                            margin="sm"
                        ),
                        BoxComponent(
                            layout="horizontal",
                            margin="xl",
                            contents=[
                                ButtonComponent(
                                    style="primary",
                                    color=type_color,
                                    action=PostbackAction(
                                        label="確認金額",
                                        display_text=f"金額：{current_amount}",
                                        data=f"action=amount&type={transaction_type}&category={category}&amount={current_amount}"
                                    ),
                                    height="sm"
                                ),
                                ButtonComponent(
                                    style="secondary",
                                    action=PostbackAction(
                                        label="重新輸入",
                                        display_text="重新輸入金額",
                                        data=f"action=back_to_amount&type={transaction_type}&category={category}"
                                    ),
                                    height="sm",
                                    margin="md"
                                )
                            ]
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout="vertical",
                    contents=[
                        ButtonComponent(
                            style="secondary",
                            action=PostbackAction(
                                label="返回類別選擇",
                                display_text="返回類別選擇",
                                data=f"action=back_to_category&type={transaction_type}"
                            ),
                            height="sm"
                        )
                    ]
                )
            )
            
            response = FlexSendMessage(alt_text="輸入金額", contents=bubble)
    
    elif action == 'amount':
        # 選擇了金額，顯示帳戶選擇
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category')
        amount = int(parsed_data.get('amount'))
        response = FlexMessageService.create_account_selection(user_id, transaction_type, category, amount)
    
    elif action == 'account':
        # 選擇了帳戶，顯示備註輸入
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category')
        amount = int(parsed_data.get('amount'))
        account = parsed_data.get('account')
        response = FlexMessageService.create_note_input(transaction_type, category, amount, account)
    
    elif action == 'new_account':
        # 等待用戶輸入新帳戶名稱
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category', None)
        amount = parsed_data.get('amount', None)
        if amount:
            amount = int(amount)
        
        user_states[user_id] = {
            'waiting_for': 'new_account',
            'type': transaction_type,
            'category': category,
            'amount': amount
        }
        response = TextSendMessage(text="請輸入新帳戶名稱：")
    
    elif action == 'finish':
        # 完成記帳
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category')
        amount = int(parsed_data.get('amount'))
        account = parsed_data.get('account')
        note = parsed_data.get('note', None)
        
        # 添加交易記錄
        is_expense = transaction_type == 'expense'
        FinanceService.add_transaction(
            user_id=user_id,
            amount=amount,
            category_name=category,
            note=note,
            account_name=account,
            is_expense=is_expense
        )
        
        # 返回確認訊息
        response = FlexMessageService.create_confirmation(transaction_type, category, amount, account, note)
    
    elif action == 'back_to_category':
        # 返回類別選擇
        transaction_type = parsed_data.get('type')
        response = FlexMessageService.create_category_selection(user_id, transaction_type)
    
    elif action == 'back_to_amount':
        # 返回金額輸入
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category')
        response = FlexMessageService.create_amount_input(transaction_type, category)
    
    elif action == 'back_to_account':
        # 返回帳戶選擇
        transaction_type = parsed_data.get('type')
        category = parsed_data.get('category')
        amount = int(parsed_data.get('amount'))
        response = FlexMessageService.create_account_selection(user_id, transaction_type, category, amount)
    
    elif action == 'transfer_from':
        # 選擇了轉出帳戶，處理轉帳邏輯
        # 此處省略轉帳邏輯的實現，可以按照類似記帳的流程來實現
        response = TextSendMessage(text="轉帳功能正在開發中...")
    
    else:
        # 未知的 action
        response = TextSendMessage(text="未知的操作，請重試。")
    
    # 回覆訊息
    if isinstance(response, FlexSendMessage) or isinstance(response, TextSendMessage):
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