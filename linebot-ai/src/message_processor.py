"""
訊息處理模組
處理從 LINE Bot 收到的訊息，並生成響應。
"""
import logging
import re
from typing import Dict, Any, Tuple
from .note_manager import note_manager

# 獲取日誌記錄器
logger = logging.getLogger(__name__)

def process_message(message_text: str, user_id: str = "default_user") -> str:
    """
    處理收到的訊息，並返回適當的回應。
    
    Args:
        message_text: 使用者發送的訊息文本
        user_id: 使用者ID，用於識別不同使用者的資料
        
    Returns:
        回覆給使用者的訊息
    """
    logger.info(f"Processing message from {user_id}: {message_text}")
    
    # 檢查是否是午餐預算格式（例如：午餐120）
    lunch_budget_match = re.match(r'午餐(\d+)', message_text)
    if lunch_budget_match:
        budget = int(lunch_budget_match.group(1))
        return process_lunch_budget(budget)
    
    # 檢查是否是記事相關命令
    note_command, args = parse_note_command(message_text)
    if note_command:
        return process_note_command(note_command, args, user_id)
    
    # 如果不匹配任何已知模式，返回預設回覆
    return ("您好！我是 LINE Bot。\n\n"
            "可用指令：\n"
            "• 午餐+金額：計算午餐預算，例如「午餐120」\n"
            "• 記事+內容：新增一條記事，例如「記事 買牛奶」\n"
            "• 記事列表：顯示所有記事\n"
            "• 記事查看+編號：查看特定記事，例如「記事查看 2」\n"
            "• 記事更新+編號+內容：更新記事，例如「記事更新 2 買巧克力」\n"
            "• 記事刪除+編號：刪除記事，例如「記事刪除 2」")

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

def parse_note_command(message_text: str) -> Tuple[str, Dict[str, Any]]:
    """
    解析記事相關命令
    
    Args:
        message_text: 使用者輸入的訊息
    
    Returns:
        命令類型和參數字典的元組
    """
    # 新增記事：記事 [內容]
    add_match = re.match(r'^記事\s+(.+)$', message_text)
    if add_match:
        return "add", {"content": add_match.group(1)}
    
    # 查看記事列表：記事列表
    if message_text == "記事列表":
        return "list", {}
    
    # 查看特定記事：記事查看 [id]
    view_match = re.match(r'^記事查看\s+(\d+)$', message_text)
    if view_match:
        return "view", {"note_id": view_match.group(1)}
    
    # 更新記事：記事更新 [id] [新內容]
    update_match = re.match(r'^記事更新\s+(\d+)\s+(.+)$', message_text)
    if update_match:
        return "update", {"note_id": update_match.group(1), "content": update_match.group(2)}
    
    # 刪除記事：記事刪除 [id]
    delete_match = re.match(r'^記事刪除\s+(\d+)$', message_text)
    if delete_match:
        return "delete", {"note_id": delete_match.group(1)}
    
    # 非記事命令
    return "", {}

def process_note_command(command: str, args: Dict[str, Any], user_id: str) -> str:
    """
    處理記事相關命令
    
    Args:
        command: 命令類型
        args: 命令參數
        user_id: 使用者ID
    
    Returns:
        處理結果訊息
    """
    try:
        if command == "add":
            note = note_manager.add_note(user_id, args["content"])
            return f"已新增記事 (ID: {note['id']})：{note['content']}"
        
        elif command == "list":
            notes = note_manager.get_all_notes(user_id)
            if not notes:
                return "您尚未新增任何記事。"
            
            notes_text = ["您的記事列表："]
            for note in notes:
                notes_text.append(f"{note['id']}. {note['content']}")
            
            return "\n".join(notes_text)
        
        elif command == "view":
            note = note_manager.get_note(user_id, args["note_id"])
            if not note:
                return f"找不到 ID 為 {args['note_id']} 的記事。"
            
            created_at = note["created_at"].split("T")[0]  # 只顯示日期部分
            return f"記事 {note['id']}：{note['content']}\n創建日期：{created_at}"
        
        elif command == "update":
            note = note_manager.update_note(user_id, args["note_id"], args["content"])
            if not note:
                return f"找不到 ID 為 {args['note_id']} 的記事。"
            
            return f"已更新記事 {note['id']}：{note['content']}"
        
        elif command == "delete":
            success = note_manager.delete_note(user_id, args["note_id"])
            if not success:
                return f"找不到 ID 為 {args['note_id']} 的記事。"
            
            return f"已刪除 ID 為 {args['note_id']} 的記事。"
        
        else:
            return "無效的記事命令。"
    
    except Exception as e:
        logger.error(f"處理記事命令時出錯: {str(e)}")
        return f"處理記事命令時發生錯誤：{str(e)}"