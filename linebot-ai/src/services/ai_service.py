"""
AI Service module.
Handles interactions with AI models and prompts.
"""
import json
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def analyze_message(text: str) -> str:
    """
    Analyze user message using simplified mock analysis.
    
    Args:
        text: The message text to analyze
        
    Returns:
        The AI analysis result as a JSON string
    """
    try:
        # 簡單的關鍵詞分析代替AI分析
        result = {}
        result["content"] = text
        
        # 記帳類型判斷
        if any(word in text for word in ["元", "塊", "錢", "$"]) or text.replace(".", "").isdigit():
            result["type"] = "accounting"
            # 提取金額
            import re
            amount_match = re.search(r'(\d+)(?:元|塊|$)', text)
            amount = int(amount_match.group(1)) if amount_match else 0
            
            # 簡單分類
            category = "其他"
            if any(word in text for word in ["餐", "飯", "吃"]):
                category = "食物"
            elif any(word in text for word in ["車", "捷運", "公車"]):
                category = "交通"
                
            # 獲取項目名稱（去除金額）
            item = text.replace(str(amount), "").replace("元", "").strip()
            if not item:
                item = "消費"
                
            result["details"] = {
                "item": item,
                "amount": amount,
                "category": category
            }
            
        # 提醒類型判斷
        elif any(word in text for word in ["提醒", "記得", "通知"]):
            result["type"] = "reminder"
            result["details"] = {
                "event": text.replace("提醒我", "").strip(),
                "time": "",
                "date": "今天" if "今天" in text else "明天" if "明天" in text else ""
            }
            
        # 默認為任務類型
        else:
            result["type"] = "task"
            result["details"] = {
                "description": text,
                "priority": "中"
            }
            
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}", exc_info=True)
        
        # Return a fallback result
        fallback = {
            "type": "unknown",
            "content": text,
            "details": {}
        }
        return json.dumps(fallback)