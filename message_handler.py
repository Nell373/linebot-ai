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
from datetime import datetime, timedelta

# 導入服務模組
from services.finance_service import FinanceService
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
        
        # 檢查是否是快速支出命令（例如：早餐-500）
        quick_expense = FinanceService.parse_quick_expense_command(message_text)
        if quick_expense:
            logger.info(f"檢測到快速支出命令: {quick_expense}")
            # 直接處理快速支出流程，在選類別時自動帶入備註
            return FinanceService.prepare_quick_expense(
                user_id=user_id,
                amount=quick_expense['amount'],
                category_keyword=quick_expense['category_keyword'],
                note=quick_expense['note']  # 將類別名稱作為備註
            )
        
        # 檢查用戶是否處於特定狀態（例如等待輸入金額）
        if user_id in user_states:
            state = user_states[user_id]
            if state.get('waiting_for') == 'amount':
                # 用戶正在輸入金額
                try:
                    amount = float(message_text)  # 使用 float 而不是 int 來支持小數金額
                    logger.info(f"用戶 {user_id} 輸入金額: {amount}")
                    return handle_amount_input(user_id, amount, state)
                except ValueError:
                    # 嘗試檢查是否包含逗號或其他非數字字符
                    try:
                        # 移除逗號、空格等字符
                        cleaned_text = message_text.replace(',', '').replace(' ', '')
                        amount = float(cleaned_text)
                        logger.info(f"用戶 {user_id} 輸入經過清理的金額: {amount}")
                        return handle_amount_input(user_id, amount, state)
                    except ValueError:
                        return "請輸入有效的數字金額，例如: 100 或 1,234.56"
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
        if message_text.lower() == 'kimi':
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
        "互動操作：輸入 kimi 啟動互動式選單",
        "",
        "=== 任務功能 ===",
        "添加任務：任務 任務內容 #標籤1 #標籤2",
        "查看列表：任務列表 或 任務列表 #標籤",
        "查看詳情：任務 ID",
        "更新狀態：任務完成 ID",
        "刪除任務：任務刪除 ID",
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
    try:
        response = process_message(event)
        logger.info(f"處理用戶 {event.source.user_id} 的訊息，準備回應")
        
        # 檢查是否為 FlexSendMessage 類型
        if isinstance(response, FlexSendMessage):
            line_bot_api.reply_message(event.reply_token, response)
            logger.info(f"已發送 Flex 訊息回應給用戶 {event.source.user_id}")
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
            logger.info(f"已發送文字訊息回應給用戶 {event.source.user_id}: {response[:30]}...")
    
    except Exception as e:
        logger.error(f"回應訊息時發生錯誤: {str(e)}")
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="處理您的請求時發生錯誤，請稍後再試。"))
        except:
            logger.error("無法發送錯誤訊息")

