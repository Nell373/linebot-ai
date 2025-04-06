"""
訊息處理模組
處理從 LINE Bot 收到的訊息，並生成響應。
"""
import logging
import re

# 獲取日誌記錄器
logger = logging.getLogger(__name__)

def process_message(message_text: str) -> str:
    """
    處理收到的訊息，並返回適當的回應。
    
    Args:
        message_text: 使用者發送的訊息文本
        
    Returns:
        回覆給使用者的訊息
    """
    logger.info(f"Processing message: {message_text}")
    
    # 檢查是否是午餐預算格式（例如：午餐120）
    lunch_budget_match = re.match(r'午餐(\d+)', message_text)
    if lunch_budget_match:
        budget = int(lunch_budget_match.group(1))
        return process_lunch_budget(budget)
    
    # 如果不匹配任何已知模式，返回默認回覆
    return "您好！我是 LINE Bot。請輸入「午餐+金額」來計算午餐預算，例如：午餐120"

def process_lunch_budget(budget: int) -> str:
    """
    處理午餐預算請求。
    
    Args:
        budget: 午餐預算金額
        
    Returns:
        關於午餐預算的回覆
    """
    logger.info(f"Processing lunch budget: {budget}")
    
    if budget <= 0:
        return "預算必須大於 0 元"
    elif budget < 50:
        return f"您的午餐預算為 {budget} 元，這可能只夠買飲料或小點心。"
    elif budget < 100:
        return f"您的午餐預算為 {budget} 元，可以考慮便當、麵食或簡單的餐點。"
    elif budget < 200:
        return f"您的午餐預算為 {budget} 元，可以選擇較好的餐廳或較豐盛的套餐。"
    elif budget < 500:
        return f"您的午餐預算為 {budget} 元，可以享用相當不錯的餐廳或特色料理。"
    else:
        return f"您的午餐預算為 {budget} 元，可以選擇高級餐廳或奢華的用餐體驗。"