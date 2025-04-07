from flask import Blueprint, request, abort, jsonify, current_app
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, 
    URIAction, PostbackEvent, PostbackAction, DatetimePickerAction, QuickReply, 
    QuickReplyButton, MessageAction, FlexSendMessage
)
from ..models import User, Task, Transaction
from ..utils.db import db
import json
import logging
from datetime import datetime, timedelta
import os
from services.task_service import TaskService
from services.finance_service import FinanceService
from services.flex_message_service import FlexMessageService
import urllib.parse

# 創建藍圖
webhook_bp = Blueprint('line_webhook', __name__)

# 日誌
logger = logging.getLogger(__name__)

# 使用預設值初始化，確保不為None
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', 'default_secret'))
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', 'default_token'))

@webhook_bp.before_app_request
def initialize_line_bot():
    """初始化 LINE Bot API 客戶端（若尚未正確初始化）"""
    global handler, line_bot_api
    try:
        channel_secret = current_app.config.get('LINE_CHANNEL_SECRET') or os.environ.get('LINE_CHANNEL_SECRET')
        channel_access_token = current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN') or os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
        
        if not channel_secret or not channel_access_token:
            logger.error("LINE Channel Secret 或 Channel Access Token 未設定")
            return
        
        # 只有當密鑰與當前不同時才重新初始化
        if channel_secret != getattr(handler, 'secret', None):
            handler = WebhookHandler(channel_secret)
            logger.info("LINE WebhookHandler 已重新初始化")
            
        # 只有當令牌與當前不同時才重新初始化
        if channel_access_token != getattr(line_bot_api, 'channel_access_token', None):
            line_bot_api = LineBotApi(channel_access_token)
            logger.info("LINE Bot API 客戶端已重新初始化")
            
    except Exception as e:
        logger.error(f"LINE Bot API 客戶端初始化失敗: {str(e)}")

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """LINE Webhook 回調處理"""
    # 獲取 X-Line-Signature 請求頭
    signature = request.headers.get('X-Line-Signature')
    logger.info('收到 webhook 請求，簽名: %s', signature)
    
    if not signature:
        logger.error("缺少 X-Line-Signature 請求頭")
        abort(400, description="缺少 X-Line-Signature 請求頭")
    
    # 獲取請求體
    body = request.get_data(as_text=True)
    logger.info('請求內容: %s', body)
    
    try:
        # 驗證簽名
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error('無效的簽名')
        return '無效的簽名', 400
    except Exception as e:
        logger.error('處理 webhook 時發生錯誤: %s', str(e))
        return '處理請求時發生錯誤', 500
    
    return 'OK'

# 使用裝飾器函數定義消息處理器
def handle_text_message_wrapper(event):
    """處理文本消息的實際函數"""
    try:
        logger.info('收到文字訊息: %s', event.message.text)
        text = event.message.text
        user_id = event.source.user_id
        logger.info('用戶 ID: %s', user_id)
        
        logger.info(f"收到來自用戶 {user_id} 的消息: {text}")
        
        # 測試回應
        if text == "測試":
            logger.info('處理測試訊息')
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="收到您的測試訊息！")
            )
            return
        
        # 主選單指令 (kimi)
        if text.lower() == "kimi":
            logger.info('處理主選單指令')
            show_menu(event)
            return
        
        # 查找或創建用戶
        user = User.find_by_line_id(user_id)
        if not user:
            try:
                # 獲取用戶資料
                logger.info(f"嘗試獲取用戶 {user_id} 的資料")
                line_user = line_bot_api.get_profile(user_id)
                logger.info(f"成功獲取用戶資料: {line_user.display_name}")
                
                # 創建新用戶
                user = User.create_from_line(user_id, line_user.display_name)
                logger.info(f"成功創建新用戶: {user_id}")
                
                # 發送歡迎消息
                welcome_message = create_welcome_message(line_user.display_name)
                logger.info("準備發送歡迎消息")
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="歡迎使用 Kimi 助手",
                        contents=welcome_message
                    )
                )
                logger.info("歡迎消息發送成功")
                return
            except LineBotApiError as e:
                logger.error(f"獲取 LINE 用戶資料時出錯: {str(e)}")
                send_error_message(event.reply_token, "獲取用戶資料時發生錯誤")
                return
            except Exception as e:
                logger.error(f"創建用戶時出錯: {str(e)}")
                send_error_message(event.reply_token, "創建用戶時發生錯誤")
                return
        
        # 處理用戶指令
        logger.info(f"處理用戶 {user_id} 的指令: {text}")
        handle_user_command(event, text, user)
        
    except Exception as e:
        logger.error('處理文字訊息時發生錯誤: %s', str(e))
        send_error_message(event.reply_token, "處理訊息時發生錯誤")

