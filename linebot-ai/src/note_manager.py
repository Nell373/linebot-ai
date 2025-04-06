"""
記事管理模組
管理使用者的記事，支援新增、查詢、刪除等操作
"""
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union

# 獲取日誌記錄器
logger = logging.getLogger(__name__)

# 資料儲存路徑
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

# 確保資料目錄存在
os.makedirs(DATA_DIR, exist_ok=True)

class NoteManager:
    """記事管理類，負責處理記事的儲存和檢索"""
    
    def __init__(self):
        """初始化記事管理器，確保儲存檔案存在"""
        self.notes: Dict[str, List[Dict]] = {}
        self._load_notes()
    
    def _load_notes(self) -> None:
        """從檔案載入記事"""
        try:
            if os.path.exists(NOTES_FILE):
                with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            else:
                # 如果檔案不存在，建立空檔案
                with open(NOTES_FILE, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"載入記事檔案時出錯: {str(e)}")
            self.notes = {}
    
    def _save_notes(self) -> None:
        """儲存記事到檔案"""
        try:
            with open(NOTES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"儲存記事檔案時出錯: {str(e)}")
    
    def add_note(self, user_id: str, content: str) -> Dict:
        """
        新增記事
        
        Args:
            user_id: 使用者 ID
            content: 記事內容
            
        Returns:
            新增的記事
        """
        # 初始化使用者的記事列表（如果不存在）
        if user_id not in self.notes:
            self.notes[user_id] = []
        
        # 建立新記事
        note = {
            "id": self._generate_note_id(user_id),
            "content": content,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 添加記事
        self.notes[user_id].append(note)
        self._save_notes()
        
        return note
    
    def get_all_notes(self, user_id: str) -> List[Dict]:
        """
        獲取使用者的所有記事
        
        Args:
            user_id: 使用者 ID
            
        Returns:
            記事列表
        """
        return self.notes.get(user_id, [])
    
    def get_note(self, user_id: str, note_id: str) -> Optional[Dict]:
        """
        獲取特定記事
        
        Args:
            user_id: 使用者 ID
            note_id: 記事 ID
            
        Returns:
            記事資訊或 None（若未找到）
        """
        for note in self.notes.get(user_id, []):
            if note["id"] == note_id:
                return note
        return None
    
    def update_note(self, user_id: str, note_id: str, content: str) -> Optional[Dict]:
        """
        更新記事
        
        Args:
            user_id: 使用者 ID
            note_id: 記事 ID
            content: 新記事內容
            
        Returns:
            更新後的記事或 None（若未找到）
        """
        for note in self.notes.get(user_id, []):
            if note["id"] == note_id:
                note["content"] = content
                note["updated_at"] = datetime.now().isoformat()
                self._save_notes()
                return note
        return None
    
    def delete_note(self, user_id: str, note_id: str) -> bool:
        """
        刪除記事
        
        Args:
            user_id: 使用者 ID
            note_id: 記事 ID
            
        Returns:
            是否刪除成功
        """
        user_notes = self.notes.get(user_id, [])
        for i, note in enumerate(user_notes):
            if note["id"] == note_id:
                user_notes.pop(i)
                self._save_notes()
                return True
        return False
    
    def _generate_note_id(self, user_id: str) -> str:
        """生成唯一記事 ID"""
        user_notes = self.notes.get(user_id, [])
        if not user_notes:
            return "1"
        
        # 找出最大 ID 並加 1
        max_id = max(int(note["id"]) for note in user_notes)
        return str(max_id + 1)

# 初始化記事管理器實例
note_manager = NoteManager() 