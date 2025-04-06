"""
Configuration management module.
"""
import os
import logging
from typing import Dict, Any

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# LINE Bot 設定
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')

# 提示詞路徑設定
PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')

def get_prompt_path(prompt_name: str) -> str:
    """獲取提示詞檔案的完整路徑"""
    return os.path.join(PROMPT_PATH, prompt_name)

# 預設回覆訊息
DEFAULT_RESPONSES: Dict[str, str] = {
    'accounting': '已記錄支出：{item} {amount}元 (分類：{category})',
    'reminder': '已設定提醒：{time_info} - {event}',
    'task': '已新增任務：{description} (優先級：{priority})',
    'error': '處理您的訊息時發生錯誤，請稍後再試。',
    'unknown': '無法辨識您的訊息類型，請重新輸入。'
}

# 類別對應關鍵字
CATEGORIES = {
    'food': ['餐', '食', '飯', '麵', '咖啡', '飲料', '水', '茶'],
    'transportation': ['車', '交通', '捷運', '公車', '計程車', '高鐵', '火車', 'uber'],
    'entertainment': ['電影', '遊戲', '娛樂', '玩', '唱歌', 'ktv', '旅遊'],
    'shopping': ['買', '購', '衣', '鞋', '包', '3c', '電子', '家電'],
    'other': []
}