# 立即註冊處理器
try:
    handler.add(MessageEvent, message=TextMessage)(handle_text_message_wrapper)
    logger.info("成功註冊消息處理器")
except Exception as e:
    logger.error(f"註冊消息處理器時發生錯誤: {str(e)}")

def create_welcome_message(display_name):
    """創建歡迎消息 Flex Message"""
    logger.info('創建歡迎訊息')
    try:
        welcome_message = {
            "type": "flex",
            "altText": "歡迎使用 Kimi 助手",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "歡迎使用 Kimi 助手",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#1DB446"
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{display_name} 您好！",
                            "size": "md",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": "我可以幫您管理任務和財務。",
                            "size": "sm",
                            "wrap": True,
                            "margin": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "新增任務",
                                "text": "新增任務"
                            },
                            "style": "primary",
                            "margin": "sm"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "記錄支出",
                                "text": "記錄支出"
                            },
                            "style": "secondary",
                            "margin": "sm"
                        }
                    ]
                }
            }
        }
        logger.info('歡迎訊息創建成功')
        return welcome_message
    except Exception as e:
        logger.error('創建歡迎訊息時發生錯誤: %s', str(e))
        return TextSendMessage(text="歡迎使用 Kimi 助手！\n您可以使用以下命令：\n• 新增任務 [內容]\n• 查看任務\n• 記錄支出 [內容] [金額]\n• 查看財務")

def send_error_message(reply_token, error_message):
    """發送錯誤消息"""
    logger.error('發送錯誤訊息: %s', error_message)
    try:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"發生錯誤：{error_message}")
        )
    except Exception as e:
        logger.error('發送錯誤訊息時發生錯誤: %s', str(e))

@handler.add(PostbackEvent)
def handle_postback(event):
    """處理 Postback 事件"""
    try:
        user_id = event.source.user_id
        data = event.postback.data
        logger.info(f"收到 Postback: {data} 從用戶: {user_id}")
        
        # 解析 postback 資料
        parsed_data = urllib.parse.parse_qs(data)
        action = parsed_data.get('action', [''])[0]
        
        # 處理任務相關的 postback
        if action.startswith('task_'):
            return handle_task_postback(event, parsed_data)
        
        # 處理財務相關的 postback
        if action.startswith('finance_'):
            return handle_finance_postback(event, parsed_data)
        
        # 其他 postback 處理...
        
    except Exception as e:
        logger.error(f"處理 Postback 時出錯: {str(e)}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="處理您的請求時發生錯誤，請稍後再試。")
        )

def handle_task_postback(event, parsed_data):
    """處理任務相關的 postback"""
    try:
        user_id = event.source.user_id
        action = parsed_data.get('action', [''])[0]
        task_id = parsed_data.get('task_id', [''])[0]
        
        if action == 'task_complete':
            # 完成任務
            success, message = task_service.update_task(
                task_id=task_id,
                user_id=user_id,
                updates={'status': 'completed'}
            )
            
            if success:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="✅ 任務已標記為完成")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"❌ {message}")
                )
        
        elif action == 'task_snooze':
            # 稍後提醒（延後 30 分鐘）
            from datetime import datetime, timedelta
            
            task = task_service.get_task(task_id)
            if task and task.reminder:
                new_reminder_time = datetime.now() + timedelta(minutes=30)
                success, message = task_service.update_task(
                    task_id=task_id,
                    user_id=user_id,
                    updates={
                        'reminder': {
                            'enabled': True,
                            'time': new_reminder_time,
                            'sent': False
                        }
                    }
                )
                
                if success:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"⏰ 已設置在 {new_reminder_time.strftime('%H:%M')} 再次提醒")
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"❌ {message}")
                    )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ 找不到指定的任務")
                )
        
        elif action == 'task_delete':
            # 刪除任務
            success, message = task_service.delete_task(task_id, user_id)
            
            if success:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="🗑️ 任務已刪除")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"❌ {message}")
                )
        
        elif action == 'task_list':
            # 顯示任務列表
            tasks = task_service.get_user_tasks(user_id)
            flex_message = flex_service.create_task_list(tasks)
            
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="任務列表",
                    contents=flex_message.contents
                )
            )
    
    except Exception as e:
        logger.error(f"處理任務 Postback 時出錯: {str(e)}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="處理任務時發生錯誤，請稍後再試。")
        )

