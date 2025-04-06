"""
Flex Message服務模組
創建互動式記帳流程的Flex Message
"""
import logging
from datetime import datetime, timedelta
from linebot.models import (
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, IconComponent,
    PostbackAction, MessageAction, SeparatorComponent,
    CarouselContainer, QuickReply, QuickReplyButton
)
from models import Category, Account
import urllib.parse

logger = logging.getLogger(__name__)

class FlexMessageService:
    @staticmethod
    def create_main_menu():
        """創建主選單 (功能選擇)"""
        bubble = BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    TextComponent(
                        text="Kimi 助手",
                        weight="bold",
                        size="xl",
                        align="center",
                        color="#5D4037"  # 深褐色文字
                    ),
                    TextComponent(
                        text="請選擇功能",
                        size="md",
                        color="#8D6E63",  # 褐色文字
                        align="center",
                        margin="md"
                    ),
                    SeparatorComponent(margin="xl", color="#D7CCC8"),  # 淺褐色分隔線
                    BoxComponent(
                        layout="horizontal",
                        margin="md",
                        contents=[
                            ButtonComponent(
                                style="primary",
                                color="#FFB74D",  # 橙黃色按鈕
                                action=PostbackAction(
                                    label="記帳",
                                    display_text="記帳",
                                    data="action=record&type=expense"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="primary",
                                color="#EF6C00",  # 深橙色按鈕
                                action=PostbackAction(
                                    label="任務",
                                    display_text="任務管理",
                                    data="action=task_menu"
                                ),
                                height="sm",
                                margin="md",
                                flex=1
                            )
                        ]
                    ),
                    BoxComponent(
                        layout="horizontal",
                        margin="md",
                        contents=[
                            ButtonComponent(
                                style="secondary",
                                color="#F9A825",  # 金黃色按鈕
                                action=PostbackAction(
                                    label="記錄查詢",
                                    display_text="查詢記錄",
                                    data="action=view_transactions&period=today"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="secondary",
                                color="#4CAF50",  # 綠色按鈕
                                action=MessageAction(
                                    label="月度報表",
                                    text="月報"
                                ),
                                height="sm",
                                margin="md",
                                flex=1
                            )
                        ]
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="Kimi 助手選單",
            contents=bubble,
            quick_reply=QuickReply(items=[
                QuickReplyButton(
                    action=MessageAction(label="最近記錄", text="今天")
                ),
                QuickReplyButton(
                    action=MessageAction(label="月度報表", text="月報")
                ),
                QuickReplyButton(
                    action=MessageAction(label="編輯記錄", text="記錄")
                )
            ])
        )

    @staticmethod
    def create_category_selection(user_id, transaction_type):
        """創建類別選擇選單"""
        is_expense = transaction_type == "expense"
        
        # 獲取用戶可用的類別
        categories = Category.query.filter_by(
            user_id=user_id,
            is_expense=is_expense
        ).all()
        
        # 如果沒有類別，使用預設類別
        if not categories:
            if is_expense:
                categories = [
                    Category(name="餐飲", icon="🍔", is_expense=True),
                    Category(name="交通", icon="🚗", is_expense=True),
                    Category(name="購物", icon="🛒", is_expense=True),
                    Category(name="娛樂", icon="🎮", is_expense=True),
                    Category(name="住房", icon="🏠", is_expense=True),
                    Category(name="醫療", icon="💊", is_expense=True),
                    Category(name="教育", icon="📚", is_expense=True),
                    Category(name="其他", icon="📝", is_expense=True)
                ]
            else:
                categories = [
                    Category(name="薪資", icon="💰", is_expense=False),
                    Category(name="獎金", icon="🎁", is_expense=False),
                    Category(name="投資", icon="📈", is_expense=False),
                    Category(name="其他收入", icon="💴", is_expense=False)
                ]
        
        # 分組顯示類別 (每行3個)
        grouped_categories = []
        for i in range(0, len(categories), 3):
            group = categories[i:i+3]
            row = BoxComponent(
                layout="horizontal",
                margin="md",
                contents=[]
            )
            
            for category in group:
                row.contents.append(
                    BoxComponent(
                        layout="vertical",
                        action=PostbackAction(
                            label=category.name,
                            display_text=f"選擇類別：{category.name}",
                            data=f"action=category&type={transaction_type}&category={category.name}"
                        ),
                        contents=[
                            TextComponent(
                                text=category.icon,
                                size="xxl",
                                align="center"
                            ),
                            TextComponent(
                                text=category.name,
                                size="sm",
                                align="center",
                                wrap=True
                            )
                        ],
                        width="33%",
                        cornerRadius="md",
                        paddingAll="8px",
                        backgroundColor="#FFF8DC"  # 淡黃色背景
                    )
                )
            
            grouped_categories.append(row)
        
        # 創建Flex Message
        type_text = "支出" if is_expense else "收入"
        type_color = "#EF6C00" if is_expense else "#FFB74D"  # 深橙色/橙黃色
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor=type_color,
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text=f"選擇{type_text}類別",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=grouped_categories + [
                    ButtonComponent(
                        style="link",
                        color="#A1887F",  # 褐色
                        action=PostbackAction(
                            label="自定義類別",
                            display_text="創建自定義類別",
                            data=f"action=custom_category&type={transaction_type}"
                        ),
                        height="sm",
                        margin="lg"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#A1887F",  # 褐色
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
            alt_text=f"選擇{type_text}類別",
            contents=bubble
        )

    @staticmethod
    def create_amount_input(transaction_type, category):
        """創建金額輸入選單"""
        is_expense = transaction_type == "expense"
        type_text = "支出" if is_expense else "收入"
        type_color = "#EF6C00" if is_expense else "#FFB74D"  # 深橙色/橙黃色
        
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    TextComponent(
                        text="請直接輸入金額數字",
                        size="md",
                        color="#8D6E63",  # 褐色文字
                        align="center",
                        margin="md"
                    ),
                    TextComponent(
                        text="例如：150、1000、33000",
                        size="sm",
                        color="#8D6E63",  # 褐色文字
                        align="center",
                        margin="sm"
                    ),
                    TextComponent(
                        text="或使用快速格式：早餐-50、薪資+5000",
                        size="sm",
                        color="#8D6E63",  # 褐色文字
                        align="center",
                        margin="sm"
                    ),
                    BoxComponent(
                        layout="vertical",
                        margin="xxl",
                        contents=[
                            TextComponent(
                                text="請在下方輸入框中直接輸入金額",
                                size="md", 
                                weight="bold",
                                align="center",
                                color="#5D4037"  # 深褐色文字
                            )
                        ]
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#A1887F",  # 褐色
                        action=PostbackAction(
                            label="返回",
                            display_text="返回類別選擇",
                            data=f"action=back_to_category&type={transaction_type}"
                        ),
                        height="sm"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text=f"輸入{type_text}金額",
            contents=bubble
        )

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
                    color="#A1887F",  # 褐色
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
        type_color = "#EF6C00" if is_expense else "#FFB74D"  # 深橙色/橙黃色
        
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    TextComponent(
                        text="請選擇要使用的帳戶",
                        size="md",
                        color="#8D6E63",  # 褐色文字
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
                        color="#A1887F",  # 褐色
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#A1887F",  # 褐色
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
        type_color = "#EF6C00" if is_expense else "#FFB74D"  # 深橙色/橙黃色
        
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
        quick_note_rows = []
        for i in range(0, len(quick_notes), 3):
            group = quick_notes[i:min(i+3, len(quick_notes))]
            row = BoxComponent(
                layout="horizontal",
                margin="md",
                contents=[]
            )
            
            for note in group:
                row.contents.append(
                    ButtonComponent(
                        style="secondary",
                        action=PostbackAction(
                            label=note,
                            display_text=f"備註：{note}",
                            data=f"action=finish&type={transaction_type}&category={category}&amount={amount}&account={account}&note={note}"
                        ),
                        height="sm",
                        flex=1,
                        margin="xs"
                    )
                )
            
            quick_note_rows.append(row)
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor=type_color,
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text="添加備註 (選填)",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    ),
                    TextComponent(
                        text=f"{type_text} {category} ${amount} - {account}",
                        color="#FFFFFF",
                        size="sm",
                        align="center",
                        wrap=True,
                        margin="xs"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text="您可以直接輸入備註文字，或選擇下方選項",
                        size="sm",
                        color="#8D6E63",  # 褐色文字
                        align="center",
                        margin="md"
                    ),
                    TextComponent(
                        text="快速備註",
                        size="md",
                        weight="bold",
                        margin="lg"
                    )
                ] + quick_note_rows
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            ButtonComponent(
                                style="secondary",
                                action=PostbackAction(
                                    label="返回",
                                    display_text="返回帳戶選擇",
                                    data=f"action=back_to_account&type={transaction_type}&category={category}&amount={amount}"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="primary",
                                color=type_color,
                                action=PostbackAction(
                                    label="跳過備註",
                                    display_text="完成記帳",
                                    data=f"action=finish&type={transaction_type}&category={category}&amount={amount}&account={account}"
                                ),
                                height="sm",
                                flex=2,
                                margin="md"
                            )
                        ]
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="添加備註",
            contents=bubble
        )

    @staticmethod
    def create_confirmation(transaction_type, category, amount, account, note=None):
        """創建記帳完成確認訊息"""
        is_expense = transaction_type == "expense"
        type_text = "支出" if is_expense else "收入"
        type_color = "#EF6C00" if is_expense else "#FFB74D"  # 深橙色/橙黃色
        
        contents = [
            BoxComponent(
                layout="horizontal",
                contents=[
                    TextComponent(text="類型", size="md", color="#8D6E63", flex=2),
                    TextComponent(text=type_text, size="md", weight="bold", color="#5D4037", flex=4)
                ],
                margin="md"
            ),
            BoxComponent(
                layout="horizontal",
                contents=[
                    TextComponent(text="類別", size="md", color="#8D6E63", flex=2),
                    TextComponent(text=category, size="md", weight="bold", color="#5D4037", flex=4)
                ],
                margin="md"
            ),
            BoxComponent(
                layout="horizontal",
                contents=[
                    TextComponent(text="金額", size="md", color="#8D6E63", flex=2),
                    TextComponent(
                        text=f"${amount}",
                        size="md",
                        weight="bold",
                        color=type_color,
                        flex=4
                    )
                ],
                margin="md"
            ),
            BoxComponent(
                layout="horizontal",
                contents=[
                    TextComponent(text="帳戶", size="md", color="#8D6E63", flex=2),
                    TextComponent(text=account, size="md", weight="bold", color="#5D4037", flex=4)
                ],
                margin="md"
            )
        ]
        
        if note:
            contents.append(
                BoxComponent(
                    layout="horizontal",
                    contents=[
                        TextComponent(text="備註", size="md", color="#8D6E63", flex=2),
                        TextComponent(text=note, size="md", weight="bold", color="#5D4037", flex=4, wrap=True)
                    ],
                    margin="md"
                )
            )
        
        # 獲取當前台灣時間（UTC+8）
        utc_now = datetime.utcnow()
        taiwan_time = utc_now + timedelta(hours=8)
        time_str = taiwan_time.strftime("%Y-%m-%d %H:%M")
        
        contents.append(
            BoxComponent(
                layout="horizontal",
                contents=[
                    TextComponent(text="時間", size="md", color="#8D6E63", flex=2),
                    TextComponent(text=time_str, size="md", weight="bold", color="#5D4037", flex=4)
                ],
                margin="md"
            )
        )
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor="#F9A825",  # 金黃色
                paddingAll="10px",
                contents=[
                    TextComponent(
                        text="記帳成功",
                        color="#FFFFFF",
                        weight="bold",
                        size="lg",
                        align="center"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=contents
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            ButtonComponent(
                                style="primary",
                                color=type_color,
                                action=PostbackAction(
                                    label="繼續記帳",
                                    display_text="繼續記帳",
                                    data=f"action=main_menu"
                                ),
                                height="sm",
                                flex=1
                            ),
                            ButtonComponent(
                                style="secondary",
                                color="#A1887F",  # 褐色
                                action=MessageAction(
                                    label="查看記錄",
                                    text="今天"
                                ),
                                height="sm",
                                flex=1,
                                margin="md"
                            )
                        ]
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="記帳成功",
            contents=bubble
        )

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
                    color="#EF6C00",  # 深橙色
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
                    color="#FFB74D",  # 橙黃色
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
                color="#A1887F",  # 褐色
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
                backgroundColor="#EF6C00",  # 深橙色
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    TextComponent(
                        text="請選擇支出類別",
                        size="md",
                        color="#8D6E63",  # 褐色文字
                        align="center",
                        margin="md"
                    ),
                    SeparatorComponent(margin="md", color="#D7CCC8"),  # 淺褐色分隔線
                    BoxComponent(
                        layout="vertical",
                        margin="md",
                        contents=category_buttons
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#A1887F",  # 褐色
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
            bg_color = "#FFF8E1" if idx % 2 == 0 else "#FFF3CF"
            
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
                                color="#5D4037",
                                weight="bold",
                                flex=4
                            ),
                            TextComponent(
                                text=f"${transaction['amount']}",
                                size="md",
                                color="#EF6C00" if transaction['type'] == "expense" else "#4CAF50",
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
                                color="#8D6E63",
                                flex=2
                            ),
                            TextComponent(
                                text=transaction['account'],
                                size="xs",
                                color="#8D6E63",
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
                        color="#8D6E63",
                        margin="xs",
                        wrap=True
                    )
                )
            
            transaction_items.append(item)
        
        if not transaction_items:
            transaction_items.append(
                BoxComponent(
                    layout="vertical",
                    backgroundColor="#FFF8E1",
                    cornerRadius="md",
                    margin="sm",
                    paddingAll="10px",
                    contents=[
                        TextComponent(
                            text="沒有交易記錄",
                            size="md",
                            color="#8D6E63",
                            align="center"
                        )
                    ]
                )
            )
        
        bubble = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                backgroundColor="#F9A825",  # 金黃色
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
                backgroundColor="#FFFDE7",  # 更淡的黃色
                paddingAll="10px",
                contents=[
                    # 總計信息
                    BoxComponent(
                        layout="vertical",
                        backgroundColor="#FFF8E1",
                        cornerRadius="md",
                        paddingAll="10px",
                        contents=[
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="總支出", size="sm", color="#8D6E63", flex=1),
                                    TextComponent(text=f"${summary['total_expense']}", size="sm", color="#EF6C00", align="end", flex=1)
                                ]
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="總收入", size="sm", color="#8D6E63", flex=1),
                                    TextComponent(text=f"${summary['total_income']}", size="sm", color="#4CAF50", align="end", flex=1)
                                ],
                                margin="xs"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="結餘", size="sm", color="#5D4037", weight="bold", flex=1),
                                    TextComponent(
                                        text=f"${summary['net']}",
                                        size="sm",
                                        color="#4CAF50" if summary['net'] >= 0 else "#EF6C00",
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
                    SeparatorComponent(margin="md", color="#D7CCC8"),
                    # 交易記錄標題
                    TextComponent(
                        text="點擊項目可查看詳情並編輯",
                        size="xs",
                        color="#8D6E63",
                        align="center",
                        margin="md"
                    )
                ] + transaction_items
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFFDE7",  # 更淡的黃色
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            ButtonComponent(
                                style="secondary",
                                color="#A1887F",  # 褐色
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
                                color="#F9A825",  # 金黃色
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
        header_color = "#EF6C00" if is_expense else "#4CAF50"  # 深橙色/綠色
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                paddingAll="15px",
                contents=[
                    # 類別
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            TextComponent(text="類別", size="md", color="#8D6E63", flex=1),
                            TextComponent(
                                text=f"{transaction['category_icon']} {transaction['category']}",
                                size="md",
                                color="#5D4037",
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
                            TextComponent(text="金額", size="md", color="#8D6E63", flex=1),
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
                            TextComponent(text="帳戶", size="md", color="#8D6E63", flex=1),
                            TextComponent(
                                text=transaction['account'],
                                size="md",
                                color="#5D4037",
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
                            TextComponent(text="時間", size="md", color="#8D6E63", flex=1),
                            TextComponent(
                                text=transaction['date'],
                                size="md",
                                color="#5D4037",
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
                            TextComponent(text="備註", size="md", color="#8D6E63", flex=1),
                            TextComponent(
                                text=transaction['note'] if transaction['note'] else "無",
                                size="md",
                                color="#5D4037",
                                align="end",
                                flex=2,
                                wrap=True
                            )
                        ],
                        margin="md"
                    ),
                    # 分隔線
                    SeparatorComponent(margin="xl", color="#D7CCC8")
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    BoxComponent(
                        layout="horizontal",
                        contents=[
                            ButtonComponent(
                                style="primary",
                                color="#F9A825",  # 金黃色
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
                                color="#A1887F",  # 褐色
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
                        color="#D32F2F",  # 紅色
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
        header_color = "#EF6C00" if is_expense else "#4CAF50"  # 深橙色/綠色
        header_title = "修改支出" if is_expense else "修改收入"
        
        # 創建類別選擇按鈕
        category_buttons = []
        for category in categories:
            bg_color = "#F9A825" if category.id == transaction['category_id'] else "#FFFFFF"
            text_color = "#FFFFFF" if category.id == transaction['category_id'] else "#5D4037"
            
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
            bg_color = "#F9A825" if account.id == transaction['account_id'] else "#FFFFFF"
            text_color = "#FFFFFF" if account.id == transaction['account_id'] else "#5D4037"
            
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                paddingAll="15px",
                contents=[
                    # 當前值顯示
                    BoxComponent(
                        layout="vertical",
                        backgroundColor="#FFFDE7",
                        cornerRadius="md",
                        paddingAll="10px",
                        contents=[
                            TextComponent(
                                text="當前值",
                                size="xs",
                                color="#8D6E63",
                                weight="bold"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="類別", size="xs", color="#8D6E63", flex=1),
                                    TextComponent(
                                        text=transaction['category'],
                                        size="xs",
                                        color="#5D4037",
                                        align="end",
                                        flex=2
                                    )
                                ],
                                margin="xs"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="金額", size="xs", color="#8D6E63", flex=1),
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
                                    TextComponent(text="帳戶", size="xs", color="#8D6E63", flex=1),
                                    TextComponent(
                                        text=transaction['account'],
                                        size="xs",
                                        color="#5D4037",
                                        align="end",
                                        flex=2
                                    )
                                ],
                                margin="xs"
                            ),
                            BoxComponent(
                                layout="horizontal",
                                contents=[
                                    TextComponent(text="備註", size="xs", color="#8D6E63", flex=1),
                                    TextComponent(
                                        text=transaction['note'] if transaction['note'] else "無",
                                        size="xs",
                                        color="#5D4037",
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
                    SeparatorComponent(margin="md", color="#D7CCC8"),
                    # 編輯選項
                    TextComponent(
                        text="選擇類別",
                        size="md",
                        color="#5D4037",
                        weight="bold",
                        margin="md"
                    )
                ] + grouped_categories + [
                    # 分隔線
                    SeparatorComponent(margin="md", color="#D7CCC8"),
                    # 帳戶選擇
                    TextComponent(
                        text="選擇帳戶",
                        size="md",
                        color="#5D4037",
                        weight="bold",
                        margin="md"
                    ),
                    BoxComponent(
                        layout="vertical",
                        margin="sm",
                        contents=account_buttons
                    ),
                    # 分隔線
                    SeparatorComponent(margin="md", color="#D7CCC8"),
                    # 修改金額和備註的按鈕
                    BoxComponent(
                        layout="horizontal",
                        margin="md",
                        contents=[
                            ButtonComponent(
                                style="primary",
                                color="#F9A825",  # 金黃色
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
                                color="#F9A825",  # 金黃色
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#A1887F",  # 褐色
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
                                color="#5D4037",
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
                                        color="#8D6E63"
                                    ),
                                    TextComponent(
                                        text=f"類別: {category}",
                                        size="md",
                                        color="#5D4037",
                                        margin="xs"
                                    ),
                                    TextComponent(
                                        text=f"金額: ${amount}",
                                        size="md",
                                        color="#5D4037",
                                        margin="xs"
                                    ),
                                    TextComponent(
                                        text=f"日期: {date}",
                                        size="xs",
                                        color="#8D6E63",
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
                                color="#A1887F",  # 褐色
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
                backgroundColor="#F9A825",  # 金黃色
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                paddingAll="15px",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#F9A825",  # 金黃色
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
                        color="#F9A825",  # 金黃色
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
                        color="#F9A825",  # 金黃色
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
                        color="#F9A825",  # 金黃色
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
                backgroundColor="#FFF8E1",  # 淡黃色背景
                contents=[
                    ButtonComponent(
                        style="secondary",
                        color="#A1887F",  # 褐色
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