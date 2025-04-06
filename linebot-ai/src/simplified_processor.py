"""
簡化版訊息處理模組
用於測試 LINE Bot 的基本功能
"""
import logging

# 獲取日誌記錄器
logger = logging.getLogger(__name__)

def process_message(message_text: str, user_id: str = "default_user") -> str:
    """
    簡化版訊息處理器
    
    Args:
        message_text: 使用者發送的訊息文本
        user_id: 使用者ID
        
    Returns:
        回覆給使用者的訊息
    """
    logger.info(f"[簡化版] 處理來自 {user_id} 的訊息: {message_text}")
    
    # 簡單的回應邏輯
    if "你好" in message_text or "哈囉" in message_text:
        return "你好！我是您的 LINE Bot 助手。"
    
    elif "記事" in message_text:
        return f"記事功能測試成功！您輸入的是：{message_text}"
    
    elif "午餐" in message_text:
        return "午餐預算功能測試成功！"
    
    else:
        return f"我收到了您的訊息：{message_text}\n這是一個簡化版的回應，用於測試 LINE Bot 的連接狀態。" 