def handle_finance_postback(event, parsed_data):
    """處理財務相關的 postback"""
    # 保留原有的財務相關 postback 處理邏輯
    pass

@webhook_bp.route('/notify', methods=['POST'])
def line_notify():
    """發送 LINE 通知"""
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'message' not in data:
            return jsonify({'error': '缺少必要參數'}), 400
        
        user_id = data['user_id']
        message = data['message']
        
        # 查找用戶
        user = User.query.filter_by(id=user_id).first()
        
        if not user or not user.line_user_id:
            return jsonify({'error': '用戶不存在或未綁定 LINE'}), 404
        
        # 發送 LINE 通知
        line_bot_api.push_message(
            user.line_user_id,
            TextSendMessage(text=message)
        )
        
        return jsonify({'message': '通知發送成功'})
    
    except Exception as e:
        logger.error(f"發送 LINE 通知時出錯: {str(e)}")
        return jsonify({'error': '處理通知請求時出錯'}), 500

def handle_user_command(event, text, user):
    """處理用戶指令"""
    try:
        logger.info('處理命令: %s', text)
        command = text.lower()
        
        # 任務指令處理
        if command.startswith("新增任務") or command.startswith("新任務"):
            logger.info("處理新增任務指令")
            handle_add_task(event)
        # 任務查詢指令
        elif command in ["今日任務", "我的任務", "查看任務"]:
            logger.info("處理查看任務指令")
            handle_view_tasks(event, user)
        # 財務記錄指令
        elif command.startswith("記錄支出") or command.startswith("新增支出"):
            logger.info("處理記錄支出指令")
            handle_add_expense(event)
        # 財務查詢指令
        elif command in ["查看財務", "財務摘要", "我的財務"]:
            logger.info("處理查看財務指令")
            handle_view_finance(event, user)
        # 其他指令
        else:
            logger.info("顯示主選單")
            show_menu(event)
    except Exception as e:
        logger.error('處理用戶命令時發生錯誤: %s', str(e))
        send_error_message(event.reply_token, "處理命令時發生錯誤")

def handle_add_task(event):
    """處理新增任務指令"""
    task_template = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "新增任務",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#1DB446"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "請選擇新增任務的方式：",
                    "size": "md",
                    "wrap": True
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "使用網頁版新增",
                        "uri": f"https://liff.line.me/{current_app.config.get('LIFF_ID')}?type=task&action=new"
                    },
                    "style": "primary",
                    "margin": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "快速新增",
                        "data": "action=task_quick_add",
                        "displayText": "快速新增任務"
                    },
                    "style": "secondary",
                    "margin": "sm"
                }
            ]
        }
    }
    
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text="新增任務", contents=task_template)
    )

def handle_view_tasks(event, user):
    """處理查看任務指令"""
    try:
        # 獲取用戶今日任務
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        tasks = Task.find_by_user(
            user_id=str(user['_id']),
            status='pending',
            due_date={'$gte': today, '$lt': tomorrow}
        )
        
        if tasks:
            # 生成任務列表 Flex Message
            task_list_template = create_task_list_template(tasks)
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="今日任務", contents=task_list_template)
            )
        else:
            # 無任務時的 Flex Message
            no_task_template = create_no_task_template()
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="無待辦任務", contents=no_task_template)
            )
    except Exception as e:
        logger.error(f"獲取任務列表時出錯: {str(e)}")
        send_error_message(event.reply_token, "獲取任務列表時發生錯誤")

def create_task_list_template(tasks):
    """創建任務列表 Flex Message 模板"""
    task_contents = []
    
    for i, task in enumerate(tasks, 1):
        priority_color = "#ff0000" if task['priority'] == 2 else "#ff9900" if task['priority'] == 1 else "#0000ff"
        task_time = task['dueDate'].strftime("%H:%M") if task.get('dueDate') else ""
        
        task_contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "●",
                    "color": priority_color,
                    "size": "sm",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": task['title'],
                    "size": "sm",
                    "flex": 8,
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": task_time,
                    "size": "sm",
                    "flex": 3,
                    "align": "end"
                }
            ],
            "margin": "sm"
        })
    
    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "今日待辦任務",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#1DB446"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": task_contents
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "查看所有任務",
                        "uri": f"https://liff.line.me/{current_app.config.get('LIFF_ID')}?type=task"
                    },
                    "style": "primary",
                    "margin": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "新增任務",
                        "data": "action=task_add",
                        "displayText": "新增任務"
                    },
                    "style": "secondary",
                    "margin": "sm"
                }
            ]
        }
    }

