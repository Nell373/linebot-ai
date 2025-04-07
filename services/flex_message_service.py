"""
Flex Message服務模組
創建互動式記帳流程的Flex Message

色彩方案：
🌟 主色 Primary：#FFC940 - 用於主按鈕、高亮區、品牌識別主色
🌞 輔助亮黃：#FFE58F - 用於 hover 狀態、背景滑過區域
🍋 強調亮點黃：#FAAD14 - 用於 icon 點綴、高注意力元素
⚪ 背景色：#FFFFFF - 清爽主背景
🟡 淡黃背景區塊：#FFFBE6 - 卡片、模組背景
🩶 主文字色：#595959 - 內文標題、主要資訊文字
⚪ 次要文字色：#8C8C8C - 備註、說明、次層資訊
⬜ 邊框用灰：#D9D9D9 - 輸入框、卡片、表格邊線、分隔線
"""
import logging
import os
from datetime import datetime, timedelta
from linebot.models import (
    FlexSendMessage,
    BubbleContainer,
    BoxComponent,
    TextComponent,
    ButtonComponent,
    IconComponent,
    SeparatorComponent,
    CarouselContainer,
    QuickReply,
    QuickReplyButton,
    PostbackAction,
    MessageAction,
    URIAction
)
from app.models import Category, User, Account, db
import urllib.parse

logger = logging.getLogger(__name__)

# 從環境變數獲取 LIFF 設定
LIFF_ID = os.environ.get('LIFF_ID', '2007212914-e3vNnYno')
LIFF_CHANNEL_SECRET = os.environ.get('LIFF_CHANNEL_SECRET', '')
# 使用正確的 LIFF URL
LIFF_URL = f"https://liff.line.me/{LIFF_ID}"

logger.info(f"使用 LIFF URL: {LIFF_URL}")
logger.info(f"LIFF Channel Secret 設定狀態: {'已設定' if LIFF_CHANNEL_SECRET else '未設定'}")