@handler.add(PostbackEvent)
def handle_postback(event):
    """處理收到的 Postback 事件"""
    try:
        user_id = event.source.user_id
        postback_data = event.postback.data
        logger.info(f"收到 Postback: {postback_data} 從用戶: {user_id}")
        
        # 防止重複處理同一個請求
        # 使用 user_id + postback_data 作為唯一鍵
        request_key = f"{user_id}:{postback_data}"
        
        # 檢查處理請求歷史（使用模組級別的字典）
        if not hasattr(handle_postback, 'processed_requests'):
            handle_postback.processed_requests = {}
            
        # 如果是短時間內的重複請求，則忽略
        current_time = datetime.now()
        if request_key in handle_postback.processed_requests:
            last_process_time = handle_postback.processed_requests[request_key]
            # 如果距離上次處理相同請求的時間不足3秒，視為重複請求
            if (current_time - last_process_time).total_seconds() < 3:
                logger.warning(f"檢測到重複請求: {request_key}，已忽略")
                return
        
        # 記錄當前請求的處理時間
        handle_postback.processed_requests[request_key] = current_time
        
        # 清理過期的請求記錄（保留最近10分鐘的記錄）
        expired_time = current_time - timedelta(minutes=10)
        handle_postback.processed_requests = {k: v for k, v in handle_postback.processed_requests.items() 
                                             if v > expired_time}
        
        # 解析 postback 數據
        params = dict(urllib.parse.parse_qsl(postback_data))
        action = params.get('action')
        
        # 處理各種 action
        response = None
        
        if action == 'record':
            # 記錄交易流程開始
            transaction_type = params.get('type')
            response = FlexMessageService.create_category_selection(user_id, transaction_type)
        
        elif action == 'category':
            # 用戶選擇了類別
            transaction_type = params.get('type')
            category = params.get('category')
            
            # 保存用戶狀態
            user_states[user_id] = {
                'type': transaction_type,
                'category': category,
                'waiting_for': 'amount'  # 添加等待輸入金額的狀態標記
            }
            
            # 轉到金額輸入
            response = FlexMessageService.create_amount_input(transaction_type, category)
        
        elif action == 'amount':
            # 用戶輸入完金額
            transaction_type = params.get('type')
            category = params.get('category')
            amount = float(params.get('amount'))
            
            # 更新用戶狀態
            user_states[user_id] = {
                'type': transaction_type,
                'category': category,
                'amount': amount
            }
            
            # 轉到帳戶選擇
            response = FlexMessageService.create_account_selection(user_id, transaction_type, category, amount)
        
        elif action == 'account':
            # 用戶選擇了帳戶
            transaction_type = params.get('type')
            category = params.get('category')
            amount = float(params.get('amount'))
            account = params.get('account')
            
            # 更新用戶狀態
            user_states[user_id] = {
                'type': transaction_type,
                'category': category,
                'amount': amount,
                'account': account,
                'waiting_for': 'note'
            }
            
            # 詢問備註
            response = "請輸入備註（如不需要，請輸入「無」）："
        
        elif action == 'quick_expense':
            # 用戶在快速支出界面選擇了類別
            category = params.get('category')
            amount = float(params.get('amount'))
            note = params.get('note')  # 獲取備註，可能為None
            
            # 記錄操作
            logger.info(f"用戶 {user_id} 執行快速支出：{category} ${amount} 備註:{note}")
            
            # 直接添加交易記錄
            add_result = FinanceService.add_transaction(
                user_id=user_id,
                amount=amount,
                category_name=category,
                note=note,  # 使用備註，可能為None
                account_name="默認",
                is_expense=True
            )
            logger.info(f"交易記錄結果: {add_result}")
            
            # 返回確認訊息
            response = FlexMessageService.create_confirmation("expense", category, amount, "默認", note)
        
        elif action == 'create_category':
            # 用戶選擇創建新類別
            name = params.get('name')
            is_expense = params.get('is_expense') == 'true'
            amount = params.get('amount')
            
            # 創建新類別
            from models import db, Category
            icon = "📝" if is_expense else "💴"
            new_category = Category(
                user_id=user_id,
                name=name,
                icon=icon,
                is_expense=is_expense
            )
            db.session.add(new_category)
            db.session.commit()
            logger.info(f"為用戶 {user_id} 創建新類別: {name}")
            
            if amount:
                # 如果是通過快速支出創建的類別，直接添加交易記錄
                amount_float = float(amount)
                add_result = FinanceService.add_transaction(
                    user_id=user_id,
                    amount=amount_float,
                    category_name=name,
                    note=None,
                    account_name="默認",
                    is_expense=is_expense
                )
                logger.info(f"交易記錄結果: {add_result}")
                
                # 返回確認訊息
                response = FlexMessageService.create_confirmation("expense", name, amount_float, "默認", None)
            else:
                # 否則回到主選單
                response = FlexMessageService.create_main_menu()
        
        elif action == 'custom_category':
            # 用戶要創建自定義類別
            transaction_type = params.get('type')
            quick_expense = params.get('quick_expense') == 'true'
            amount = params.get('amount')
            
            # 更新用戶狀態
            state = {
                'type': transaction_type,
                'waiting_for': 'custom_category'
            }
            
            if quick_expense and amount:
                state['quick_expense'] = True
                state['amount'] = float(amount)
                
            user_states[user_id] = state
            
            # 提示輸入類別名稱
            response = "請輸入新的類別名稱："
        
        elif action == 'new_account':
            # 用戶要創建新帳戶
            transaction_type = params.get('type')
            amount = params.get('amount')
            category = params.get('category')
            
            # 更新用戶狀態
            state = {
                'type': transaction_type,
                'waiting_for': 'new_account'
            }
            
            if amount:
                state['amount'] = float(amount)
            
            if category:
                state['category'] = category
                
            user_states[user_id] = state
            
            # 提示輸入帳戶名稱
            response = "請輸入新的帳戶名稱："
        
        elif action == 'skip_note':
            # 用戶跳過輸入備註
            transaction_type = params.get('type')
            category = params.get('category')
            amount = float(params.get('amount'))
            account = params.get('account')
            
            # 添加交易記錄
            is_expense = transaction_type == 'expense'
            add_result = FinanceService.add_transaction(
                user_id=user_id,
                amount=amount,
                category_name=category,
                note=None,
                account_name=account,
                is_expense=is_expense
            )
            logger.info(f"交易記錄結果: {add_result}")
            
            # 返回確認訊息
            response = FlexMessageService.create_confirmation(transaction_type, category, amount, account, None)
        
        elif action == 'cancel':
            # 用戶取消操作
            if user_id in user_states:
                del user_states[user_id]
            
            response = "已取消當前操作。"
        
        elif action == 'task_menu':
            # 顯示任務管理選單
            # 這裡可以根據需要添加任務管理的功能
            response = "任務管理功能即將推出，敬請期待！"
        
        elif action == 'main_menu':
            # 返回主選單
            response = FlexMessageService.create_main_menu()
        
        else:
            response = "未知的操作。"
        
        # 發送回覆
        if response:
            logger.info(f"準備回覆用戶 {user_id}")
            if isinstance(response, FlexSendMessage):
                line_bot_api.reply_message(event.reply_token, response)
                logger.info(f"已發送 Flex 訊息回應給用戶 {user_id}")
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
                logger.info(f"已發送文字訊息回應給用戶 {user_id}: {response[:30]}...")
        else:
            logger.warning(f"沒有對用戶 {user_id} 的回應")
    
    except Exception as e:
        logger.error(f"處理 Postback 時發生錯誤: {str(e)}", exc_info=True)
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="處理您的請求時發生錯誤，請稍後再試。"))
        except:
            logger.error("無法發送錯誤訊息")

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