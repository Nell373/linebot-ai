"""
任務服務模組
用於處理任務和提醒相關功能
"""
import logging
from linebot.models import FlexSendMessage

logger = logging.getLogger(__name__)

class TaskService:
    @staticmethod
    def show_task_menu(user_id):
        """顯示任務管理選單"""
        logger.info(f"為用戶 {user_id} 顯示任務管理選單")
        
        # 簡單文字回應，實際實現時可替換為 Flex 消息
        return "任務管理功能正在開發中，敬請期待！" 