def create_no_task_template():
    """創建無任務提示 Flex Message 模板"""
    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "無待辦任務",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#1DB446"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "您今日沒有待辦任務，要新增任務嗎？",
                    "size": "md",
                    "wrap": True
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "使用網頁版新增",
                        "uri": f"https://liff.line.me/{current_app.config.get('LIFF_ID')}?type=task&action=new"
                    },
                    "style": "primary",
                    "margin": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "快速新增",
                        "data": "action=task_quick_add",
                        "displayText": "快速新增任務"
                    },
                    "style": "secondary",
                    "margin": "sm"
                }
            ]
        }
    }

def handle_add_expense(event):
    """處理記錄支出指令"""
    expense_template = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "記錄支出",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#1DB446"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "請選擇記錄方式：",
                    "size": "md",
                    "wrap": True
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "使用網頁版記錄",
                        "uri": f"https://liff.line.me/{current_app.config.get('LIFF_ID')}?type=finance&action=expense"
                    },
                    "style": "primary",
                    "margin": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "快速記錄",
                        "data": "action=expense_quick_add",
                        "displayText": "快速記錄支出"
                    },
                    "style": "secondary",
                    "margin": "sm"
                }
            ]
        }
    }
    
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text="記錄支出", contents=expense_template)
    )

def handle_view_finance(event, user):
    """處理查看財務指令"""
    try:
        # 獲取用戶當月財務摘要
        today = datetime.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = first_day.replace(month=first_day.month + 1) if first_day.month < 12 else first_day.replace(year=first_day.year + 1, month=1)
        
        # 獲取收支統計
        transactions = Transaction.find_by_user(
            user_id=str(user['_id']),
            date={'$gte': first_day, '$lt': next_month}
        )
        
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        balance = total_income - total_expense
        
        # 創建財務摘要 Flex Message
        finance_template = create_finance_summary_template(total_income, total_expense, balance)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="財務摘要", contents=finance_template)
        )
    except Exception as e:
        logger.error(f"獲取財務摘要時出錯: {str(e)}")
        send_error_message(event.reply_token, "獲取財務摘要時發生錯誤")

def create_finance_summary_template(income, expense, balance):
    """創建財務摘要 Flex Message 模板"""
    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "本月財務摘要",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#1DB446"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "收入",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": f"${income:,.2f}",
                            "size": "sm",
                            "color": "#111111",
                            "align": "end",
                            "flex": 2
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "支出",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": f"${expense:,.2f}",
                            "size": "sm",
                            "color": "#111111",
                            "align": "end",
                            "flex": 2
                        }
                    ],
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "結餘",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": f"${balance:,.2f}",
                            "size": "sm",
                            "color": "#111111",
                            "align": "end",
                            "flex": 2
                        }
                    ],
                    "margin": "md"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "查看詳細報表",
                        "uri": f"https://liff.line.me/{current_app.config.get('LIFF_ID')}?type=finance"
                    },
                    "style": "primary",
                    "margin": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "記錄支出",
                        "data": "action=expense_add",
                        "displayText": "記錄支出"
                    },
                    "style": "secondary",
                    "margin": "sm"
                }
            ]
        }
    }

def show_menu(event):
    """顯示主選單"""
    menu_template = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FFC940",
            "paddingAll": "10px",
            "contents": [
                {
                    "type": "text",
                    "text": "Kimi 助手主選單",
                    "color": "#FFFFFF",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FFFBE6",
            "paddingAll": "15px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#FFC940",
                    "action": {
                        "type": "message",
                        "label": "任務管理",
                        "text": "任務管理"
                    },
                    "height": "sm",
                    "margin": "md"
                },
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#FAAD14",
                    "action": {
                        "type": "message",
                        "label": "記錄支出",
                        "text": "記錄支出"
                    },
                    "height": "sm",
                    "margin": "md"
                },
                {
                    "type": "button",
                    "style": "primary", 
                    "color": "#FFE58F",
                    "action": {
                        "type": "message",
                        "label": "記錄收入",
                        "text": "記錄收入"
                    },
                    "height": "sm",
                    "margin": "md"
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "查看今日記錄",
                        "text": "今日收支"
                    },
                    "height": "sm",
                    "margin": "md"
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "查看本月記錄",
                        "text": "本月收支"
                    },
                    "height": "sm",
                    "margin": "md"
                },
                {
                    "type": "button",
                    "style": "link",
                    "color": "#8C8C8C",
                    "action": {
                        "type": "message",
                        "label": "幫助",
                        "text": "kimi help"
                    },
                    "height": "sm",
                    "margin": "md"
                }
            ]
        }
    }
    
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text="Kimi 助手主選單", contents=menu_template)
    )