class FlexMessageService:
    """Flex Message 服務類"""
    
    def __init__(self):
        """初始化 Flex Message 服務"""
        self.liff_id = os.environ.get('LIFF_ID', '')
        self.liff_url = f"https://liff.line.me/{self.liff_id}" if self.liff_id else ""
        self.liff_channel_secret = os.environ.get('LIFF_CHANNEL_SECRET', '')
        
        logger.info(f"使用 LIFF URL: {self.liff_url}")
        logger.info(f"LIFF Channel Secret 設定狀態: {'已設定' if self.liff_channel_secret else '未設定'}")

    def create_main_menu(self):
        """創建主選單"""
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "主選單",
                        "weight": "bold",
                        "size": "xl"
                    }
                ]
            }
        }
        return FlexSendMessage(alt_text="主選單", contents=bubble)

    def create_task_menu(self):
        """創建任務管理選單"""
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "任務管理",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#555555"
                    },
                    {
                        "type": "text",
                        "text": "請選擇操作",
                        "color": "#888888",
                        "size": "md",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "color": "#FAAD14",
                                "action": {
                                    "type": "uri",
                                    "label": "新增任務",
                                    "uri": f"{self.liff_url}?action=create_task"
                                }
                            },
                            {
                                "type": "button",
                                "style": "secondary",
                                "action": {
                                    "type": "uri",
                                    "label": "查看任務",
                                    "uri": f"{self.liff_url}?action=view_tasks"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        return FlexSendMessage(alt_text="任務管理選單", contents=bubble)

    @staticmethod
    def create_category_selection(user_id, transaction_type):
        """創建類別選擇選單"""
        categories = []
        
        # 支出與收入類別 (簡易版)
        if transaction_type == "expense":
            categories = [
                {"name": "餐飲", "color": "#FF9800"},
                {"name": "交通", "color": "#03A9F4"},
                {"name": "購物", "color": "#E91E63"},
                {"name": "娛樂", "color": "#9C27B0"},
                {"name": "居家", "color": "#8BC34A"},
                {"name": "其它", "color": "#607D8B"}
            ]
        else:  # income
            categories = [
                {"name": "薪資", "color": "#4CAF50"},
                {"name": "獎金", "color": "#FFC107"},
                {"name": "理財", "color": "#3F51B5"},
                {"name": "其它", "color": "#607D8B"}
            ]
        
        # 建立類別按鈕
        category_buttons = []
        for i, category in enumerate(categories):
            button = {
                "type": "button",
                "style": "primary",
                "color": category["color"],
                "action": {
                    "type": "message",
                    "label": category["name"],
                    "text": category["name"]
                },
                "height": "sm",
                "margin": "sm" if i > 0 else "none"
            }
            category_buttons.append(button)
        
        # 添加自定義類別按鈕
        category_buttons.append({
            "type": "button",
            "style": "secondary",
            "action": {
                "type": "message",
                "label": "自定義類別",
                "text": "自定義類別"
            },
            "height": "sm",
            "margin": "md"
        })
        
        # 創建 Flex 消息
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "選擇類別",
                        "weight": "bold",
                        "size": "xl"
                    },
                    {
                        "type": "text",
                        "text": "支出" if transaction_type == "expense" else "收入",
                        "color": "#888888",
                        "size": "md",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": category_buttons
                    }
                ]
            }
        }
        
        return FlexSendMessage(alt_text="選擇類別", contents=bubble)

    @staticmethod
    def create_amount_input(transaction_type, category):
        """創建金額輸入選單"""
        is_expense = transaction_type == "expense"
        type_text = "支出" if is_expense else "收入"
        type_color = "#FAAD14" if is_expense else "#FFC940"  # 強調亮點黃/主色 Primary
        
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": type_color,
                "paddingAll": "10px",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{type_text}金額",
                        "color": "#FFFFFF",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"類別：{category}",
                        "color": "#FFFFFF",
                        "size": "sm",
                        "align": "center",
                        "margin": "xs"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#FFFBE6",  # 淡黃背景區塊
                "contents": [
                    {
                        "type": "text",
                        "text": "請直接輸入金額數字",
                        "size": "md",
                        "color": "#8C8C8C",  # 次要文字色
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "例如：150、1000、33000",
                        "size": "sm",
                        "color": "#8C8C8C",  # 次要文字色
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": "或使用快速格式：早餐-50、薪資+5000",
                        "size": "sm",
                        "color": "#8C8C8C",  # 次要文字色
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "contents": [
                            {
                                "type": "text",
                                "text": "請在下方輸入框中直接輸入金額",
                                "size": "md", 
                                "weight": "bold",
                                "align": "center",
                                "color": "#595959"  # 主文字色
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#FFFBE6",  # 淡黃背景區塊
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "color": "#8C8C8C",  # 次要文字色
                        "action": {
                            "type": "postback",
                            "label": "返回",
                            "displayText": "返回類別選擇",
                            "data": f"action=back_to_category&type={transaction_type}"
                        },
                        "height": "sm"
                    }
                ]
            }
        }
        
        return FlexSendMessage(alt_text=f"輸入{type_text}金額", contents=bubble)

    @staticmethod
    def create_account_selection(user_id, transaction_type, category, amount, note=None):
        """創建帳戶選擇選單"""
        # 獲取用戶的帳戶
        accounts = Account.query.filter_by(user_id=user_id).all()
        
        # 如果沒有帳戶，使用預設帳戶
        if not accounts:
            accounts = [Account(name="默認", account_type="cash")]
        
        # 創建帳戶按鈕
        account_buttons = []
        for account in accounts:
            # 構建 postback 數據，如果有備註則包含
            postback_data = f"action=account&type={transaction_type}&category={category}&amount={amount}&account={account.name}"
            if note:
                # 對備註進行URL編碼，避免特殊字符造成問題
                encoded_note = urllib.parse.quote(note)
                postback_data += f"&note={encoded_note}"
                logger.info(f"帳戶選擇中備註已URL編碼: '{note}' -> '{encoded_note}'")
                
            account_buttons.append(
                ButtonComponent(
                    style="primary",
                    color="#8C8C8C",  # 次要文字色
                    action=PostbackAction(
                        label=account.name,
                        display_text=f"選擇帳戶：{account.name}",
                        data=postback_data
                    ),
                    height="sm",
                    margin="md"
                )
            )
        
        is_expense = transaction_type == "expense"
        type_text = "支出" if is_expense else "收入"
        type_color = "#FAAD14" if is_expense else "#FFC940"  # 強調亮點黃/主色 Primary
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor=type_color,
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text="選擇帳戶",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    ),
                    TextComponent(
                        text=f"{type_text} {category} ${amount}",
                        color="#FFFFFF",
                        size="sm",
                        align="center",
                        margin="xs"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    TextComponent(
                        text="請選擇要使用的帳戶",
                        size="md",
                        color="#8C8C8C",  # 次要文字色
                        align="center",
                        margin="md"
                    ),
                    BoxComponent(
                        layout="vertical",
                        margin="lg",
                        contents=account_buttons
                    ),
                    ButtonComponent(
                        style="link",
                        color="#8C8C8C",  # 次要文字色
                        action=PostbackAction(
                            label="新增帳戶",
                            display_text="創建新帳戶",
                            data=f"action=new_account&type={transaction_type}&category={category}&amount={amount}"
                        ),
                        height="sm",
                        margin="lg"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#8C8C8C",  # 次要文字色
                        action=PostbackAction(
                            label="返回",
                            display_text="返回金額輸入",
                            data=f"action=back_to_amount&type={transaction_type}&category={category}"
                        ),
                        height="sm"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="選擇帳戶",
            contents=bubble
        )

    @staticmethod
    def create_note_input(transaction_type, category, amount, account):
        """創建備註輸入選單"""
        is_expense = transaction_type == "expense"
        type_text = "支出" if is_expense else "收入"
        type_color = "#FAAD14" if is_expense else "#FFC940"  # 強調亮點黃/主色 Primary
        
        quick_notes = []
        if is_expense:
            if category == "餐飲":
                quick_notes = ["早餐", "午餐", "晚餐", "外食", "飲料", "宵夜"]
            elif category == "交通":
                quick_notes = ["公車", "捷運", "計程車", "共享單車", "加油", "停車費"]
            elif category == "購物":
                quick_notes = ["日用品", "衣服鞋子", "電子產品", "禮品", "網購"]
        else:
            quick_notes = ["薪資", "額外收入", "獎金", "紅利", "投資收益", "退款"]
        
        # 創建快速備註按鈕
        quick_note_buttons = []
        for i in range(0, len(quick_notes), 3):
            group = quick_notes[i:min(i+3, len(quick_notes))]
            row = {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": []
            }
            
            for note in group:
                row["contents"].append({
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "postback",
                        "label": note,
                        "displayText": f"備註：{note}",
                        "data": f"action=finish&type={transaction_type}&category={category}&amount={amount}&account={account}&note={note}"
                    },
                    "height": "sm",
                    "flex": 1,
                    "margin": "xs"
                })
            
            quick_note_buttons.append(row)
        
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": type_color,
                "paddingAll": "10px",
                "contents": [
                    {
                        "type": "text",
                        "text": "添加備註 (選填)",
                        "color": "#FFFFFF",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"{type_text} {category} ${amount} - {account}",
                        "color": "#FFFFFF",
                        "size": "sm",
                        "align": "center",
                        "wrap": True,
                        "margin": "xs"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "您可以直接輸入備註文字，或選擇下方選項",
                        "size": "sm",
                        "color": "#8C8C8C",  # 次要文字色
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "快速備註",
                        "size": "md",
                        "weight": "bold",
                        "margin": "lg"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "style": "secondary",
                                "action": {
                                    "type": "postback",
                                    "label": "返回",
                                    "displayText": "返回帳戶選擇",
                                    "data": f"action=back_to_account&type={transaction_type}&category={category}&amount={amount}"
                                },
                                "height": "sm",
                                "flex": 1
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "color": type_color,
                                "action": {
                                    "type": "postback",
                                    "label": "跳過備註",
                                    "displayText": "完成記帳",
                                    "data": f"action=finish&type={transaction_type}&category={category}&amount={amount}&account={account}"
                                },
                                "height": "sm",
                                "flex": 2,
                                "margin": "md"
                            }
                        ]
                    }
                ]
            }
        }
        
        # 將快速備註按鈕添加到body的contents中
        bubble["body"]["contents"].extend(quick_note_buttons)
        
        return FlexSendMessage(alt_text="添加備註", contents=bubble)

    @staticmethod
    def create_confirmation(transaction_type, category, amount, account, note=None):
        """創建記帳完成確認訊息"""
        is_expense = transaction_type == "expense"
        type_text = "支出" if is_expense else "收入"
        type_color = "#FAAD14" if is_expense else "#FFC940"  # 強調亮點黃/主色 Primary
        
        contents = [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": "類型",
                        "size": "md",
                        "color": "#8C8C8C", 
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": type_text,
                        "size": "md",
                        "weight": "bold",
                        "color": "#595959",
                        "flex": 4
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
                        "text": "類別",
                        "size": "md",
                        "color": "#8C8C8C",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": category,
                        "size": "md",
                        "weight": "bold",
                        "color": "#595959",
                        "flex": 4
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
                        "text": "金額",
                        "size": "md",
                        "color": "#8C8C8C",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": f"${amount}",
                        "size": "md",
                        "weight": "bold",
                        "color": type_color,
                        "flex": 4
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
                        "text": "帳戶",
                        "size": "md",
                        "color": "#8C8C8C",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": account,
                        "size": "md",
                        "weight": "bold",
                        "color": "#595959",
                        "flex": 4
                    }
                ],
                "margin": "md"
            }
        ]
        
        if note:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": "備註",
                        "size": "md",
                        "color": "#8C8C8C",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": note,
                        "size": "md",
                        "weight": "bold",
                        "color": "#595959",
                        "flex": 4,
                        "wrap": True
                    }
                ],
                "margin": "md"
            })
        
        # 獲取當前台灣時間（UTC+8）
        utc_now = datetime.utcnow()
        taiwan_time = utc_now + timedelta(hours=8)
        time_str = taiwan_time.strftime("%Y-%m-%d %H:%M")
        
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "時間",
                    "size": "md",
                    "color": "#8C8C8C",
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": time_str,
                    "size": "md",
                    "weight": "bold",
                    "color": "#595959",
                    "flex": 4
                }
            ],
            "margin": "md"
        })
        
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#FFE58F",  # 輔助亮黃
                "paddingAll": "10px",
                "contents": [
                    {
                        "type": "text",
                        "text": "記帳成功",
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
                "backgroundColor": "#FFFBE6",  # 淡黃背景區塊
                "contents": contents
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#FFFBE6",  # 淡黃背景區塊
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "color": type_color,
                                "action": {
                                    "type": "postback",
                                    "label": "繼續記帳",
                                    "displayText": "繼續記帳",
                                    "data": "action=main_menu"
                                },
                                "height": "sm",
                                "flex": 1
                            },
                            {
                                "type": "button",
                                "style": "secondary",
                                "color": "#8C8C8C",  # 次要文字色
                                "action": {
                                    "type": "message",
                                    "label": "查看記錄",
                                    "text": "今天"
                                },
                                "height": "sm",
                                "flex": 1,
                                "margin": "md"
                            }
                        ]
                    }
                ]
            }
        }
        
        return FlexSendMessage(alt_text="記帳成功", contents=bubble)

    @staticmethod
    def create_transfer_menu(user_id):
        """創建轉帳選單"""
        # 獲取用戶的帳戶
        accounts = Account.query.filter_by(user_id=user_id).all()
        
        # 如果帳戶數量不足，提示創建更多帳戶
        if len(accounts) < 2:
            bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(
                            text="需要至少兩個帳戶",
                            weight="bold",
                            size="lg",
                            align="center"
                        ),
                        TextComponent(
                            text="要進行轉帳，您需要至少兩個不同的帳戶。請先創建更多帳戶。",
                            size="md",
                            color="#888888",
                            align="center",
                            wrap=True,
                            margin="md"
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout="vertical",
                    contents=[
                        ButtonComponent(
                            style="primary",
                            action=PostbackAction(
                                label="創建新帳戶",
                                display_text="創建新帳戶",
                                data="action=new_account&type=transfer"
                            ),
                            height="sm"
                        ),
                        ButtonComponent(
                            style="secondary",
                            action=PostbackAction(
                                label="返回主選單",
                                display_text="返回主選單",
                                data="action=main_menu"
                            ),
                            height="sm",
                            margin="md"
                        )
                    ]
                )
            )
            
            return FlexSendMessage(
                alt_text="需要更多帳戶",
                contents=bubble
            )
        
        # 創建來源帳戶選擇按鈕
        account_buttons = []
        for account in accounts:
            account_buttons.append(
                ButtonComponent(
                    style="primary",
                    color="#555555",
                    action=PostbackAction(
                        label=f"{account.name} (${account.balance})",
                        display_text=f"從 {account.name} 轉出",
                        data=f"action=transfer_from&account={account.name}"
                    ),
                    height="sm",
                    margin="md"
                )
            )
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor="#9966FF",
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text="轉帳",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text="請選擇轉出帳戶",
                        size="md",
                        color="#888888",
                        align="center",
                        margin="md"
                    ),
                    BoxComponent(
                        layout="vertical",
                        margin="lg",
                        contents=account_buttons
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        style="secondary",
                        action=PostbackAction(
                            label="返回主選單",
                            display_text="返回主選單",
                            data="action=main_menu"
                        ),
                        height="sm"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="選擇轉出帳戶",
            contents=bubble
        )

    @staticmethod
    def create_category_selection_for_quick_expense(user_id, amount, category_keyword, categories, note=None):
        """
        創建快速支出的類別選擇界面
        :param user_id: 用戶ID
        :param amount: 支出金額
        :param category_keyword: 用戶輸入的類別關鍵字
        :param categories: 可選的類別列表
        :param note: 可選備註
        """
        # 篩選與輸入關鍵字相關的類別
        filtered_categories = []
        for category in categories:
            if category_keyword.lower() in category.name.lower() or category.name.lower() in category_keyword.lower():
                filtered_categories.append(category)
        
        # 如果沒有找到匹配的類別，顯示所有類別
        if not filtered_categories:
            filtered_categories = categories
        
        # 創建類別選擇按鈕
        category_buttons = []
        for category in filtered_categories:
            # 創建Postback數據，如果有備註則包含
            postback_data = f"action=quick_expense&amount={amount}&category={category.name}"
            if note:
                # 對備註進行URL編碼，避免特殊字符造成問題
                encoded_note = urllib.parse.quote(note)
                postback_data += f"&note={encoded_note}"
                logger.info(f"備註已URL編碼: '{note}' -> '{encoded_note}'")
                
            category_buttons.append(
                ButtonComponent(
                    style="secondary",
                    color="#FAAD14",  # 強調亮點黃
                    action=PostbackAction(
                        label=f"{category.icon} {category.name}",
                        display_text=f"選擇類別：{category.name}",
                        data=postback_data
                    ),
                    height="sm",
                    margin="md"
                )
            )
        
        # 如果沒有可用類別，添加一個創建新類別的按鈕
        if not category_buttons:
            category_buttons.append(
                ButtonComponent(
                    style="primary",
                    color="#FFC940",  # 主色 Primary
                    action=PostbackAction(
                        label=f"創建新類別 '{category_keyword}'",
                        display_text=f"創建新類別：{category_keyword}",
                        data=f"action=create_category&name={category_keyword}&is_expense=true&amount={amount}"
                    ),
                    height="sm",
                    margin="md"
                )
            )
        
        # 添加創建新類別的按鈕
        category_buttons.append(
            ButtonComponent(
                style="link",
                color="#8C8C8C",  # 次要文字色
                action=PostbackAction(
                    label="創建新類別",
                    display_text="創建新類別",
                    data=f"action=custom_category&type=expense&quick_expense=true&amount={amount}"
                ),
                height="sm",
                margin="md"
            )
        )
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor="#FAAD14",  # 強調亮點黃
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text=f"支出：${amount}",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    TextComponent(
                        text="請選擇支出類別",
                        size="md",
                        color="#8C8C8C",  # 次要文字色
                        align="center",
                        margin="md"
                    ),
                    SeparatorComponent(margin="md", color="#D9D9D9"),  # 邊框用灰
                    BoxComponent(
                        layout="vertical",
                        margin="md",
                        contents=category_buttons
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#8C8C8C",  # 次要文字色
                        action=PostbackAction(
                            label="取消",
                            display_text="取消記帳",
                            data="action=cancel"
                        ),
                        height="sm"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="選擇支出類別",
            contents=bubble
        )

    @staticmethod
    def create_editable_transaction_list(transactions, summary):
        """創建可編輯的交易記錄列表界面"""
        transaction_items = []
        
        # 為每筆交易創建內容
        for idx, transaction in enumerate(transactions[:10]):  # 限制顯示最近10筆，避免訊息過長
            # 設置不同的背景顏色
            bg_color = "#FFFBE6" if idx % 2 == 0 else "#FFF3CF"
            
            # 交易項目
            item = BoxComponent(
                layout="vertical",
                backgroundColor=bg_color,
                cornerRadius="md",
                margin="sm",
                paddingAll="10px",
                action=PostbackAction(
                    label=f"查看交易 {transaction['id']}",
                    display_text=f"查看交易記錄 {transaction['id']}",
                    data=f"action=view_transaction&id={transaction['id']}"
                ),
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            TextComponent(
                                text=f"{transaction['category_icon']} {transaction['category']}",
                                size="md",
                                color="#595959",
                                weight="bold",
                                flex=4
                            ),
                            TextComponent(
                                text=f"${transaction['amount']}",
                                size="md",
                                color="#FAAD14" if transaction['type'] == "expense" else "#FFC940",
                                align="end",
                                weight="bold",
                                flex=2
                            )
                        ]
                    ),
                    BoxComponent(
                        layout="horizontal",
                        margin="xs",
                        contents=[
                            TextComponent(
                                text=transaction['date'],
                                size="xs",
                                color="#8C8C8C",
                                flex=2
                            ),
                            TextComponent(
                                text=transaction['account'],
                                size="xs",
                                color="#8C8C8C",
                                align="end",
                                flex=2
                            )
                        ]
                    )
                ]
            )
            
            # 如果有備註，添加備註
            if transaction['note']:
                item.contents.append(
                    TextComponent(
                        text=f"備註: {transaction['note']}",
                        size="xs",
                        color="#8C8C8C",
                        margin="xs",
                        wrap=True
                    )
                )
            
            transaction_items.append(item)
        
        if not transaction_items:
            transaction_items.append(
                BoxComponent(
                    layout="vertical",
                    backgroundColor="#FFFBE6",
                    cornerRadius="md",
                    margin="sm",
                    paddingAll="10px",
                    contents=[
                        TextComponent(
                            text="沒有交易記錄",
                            size="md",
                            color="#8C8C8C",
                            align="center"
                        )
                    ]
                )
            )
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor="#FFE58F",  # 輔助亮黃
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text=f"{summary['period']}的交易記錄",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                paddingAll="10px",
                contents=[
                    # 總計信息
                    BoxComponent(
                        layout="vertical",
                        backgroundColor="#FFFBE6",
                        cornerRadius="md",
                        paddingAll="10px",
                        contents=[
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="總支出", size="sm", color="#8C8C8C", flex=1),
                                    TextComponent(text=f"${summary['total_expense']}", size="sm", color="#FAAD14", align="end", flex=1)
                                ]
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="總收入", size="sm", color="#8C8C8C", flex=1),
                                    TextComponent(text=f"${summary['total_income']}", size="sm", color="#FFC940", align="end", flex=1)
                                ],
                                margin="xs"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="結餘", size="sm", color="#595959", weight="bold", flex=1),
                                    TextComponent(
                                        text=f"${summary['net']}",
                                        size="sm",
                                        color="#FFC940" if summary['net'] >= 0 else "#FAAD14",
                                        align="end",
                                        weight="bold",
                                        flex=1
                                    )
                                ],
                                margin="xs"
                            )
                        ]
                    ),
                    # 分隔線
                    SeparatorComponent(margin="md", color="#D9D9D9"),
                    # 交易記錄標題
                    TextComponent(
                        text="點擊項目可查看詳情並編輯",
                        size="xs",
                        color="#8C8C8C",
                        align="center",
                        margin="md"
                    )
                ] + transaction_items
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            ButtonComponent(
                                style="secondary",
                                color="#8C8C8C",  # 次要文字色
                                action=PostbackAction(
                                    label="返回",
                                    display_text="返回主選單",
                                    data="action=main_menu"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="primary",
                                color="#FFE58F",  # 輔助亮黃
                                action=MessageAction(
                                    label="新增記錄",
                                    text="kimi"
                                ),
                                height="sm",
                                flex=1,
                                margin="sm"
                            )
                        ]
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text=f"{summary['period']}的交易記錄",
            contents=bubble
        )

    @staticmethod
    def create_transaction_detail(transaction):
        """創建交易詳情界面"""
        # 設置顏色和標題
        is_expense = transaction['is_expense']
        header_color = "#FAAD14" if is_expense else "#FFC940"  # 強調亮點黃/主色 Primary
        header_title = "支出詳情" if is_expense else "收入詳情"
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor=header_color,
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text=header_title,
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    ),
                    TextComponent(
                        text=f"ID: {transaction['id']}",
                        color="#FFFFFF",
                        size="xs",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                paddingAll="15px",
                contents=[
                    # 類別
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            TextComponent(text="類別", size="md", color="#8C8C8C", flex=1),
                            TextComponent(
                                text=f"{transaction['category_icon']} {transaction['category']}",
                                size="md",
                                color="#595959",
                                weight="bold",
                                align="end",
                                flex=2
                            )
                        ],
                        margin="md"
                    ),
                    # 金額
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            TextComponent(text="金額", size="md", color="#8C8C8C", flex=1),
                            TextComponent(
                                text=f"${transaction['amount']}",
                                size="md",
                                color=header_color,
                                weight="bold",
                                align="end",
                                flex=2
                            )
                        ],
                        margin="md"
                    ),
                    # 帳戶
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            TextComponent(text="帳戶", size="md", color="#8C8C8C", flex=1),
                            TextComponent(
                                text=transaction['account'],
                                size="md",
                                color="#595959",
                                align="end",
                                flex=2
                            )
                        ],
                        margin="md"
                    ),
                    # 時間
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            TextComponent(text="時間", size="md", color="#8C8C8C", flex=1),
                            TextComponent(
                                text=transaction['date'],
                                size="md",
                                color="#595959",
                                align="end",
                                flex=2
                            )
                        ],
                        margin="md"
                    ),
                    # 備註
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            TextComponent(text="備註", size="md", color="#8C8C8C", flex=1),
                            TextComponent(
                                text=transaction['note'] if transaction['note'] else "無",
                                size="md",
                                color="#595959",
                                align="end",
                                flex=2,
                                wrap=True
                            )
                        ],
                        margin="md"
                    ),
                    # 分隔線
                    SeparatorComponent(margin="xl", color="#D9D9D9")
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            ButtonComponent(
                                style="primary",
                                color="#FFC940",  # 主色 Primary
                                action=PostbackAction(
                                    label="修改",
                                    display_text=f"修改交易 {transaction['id']}",
                                    data=f"action=edit_transaction&id={transaction['id']}"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="secondary",
                                color="#8C8C8C",  # 次要文字色
                                action=PostbackAction(
                                    label="確定",
                                    display_text="返回交易列表",
                                    data="action=view_transactions&period=today"
                                ),
                                height="sm",
                                flex=1,
                                margin="sm"
                            )
                        ]
                    ),
                    ButtonComponent(
                        style="secondary",
                        color="#FAAD14",  # 強調亮點黃
                        action=PostbackAction(
                            label="刪除",
                            display_text=f"刪除交易 {transaction['id']}",
                            data=f"action=confirm_delete&id={transaction['id']}"
                        ),
                        height="sm",
                        margin="md"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text=f"{transaction['type_text']}詳情",
            contents=bubble
        )

    @staticmethod
    def create_edit_transaction_form(transaction, categories, accounts):
        """創建編輯交易的表單界面"""
        # 設置顏色和標題
        is_expense = transaction['is_expense']
        header_color = "#FAAD14" if is_expense else "#FFC940"  # 強調亮點黃/主色 Primary
        header_title = "修改支出" if is_expense else "修改收入"
        
        # 創建類別選擇按鈕
        category_buttons = []
        for category in categories:
            bg_color = "#FFE58F" if category.id == transaction['category_id'] else "#FFFFFF"
            text_color = "#FFFFFF" if category.id == transaction['category_id'] else "#595959"
            
            category_buttons.append(
                BoxComponent(
                    layout="vertical",
                    action=PostbackAction(
                        label=category.name,
                        display_text=f"修改類別為：{category.name}",
                        data=f"action=update_category&id={transaction['id']}&category_id={category.id}"
                    ),
                    backgroundColor=bg_color,
                    cornerRadius="md",
                    paddingAll="8px",
                    width="30%",
                    height="60px",
                    margin="xs",
                    contents=[
                        TextComponent(
                            text=category.icon,
                            size="lg",
                            align="center",
                            color=text_color
                        ),
                        TextComponent(
                            text=category.name,
                            size="xs",
                            align="center",
                            color=text_color
                        )
                    ]
                )
            )
        
        # 分組顯示類別 (每行3個)
        grouped_categories = []
        for i in range(0, len(category_buttons), 3):
            group = category_buttons[i:i+3]
            row = BoxComponent(
                layout="horizontal",
                margin="xs",
                contents=group
            )
            grouped_categories.append(row)
        
        # 創建帳戶選擇按鈕
        account_buttons = []
        for account in accounts:
            bg_color = "#FFE58F" if account.id == transaction['account_id'] else "#FFFFFF"
            text_color = "#FFFFFF" if account.id == transaction['account_id'] else "#595959"
            
            account_buttons.append(
                ButtonComponent(
                    style="secondary",
                    color=bg_color,
                    action=PostbackAction(
                        label=account.name,
                        display_text=f"修改帳戶為：{account.name}",
                        data=f"action=update_account&id={transaction['id']}&account_id={account.id}"
                    ),
                    height="sm",
                    margin="xs"
                )
            )
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor=header_color,
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text=header_title,
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    ),
                    TextComponent(
                        text=f"ID: {transaction['id']}",
                        color="#FFFFFF",
                        size="xs",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                paddingAll="15px",
                contents=[
                    # 當前值顯示
                    BoxComponent(
                        layout="vertical",
                        backgroundColor="#FFFBE6",
                        cornerRadius="md",
                        paddingAll="10px",
                        contents=[
                            TextComponent(
                                text="當前值",
                                size="xs",
                                color="#8C8C8C",
                                weight="bold"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="類別", size="xs", color="#8C8C8C", flex=1),
                                    TextComponent(
                                        text=transaction['category'],
                                        size="xs",
                                        color="#595959",
                                        align="end",
                                        flex=2
                                    )
                                ],
                                margin="xs"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="金額", size="xs", color="#8C8C8C", flex=1),
                                    TextComponent(
                                        text=f"${transaction['amount']}",
                                        size="xs",
                                        color=header_color,
                                        align="end",
                                        flex=2
                                    )
                                ],
                                margin="xs"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="帳戶", size="xs", color="#8C8C8C", flex=1),
                                    TextComponent(
                                        text=transaction['account'],
                                        size="xs",
                                        color="#595959",
                                        align="end",
                                        flex=2
                                    )
                                ],
                                margin="xs"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="備註", size="xs", color="#8C8C8C", flex=1),
                                    TextComponent(
                                        text=transaction['note'] if transaction['note'] else "無",
                                        size="xs",
                                        color="#595959",
                                        align="end",
                                        flex=2,
                                        wrap=True
                                    )
                                ],
                                margin="xs"
                            )
                        ]
                    ),
                    # 分隔線
                    SeparatorComponent(margin="md", color="#D9D9D9"),
                    # 編輯選項
                    TextComponent(
                        text="選擇類別",
                        size="md",
                        color="#595959",
                        weight="bold",
                        margin="md"
                    )
                ] + grouped_categories + [
                    # 分隔線
                    SeparatorComponent(margin="md", color="#D9D9D9"),
                    # 帳戶選擇
                    TextComponent(
                        text="選擇帳戶",
                        size="md",
                        color="#595959",
                        weight="bold",
                        margin="md"
                    ),
                    BoxComponent(
                        layout="vertical",
                        margin="sm",
                        contents=account_buttons
                    ),
                    # 分隔線
                    SeparatorComponent(margin="md", color="#D9D9D9"),
                    # 修改金額和備註的按鈕
                    BoxComponent(
                        layout="horizontal",
                        margin="md",
                        contents=[
                            ButtonComponent(
                                style="primary",
                                color="#FFE58F",  # 輔助亮黃
                                action=PostbackAction(
                                    label="修改金額",
                                    display_text=f"修改交易 {transaction['id']} 金額",
                                    data=f"action=edit_amount&id={transaction['id']}"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="primary",
                                color="#FFE58F",  # 輔助亮黃
                                action=PostbackAction(
                                    label="修改備註",
                                    display_text=f"修改交易 {transaction['id']} 備註",
                                    data=f"action=edit_note&id={transaction['id']}"
                                ),
                                height="sm",
                                flex=1,
                                margin="sm"
                            )
                        ]
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#8C8C8C",  # 次要文字色
                        action=PostbackAction(
                            label="返回詳情",
                            display_text=f"查看交易 {transaction['id']}",
                            data=f"action=view_transaction&id={transaction['id']}"
                        ),
                        height="sm"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text=f"修改{transaction['type_text']}",
            contents=bubble
        )

    @staticmethod
    def create_confirm_delete(transaction_id, category, amount, date):
        """創建刪除確認界面"""
        bubble = BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFE0E0",  # 淡紅色背景
                paddingAll="15px",
                contents=[
                    TextComponent(
                        text="確認刪除交易記錄",
                        size="lg",
                        color="#D32F2F",  # 紅色
                        weight="bold",
                        align="center"
                    ),
                    BoxComponent(
                        layout="vertical",
                        margin="md",
                        contents=[
                            TextComponent(
                                text="您確定要刪除以下交易記錄嗎？",
                                size="md",
                                color="#595959",
                                wrap=True
                            ),
                            TextComponent(
                                text="此操作無法撤銷。",
                                size="sm",
                                color="#D32F2F",  # 紅色
                                margin="sm"
                            ),
                            BoxComponent(
                                layout="vertical",
                                backgroundColor="#FFFFFF",
                                cornerRadius="md",
                                margin="md",
                                paddingAll="10px",
                                contents=[
                                    TextComponent(
                                        text=f"ID: {transaction_id}",
                                        size="xs",
                                        color="#8C8C8C"
                                    ),
                                    TextComponent(
                                        text=f"類別: {category}",
                                        size="md",
                                        color="#595959",
                                        margin="xs"
                                    ),
                                    TextComponent(
                                        text=f"金額: ${amount}",
                                        size="md",
                                        color="#595959",
                                        margin="xs"
                                    ),
                                    TextComponent(
                                        text=f"日期: {date}",
                                        size="xs",
                                        color="#8C8C8C",
                                        margin="xs"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFE0E0",  # 淡紅色背景
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            ButtonComponent(
                                style="secondary",
                                color="#8C8C8C",  # 次要文字色
                                action=PostbackAction(
                                    label="取消",
                                    display_text=f"取消刪除交易 {transaction_id}",
                                    data=f"action=view_transaction&id={transaction_id}"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="primary",
                                color="#D32F2F",  # 紅色
                                action=PostbackAction(
                                    label="確認刪除",
                                    display_text=f"確認刪除交易 {transaction_id}",
                                    data=f"action=delete_transaction&id={transaction_id}"
                                ),
                                height="sm",
                                flex=1,
                                margin="sm"
                            )
                        ]
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="確認刪除交易記錄",
            contents=bubble
        )

    @staticmethod
    def create_transaction_period_selection():
        """創建交易記錄時間範圍選擇界面"""
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor="#FFE58F",  # 輔助亮黃
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text="選擇查詢時間範圍",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                paddingAll="15px",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#FFE58F",  # 輔助亮黃
                        action=PostbackAction(
                            label="今天",
                            display_text="查詢今天的交易記錄",
                            data="action=view_transactions&period=today"
                        ),
                        height="sm",
                        margin="md"
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#FFE58F",  # 輔助亮黃
                        action=PostbackAction(
                            label="昨天",
                            display_text="查詢昨天的交易記錄",
                            data="action=view_transactions&period=yesterday"
                        ),
                        height="sm",
                        margin="md"
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#FFE58F",  # 輔助亮黃
                        action=PostbackAction(
                            label="本週",
                            display_text="查詢本週的交易記錄",
                            data="action=view_transactions&period=week"
                        ),
                        height="sm",
                        margin="md"
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#FFE58F",  # 輔助亮黃
                        action=PostbackAction(
                            label="本月",
                            display_text="查詢本月的交易記錄",
                            data="action=view_transactions&period=month"
                        ),
                        height="sm",
                        margin="md"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFBE6",  # 淡黃背景區塊
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#8C8C8C",  # 次要文字色
                        action=PostbackAction(
                            label="返回",
                            display_text="返回主選單",
                            data="action=main_menu"
                        ),
                        height="sm"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="選擇查詢時間範圍",
            contents=bubble
        )

    def create_task_list(self, tasks):
        """創建任務列表"""
        if not tasks:
            bubble = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "目前沒有任務",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#888888",
                            "align": "center"
                        }
                    ]
                }
            }
            return FlexSendMessage(alt_text="任務列表", contents=bubble)
        
        task_contents = []
        for task in tasks:
            status_emoji = "✅" if task.status == "completed" else "⭕"
            task_content = {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"{status_emoji} {task.title}",
                                "size": "md",
                                "weight": "bold",
                                "flex": 5
                            }
                        ]
                    }
                ]
            }
            
            if task.description:
                task_content["contents"].append({
                    "type": "text",
                    "text": task.description,
                    "size": "sm",
                    "color": "#888888",
                    "wrap": True,
                    "margin": "sm"
                })
            
            if task.due_date:
                task_content["contents"].append({
                    "type": "text",
                    "text": f"截止時間：{task.due_date.strftime('%Y-%m-%d %H:%M')}",
                    "size": "xs",
                    "color": "#AAAAAA",
                    "margin": "sm"
                })
            
            task_content["contents"].append({
                "type": "box",
                "layout": "horizontal",
                "margin": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary" if task.status != "completed" else "secondary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "完成" if task.status != "completed" else "取消完成",
                            "data": f"action=toggle_task&task_id={task.id}"
                        },
                        "color": "#FAAD14"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "margin": "sm",
                        "action": {
                            "type": "postback",
                            "label": "刪除",
                            "data": f"action=delete_task&task_id={task.id}"
                        }
                    }
                ]
            })
            
            task_contents.append(task_content)
            
            # 添加分隔線
            if tasks.index(task) < len(tasks) - 1:
                task_contents.append({
                    "type": "separator",
                    "margin": "lg"
                })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "任務列表",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#555555"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": task_contents
                    }
                ]
            }
        }
        
        return FlexSendMessage(alt_text="任務列表", contents=bubble) 