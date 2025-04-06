"""
財務服務模組
處理記帳相關功能
"""
from datetime import datetime, timedelta
import re
import logging
from models import db, Transaction, Category, Account

logger = logging.getLogger(__name__)

# 默認支出分類
DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "餐飲", "icon": "🍔"},
    {"name": "交通", "icon": "🚗"},
    {"name": "購物", "icon": "🛒"},
    {"name": "娛樂", "icon": "🎮"},
    {"name": "住房", "icon": "🏠"},
    {"name": "醫療", "icon": "💊"},
    {"name": "教育", "icon": "📚"},
    {"name": "其他", "icon": "📝"}
]

# 默認收入分類
DEFAULT_INCOME_CATEGORIES = [
    {"name": "薪資", "icon": "💰"},
    {"name": "獎金", "icon": "🎁"},
    {"name": "投資", "icon": "📈"},
    {"name": "其他收入", "icon": "💴"}
]

class FinanceService:
    @staticmethod
    def initialize_user(user_id):
        """初始化用戶的記帳數據"""
        try:
            # 檢查默認賬戶是否存在
            default_account = Account.query.filter_by(user_id=user_id, name="默認").first()
            if not default_account:
                default_account = Account(
                    user_id=user_id,
                    name="默認",
                    balance=0,
                    currency="TWD",
                    account_type="cash"
                )
                db.session.add(default_account)
                logger.info(f"為用戶 {user_id} 創建默認賬戶")
            
            # 添加默認支出分類
            for category_data in DEFAULT_EXPENSE_CATEGORIES:
                category = Category.query.filter_by(
                    user_id=user_id, 
                    name=category_data["name"],
                    is_expense=True
                ).first()
                
                if not category:
                    category = Category(
                        user_id=user_id,
                        name=category_data["name"],
                        icon=category_data["icon"],
                        is_expense=True
                    )
                    db.session.add(category)
                    logger.info(f"為用戶 {user_id} 添加支出分類：{category_data['name']}")
            
            # 添加默認收入分類
            for category_data in DEFAULT_INCOME_CATEGORIES:
                category = Category.query.filter_by(
                    user_id=user_id, 
                    name=category_data["name"],
                    is_expense=False
                ).first()
                
                if not category:
                    category = Category(
                        user_id=user_id,
                        name=category_data["name"],
                        icon=category_data["icon"],
                        is_expense=False
                    )
                    db.session.add(category)
                    logger.info(f"為用戶 {user_id} 添加收入分類：{category_data['name']}")
            
            db.session.commit()
            return "初始化成功！已創建默認賬戶和分類。"
        
        except Exception as e:
            logger.error(f"初始化用戶 {user_id} 失敗: {str(e)}")
            db.session.rollback()
            return f"初始化失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def add_transaction(user_id, amount, category_name, note=None, account_name="默認", is_expense=True):
        """添加交易記錄"""
        try:
            # 確保用戶已初始化
            default_account = Account.query.filter_by(user_id=user_id, name="默認").first()
            if not default_account:
                FinanceService.initialize_user(user_id)
            
            # 查找分類
            category = Category.query.filter_by(user_id=user_id, name=category_name, is_expense=is_expense).first()
            
            # 如果找不到指定分類，使用默認分類
            if not category:
                default_category_name = "其他" if is_expense else "其他收入"
                category = Category.query.filter_by(user_id=user_id, name=default_category_name, is_expense=is_expense).first()
                
                if not category:
                    # 如果連默認分類都沒有，創建一個
                    icon = "📝" if is_expense else "💴"
                    category = Category(
                        user_id=user_id,
                        name=default_category_name,
                        icon=icon,
                        is_expense=is_expense
                    )
                    db.session.add(category)
            
            # 查找賬戶
            account = Account.query.filter_by(user_id=user_id, name=account_name).first()
            if not account:
                account = Account.query.filter_by(user_id=user_id, name="默認").first()
            
            # 使用 UTC 時間直接存儲，不轉換為台灣時間
            # Fly.io 服務可能已經在日本或台灣區域，會有時區影響
            utc_now = datetime.utcnow()
            
            # 創建交易記錄
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                category_id=category.id,
                account_id=account.id,
                transaction_date=utc_now,  # 使用 UTC 時間
                note=note,
                is_expense=is_expense
            )
            
            db.session.add(transaction)
            
            # 更新賬戶餘額
            if is_expense:
                account.balance -= amount
            else:
                account.balance += amount
            
            db.session.commit()
            
            transaction_type = "支出" if is_expense else "收入"
            response = f"已記錄{transaction_type}：{category.icon} {category.name} ${amount}"
            if note:
                response += f"，備註：{note}"
            
            return response
        
        except Exception as e:
            logger.error(f"添加交易記錄失敗: {str(e)}")
            db.session.rollback()
            return f"記錄失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def get_transactions(user_id, period="today"):
        """獲取用戶的交易記錄"""
        try:
            # 設置時間範圍，使用 UTC 時間
            utc_now = datetime.utcnow()
            # 轉換為台灣時間進行顯示，但查詢條件仍使用 UTC
            taiwan_now = utc_now + timedelta(hours=8)
            
            if period == "today":
                # 創建台灣時間當天的0點，然後轉換回 UTC 時間
                start_date = datetime(taiwan_now.year, taiwan_now.month, taiwan_now.day) - timedelta(hours=8)
                period_text = "今天"
            elif period == "yesterday":
                yesterday = taiwan_now - timedelta(days=1)
                start_date = datetime(yesterday.year, yesterday.month, yesterday.day) - timedelta(hours=8)
                period_text = "昨天"
            elif period == "week":
                # 獲取本週一的日期 (台灣時間)
                monday = taiwan_now - timedelta(days=taiwan_now.weekday())
                start_date = datetime(monday.year, monday.month, monday.day) - timedelta(hours=8)
                period_text = "本週"
            elif period == "month":
                start_date = datetime(taiwan_now.year, taiwan_now.month, 1) - timedelta(hours=8)
                period_text = "本月"
            else:
                return "無效的時間範圍，請使用：今天、昨天、本週、本月"
            
            # 查詢交易記錄
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date
            ).order_by(Transaction.transaction_date.desc()).all()
            
            if not transactions:
                return f"{period_text}沒有交易記錄。"
            
            # 計算總支出和總收入
            total_expense = sum(t.amount for t in transactions if t.is_expense)
            total_income = sum(t.amount for t in transactions if not t.is_expense)
            
            # 構建回應訊息
            message_parts = [f"{period_text}的交易記錄："]
            message_parts.append(f"總支出：${total_expense}")
            message_parts.append(f"總收入：${total_income}")
            message_parts.append(f"淨額：${total_income - total_expense}")
            message_parts.append("----------")
            
            # 添加每筆交易的詳情
            for transaction in transactions:
                category = Category.query.filter_by(id=transaction.category_id).first()
                category_name = category.name if category else "未分類"
                category_icon = category.icon if category else "📝"
                
                transaction_type = "支出" if transaction.is_expense else "收入"
                
                # 轉換交易時間為台灣時間顯示
                taiwan_date = transaction.transaction_date + timedelta(hours=8)
                date_str = taiwan_date.strftime("%m-%d %H:%M")
                
                transaction_text = f"{date_str} {category_icon} {category_name} ${transaction.amount} ({transaction_type})"
                if transaction.note:
                    transaction_text += f"，備註：{transaction.note}"
                
                message_parts.append(transaction_text)
            
            return "\n".join(message_parts)
        
        except Exception as e:
            logger.error(f"獲取交易記錄失敗: {str(e)}")
            return f"獲取記錄失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def get_monthly_summary(user_id, year=None, month=None):
        """獲取月度匯總報告"""
        try:
            # 如果未指定年月，使用當前月份（台灣時間）
            utc_now = datetime.utcnow()
            taiwan_now = utc_now + timedelta(hours=8)
            year = year or taiwan_now.year
            month = month or taiwan_now.month
            
            # 設置時間範圍（轉換回UTC時間以匹配數據庫）
            # 創建台灣時間當月的1號，然後轉換回 UTC 時間
            start_date = datetime(year, month, 1) - timedelta(hours=8)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(hours=8)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(hours=8)
            
            # 查詢該月的交易記錄
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date
            ).all()
            
            if not transactions:
                return f"{year}年{month}月沒有交易記錄。"
            
            # 計算總支出和總收入
            total_expense = sum(t.amount for t in transactions if t.is_expense)
            total_income = sum(t.amount for t in transactions if not t.is_expense)
            
            # 按分類匯總支出
            expense_by_category = {}
            for transaction in transactions:
                if transaction.is_expense:
                    category = Category.query.filter_by(id=transaction.category_id).first()
                    category_name = category.name if category else "未分類"
                    
                    if category_name not in expense_by_category:
                        expense_by_category[category_name] = {
                            "amount": 0,
                            "icon": category.icon if category else "📝"
                        }
                    
                    expense_by_category[category_name]["amount"] += transaction.amount
            
            # 按分類匯總收入
            income_by_category = {}
            for transaction in transactions:
                if not transaction.is_expense:
                    category = Category.query.filter_by(id=transaction.category_id).first()
                    category_name = category.name if category else "未分類"
                    
                    if category_name not in income_by_category:
                        income_by_category[category_name] = {
                            "amount": 0,
                            "icon": category.icon if category else "💴"
                        }
                    
                    income_by_category[category_name]["amount"] += transaction.amount
            
            # 構建回應數據
            report_data = {
                "total_expense": total_expense,
                "total_income": total_income,
                "expense_by_category": [
                    {"name": f"{data['icon']} {name}", "amount": data["amount"]}
                    for name, data in expense_by_category.items()
                ],
                "income_by_category": [
                    {"name": f"{data['icon']} {name}", "amount": data["amount"]}
                    for name, data in income_by_category.items()
                ]
            }
            
            return report_data
        
        except Exception as e:
            logger.error(f"獲取月度匯總失敗: {str(e)}")
            return f"獲取月度匯總失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def parse_transaction_command(text):
        """解析用戶輸入的命令"""
        # 支出格式：類別-金額+備註(可選) 或 類別+金額+備註(可選)
        # 例如：早餐-50 或 午餐120 麥當勞
        expense_pattern1 = r'^([\u4e00-\u9fa5a-zA-Z]+)-(\d+)(?:\s+(.+))?$'
        expense_pattern2 = r'^([\u4e00-\u9fa5a-zA-Z]+)(\d+)(?:\s+(.+))?$'
        
        expense_match1 = re.match(expense_pattern1, text)
        expense_match2 = re.match(expense_pattern2, text)
        
        # 收入格式：類別+金額 或 收入+金額+備註(可選)
        # 例如：薪資+33000 或 收入5000 薪資
        income_pattern1 = r'^([\u4e00-\u9fa5a-zA-Z]+)\+(\d+)(?:\s+(.+))?$'
        income_pattern2 = r'^收入(\d+)(?:\s+(.+))?$'
        
        income_match1 = re.match(income_pattern1, text)
        income_match2 = re.match(income_pattern2, text)
        
        # 查詢格式：今天 或 昨天 或 本週 或 本月
        query_pattern = r'^(今天|昨天|本週|本月)$'
        query_match = re.match(query_pattern, text)
        
        # 月報格式：月報 或 月報+年份-月份
        # 例如：月報 或 月報2023-5
        monthly_pattern = r'^月報(?:(\d{4})-(\d{1,2}))?$'
        monthly_match = re.match(monthly_pattern, text)
        
        if expense_match1:
            category = expense_match1.group(1)
            amount = int(expense_match1.group(2))
            note = expense_match1.group(3)
            
            return {
                'type': 'expense',
                'category': category,
                'amount': amount,
                'note': note
            }
        
        elif expense_match2:
            category = expense_match2.group(1)
            amount = int(expense_match2.group(2))
            note = expense_match2.group(3)
            
            return {
                'type': 'expense',
                'category': category,
                'amount': amount,
                'note': note
            }
        
        elif income_match1:
            category = income_match1.group(1)
            amount = int(income_match1.group(2))
            note = income_match1.group(3)
            
            return {
                'type': 'income',
                'category': category,
                'amount': amount,
                'note': note
            }
        
        elif income_match2:
            amount = int(income_match2.group(1))
            note = income_match2.group(2)
            
            return {
                'type': 'income',
                'amount': amount,
                'note': note
            }
        
        elif query_match:
            period_mapping = {
                '今天': 'today',
                '昨天': 'yesterday',
                '本週': 'week',
                '本月': 'month'
            }
            
            return {
                'type': 'query',
                'period': period_mapping[query_match.group(1)]
            }
        
        elif monthly_match:
            year = int(monthly_match.group(1)) if monthly_match.group(1) else None
            month = int(monthly_match.group(2)) if monthly_match.group(2) else None
            
            return {
                'type': 'monthly',
                'year': year,
                'month': month
            }
        
        return None

    @staticmethod
    def process_finance_command(text, user_id):
        """處理財務相關命令"""
        command = FinanceService.parse_transaction_command(text)
        
        if not command:
            return None
        
        if command['type'] == 'expense':
            return FinanceService.add_transaction(
                user_id=user_id,
                amount=command['amount'],
                category_name=command['category'],
                note=command['note'],
                is_expense=True
            )
        
        elif command['type'] == 'income':
            category_name = command.get('category', '其他收入')  # 如果沒有指定類別，使用"其他收入"
            return FinanceService.add_transaction(
                user_id=user_id,
                amount=command['amount'],
                category_name=category_name,
                note=command['note'],
                is_expense=False
            )
        
        elif command['type'] == 'query':
            return FinanceService.get_transactions(user_id, command['period'])
        
        elif command['type'] == 'monthly':
            from message_handler import create_monthly_report_flex
            report_data = FinanceService.get_monthly_summary(user_id, command['year'], command['month'])
            
            if isinstance(report_data, str):  # 處理錯誤訊息
                return report_data
            
            # 獲取年月
            now = datetime.utcnow()
            year = command['year'] or now.year
            month = command['month'] or now.month
            
            # 創建 Flex 訊息
            return create_monthly_report_flex(report_data, year, month)
        
        return None 