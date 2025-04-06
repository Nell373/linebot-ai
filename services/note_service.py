"""
記事服務模組
處理筆記和提醒相關功能
"""
from datetime import datetime, timedelta
import re
import logging
from models import db, Note, Tag, Reminder

logger = logging.getLogger(__name__)

class NoteService:
    @staticmethod
    def add_note(user_id, title, content=None, tags=None):
        """添加筆記"""
        try:
            # 創建筆記
            note = Note(
                user_id=user_id,
                title=title,
                content=content
            )
            
            # 處理標籤
            if tags:
                for tag_name in tags:
                    # 查找或創建標籤
                    tag = Tag.query.filter_by(user_id=user_id, name=tag_name).first()
                    if not tag:
                        tag = Tag(user_id=user_id, name=tag_name)
                        db.session.add(tag)
                    
                    # 將標籤添加到筆記
                    note.tags.append(tag)
            
            db.session.add(note)
            db.session.commit()
            
            # 返回成功訊息
            return f"已添加筆記：{title}"
        
        except Exception as e:
            logger.error(f"添加筆記失敗: {str(e)}")
            db.session.rollback()
            return f"添加筆記失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def get_notes(user_id, tag=None):
        """獲取用戶的筆記列表"""
        try:
            # 構建查詢
            query = Note.query.filter_by(user_id=user_id)
            
            # 如果指定了標籤，篩選有該標籤的筆記
            if tag:
                tag_obj = Tag.query.filter_by(user_id=user_id, name=tag).first()
                if tag_obj:
                    query = query.filter(Note.tags.contains(tag_obj))
                else:
                    return f"找不到標籤：{tag}"
            
            # 獲取筆記列表
            notes = query.order_by(Note.updated_at.desc()).all()
            
            if not notes:
                return "沒有找到筆記。" if not tag else f"沒有找到標籤為「{tag}」的筆記。"
            
            # 構建回應訊息
            message_parts = ["您的筆記列表："] if not tag else [f"標籤「{tag}」的筆記："]
            
            for note in notes:
                updated_date = note.updated_at.strftime("%Y-%m-%d")
                tags_str = ", ".join([t.name for t in note.tags]) if note.tags else ""
                tags_display = f" [{tags_str}]" if tags_str else ""
                
                message_parts.append(f"{note.id}. {note.title}{tags_display} - {updated_date}")
            
            return "\n".join(message_parts)
        
        except Exception as e:
            logger.error(f"獲取筆記列表失敗: {str(e)}")
            return f"獲取筆記列表失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def get_note_detail(user_id, note_id):
        """獲取筆記詳情"""
        try:
            # 查找筆記
            note = Note.query.filter_by(user_id=user_id, id=note_id).first()
            
            if not note:
                return f"找不到 ID 為 {note_id} 的筆記。"
            
            # 構建回應訊息
            tags_str = ", ".join([t.name for t in note.tags]) if note.tags else ""
            tags_display = f"標籤: {tags_str}\n" if tags_str else ""
            
            updated_date = note.updated_at.strftime("%Y-%m-%d %H:%M")
            
            message_parts = [
                f"筆記 #{note.id}: {note.title}",
                f"{tags_display}更新時間: {updated_date}",
                "---",
                note.content or "（無內容）"
            ]
            
            return "\n".join(message_parts)
        
        except Exception as e:
            logger.error(f"獲取筆記詳情失敗: {str(e)}")
            return f"獲取筆記詳情失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def update_note(user_id, note_id, title=None, content=None, tags=None):
        """更新筆記"""
        try:
            # 查找筆記
            note = Note.query.filter_by(user_id=user_id, id=note_id).first()
            
            if not note:
                return f"找不到 ID 為 {note_id} 的筆記。"
            
            # 更新標題
            if title:
                note.title = title
            
            # 更新內容
            if content:
                note.content = content
            
            # 更新標籤
            if tags is not None:  # 允許清空標籤
                # 清除現有標籤
                note.tags = []
                
                # 添加新標籤
                for tag_name in tags:
                    tag = Tag.query.filter_by(user_id=user_id, name=tag_name).first()
                    if not tag:
                        tag = Tag(user_id=user_id, name=tag_name)
                        db.session.add(tag)
                    
                    note.tags.append(tag)
            
            # 更新時間戳
            note.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return f"已更新筆記 #{note_id}：{note.title}"
        
        except Exception as e:
            logger.error(f"更新筆記失敗: {str(e)}")
            db.session.rollback()
            return f"更新筆記失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def delete_note(user_id, note_id):
        """刪除筆記"""
        try:
            # 查找筆記
            note = Note.query.filter_by(user_id=user_id, id=note_id).first()
            
            if not note:
                return f"找不到 ID 為 {note_id} 的筆記。"
            
            # 保存筆記標題以便回應訊息
            note_title = note.title
            
            # 刪除筆記
            db.session.delete(note)
            db.session.commit()
            
            return f"已刪除筆記 #{note_id}：{note_title}"
        
        except Exception as e:
            logger.error(f"刪除筆記失敗: {str(e)}")
            db.session.rollback()
            return f"刪除筆記失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def add_reminder(user_id, content, reminder_time, repeat_type=None):
        """添加提醒事項"""
        try:
            # 創建提醒
            reminder = Reminder(
                user_id=user_id,
                content=content,
                reminder_time=reminder_time,
                repeat_type=repeat_type
            )
            
            db.session.add(reminder)
            db.session.commit()
            
            # 格式化回應訊息
            time_str = reminder_time.strftime("%Y-%m-%d %H:%M")
            repeat_str = ""
            if repeat_type == "daily":
                repeat_str = "（每日重複）"
            elif repeat_type == "weekly":
                repeat_str = "（每週重複）"
            elif repeat_type == "monthly":
                repeat_str = "（每月重複）"
            
            return f"已設置提醒：{content}\n時間：{time_str}{repeat_str}"
        
        except Exception as e:
            logger.error(f"添加提醒失敗: {str(e)}")
            db.session.rollback()
            return f"添加提醒失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def get_reminders(user_id, include_completed=False):
        """獲取用戶的提醒事項列表"""
        try:
            # 構建查詢
            query = Reminder.query.filter_by(user_id=user_id)
            
            # 如果不包括已完成的提醒
            if not include_completed:
                query = query.filter_by(is_completed=False)
            
            # 獲取提醒列表
            reminders = query.order_by(Reminder.reminder_time).all()
            
            if not reminders:
                return "沒有待辦的提醒事項。"
            
            # 構建回應訊息
            now = datetime.utcnow()
            message_parts = ["您的提醒事項："]
            
            for reminder in reminders:
                time_str = reminder.reminder_time.strftime("%Y-%m-%d %H:%M")
                status = "（已完成）" if reminder.is_completed else ""
                
                # 確定提醒狀態
                if not reminder.is_completed:
                    if reminder.reminder_time < now:
                        status = "（已過期）"
                    elif (reminder.reminder_time - now).total_seconds() < 3600:  # 一小時內
                        status = "（即將到期）"
                
                # 重複類型
                repeat_str = ""
                if reminder.repeat_type == "daily":
                    repeat_str = "（每日）"
                elif reminder.repeat_type == "weekly":
                    repeat_str = "（每週）"
                elif reminder.repeat_type == "monthly":
                    repeat_str = "（每月）"
                
                message_parts.append(f"{reminder.id}. {time_str}{repeat_str} - {reminder.content}{status}")
            
            return "\n".join(message_parts)
        
        except Exception as e:
            logger.error(f"獲取提醒列表失敗: {str(e)}")
            return f"獲取提醒列表失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def complete_reminder(user_id, reminder_id):
        """標記提醒事項為已完成"""
        try:
            # 查找提醒
            reminder = Reminder.query.filter_by(user_id=user_id, id=reminder_id).first()
            
            if not reminder:
                return f"找不到 ID 為 {reminder_id} 的提醒事項。"
            
            # 標記為已完成
            reminder.is_completed = True
            db.session.commit()
            
            return f"已將提醒「{reminder.content}」標記為完成。"
        
        except Exception as e:
            logger.error(f"完成提醒失敗: {str(e)}")
            db.session.rollback()
            return f"操作失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def delete_reminder(user_id, reminder_id):
        """刪除提醒事項"""
        try:
            # 查找提醒
            reminder = Reminder.query.filter_by(user_id=user_id, id=reminder_id).first()
            
            if not reminder:
                return f"找不到 ID 為 {reminder_id} 的提醒事項。"
            
            # 保存提醒內容以便回應訊息
            reminder_content = reminder.content
            
            # 刪除提醒
            db.session.delete(reminder)
            db.session.commit()
            
            return f"已刪除提醒：{reminder_content}"
        
        except Exception as e:
            logger.error(f"刪除提醒失敗: {str(e)}")
            db.session.rollback()
            return f"刪除失敗，請稍後再試。錯誤: {str(e)}"

    @staticmethod
    def parse_note_command(text):
        """解析記事相關指令"""
        # 添加筆記格式：筆記+標題+內容（可選）+標籤（可選，用#標記）
        note_pattern = r'^筆記\s+([^#]+?)(?:\s+#(.+))?$'
        note_match = re.match(note_pattern, text)
        if note_match:
            title_content = note_match.group(1).strip()
            tags_str = note_match.group(2) if note_match.group(2) else ""
            
            # 分離標題和內容
            parts = title_content.split('\n', 1)
            title = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else None
            
            # 處理標籤
            tags = [tag.strip() for tag in tags_str.split('#') if tag.strip()] if tags_str else []
            
            return {
                'type': 'add_note',
                'title': title,
                'content': content,
                'tags': tags
            }
        
        # 查看筆記列表格式：筆記列表 或 筆記列表+標籤
        list_pattern = r'^筆記列表(?:\s+#(.+))?$'
        list_match = re.match(list_pattern, text)
        if list_match:
            tag = list_match.group(1).strip() if list_match.group(1) else None
            return {
                'type': 'list_notes',
                'tag': tag
            }
        
        # 查看筆記詳情格式：筆記+ID
        detail_pattern = r'^筆記\s+(\d+)$'
        detail_match = re.match(detail_pattern, text)
        if detail_match:
            note_id = int(detail_match.group(1))
            return {
                'type': 'note_detail',
                'note_id': note_id
            }
        
        # 更新筆記格式：筆記更新+ID+標題和內容+標籤（可選）
        update_pattern = r'^筆記更新\s+(\d+)\s+([^#]+?)(?:\s+#(.+))?$'
        update_match = re.match(update_pattern, text)
        if update_match:
            note_id = int(update_match.group(1))
            title_content = update_match.group(2).strip()
            tags_str = update_match.group(3) if update_match.group(3) else ""
            
            # 分離標題和內容
            parts = title_content.split('\n', 1)
            title = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else None
            
            # 處理標籤
            tags = [tag.strip() for tag in tags_str.split('#') if tag.strip()] if tags_str else []
            
            return {
                'type': 'update_note',
                'note_id': note_id,
                'title': title,
                'content': content,
                'tags': tags
            }
        
        # 刪除筆記格式：筆記刪除+ID
        delete_pattern = r'^筆記刪除\s+(\d+)$'
        delete_match = re.match(delete_pattern, text)
        if delete_match:
            note_id = int(delete_match.group(1))
            return {
                'type': 'delete_note',
                'note_id': note_id
            }
        
        # 添加提醒格式：提醒+內容+時間+重複（可選）
        # 例如：提醒 開會 2023-5-20 14:30 每週
        reminder_pattern = r'^提醒\s+(.+?)\s+(\d{4}-\d{1,2}-\d{1,2}(?:\s+\d{1,2}:\d{1,2})?)\s*(每日|每週|每月)?$'
        reminder_match = re.match(reminder_pattern, text)
        if reminder_match:
            content = reminder_match.group(1).strip()
            time_str = reminder_match.group(2).strip()
            repeat_type = reminder_match.group(3)
            
            # 解析時間
            try:
                if ' ' in time_str:  # 包含時間
                    date_part, time_part = time_str.split(' ')
                    date_parts = date_part.split('-')
                    time_parts = time_part.split(':')
                    
                    year = int(date_parts[0])
                    month = int(date_parts[1])
                    day = int(date_parts[2])
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    
                    reminder_time = datetime(year, month, day, hour, minute)
                else:  # 只有日期
                    date_parts = time_str.split('-')
                    year = int(date_parts[0])
                    month = int(date_parts[1])
                    day = int(date_parts[2])
                    
                    reminder_time = datetime(year, month, day, 9, 0)  # 默認早上9點
                
                # 轉換重複類型
                repeat_mapping = {
                    '每日': 'daily',
                    '每週': 'weekly',
                    '每月': 'monthly'
                }
                repeat = repeat_mapping.get(repeat_type) if repeat_type else None
                
                return {
                    'type': 'add_reminder',
                    'content': content,
                    'reminder_time': reminder_time,
                    'repeat_type': repeat
                }
            except ValueError:
                return {
                    'type': 'error',
                    'message': f"無法解析時間：{time_str}，請使用格式：YYYY-MM-DD HH:MM"
                }
        
        # 查看提醒列表格式：提醒列表 或 所有提醒
        reminder_list_pattern = r'^(提醒列表|所有提醒)$'
        reminder_list_match = re.match(reminder_list_pattern, text)
        if reminder_list_match:
            include_completed = reminder_list_match.group(1) == '所有提醒'
            return {
                'type': 'list_reminders',
                'include_completed': include_completed
            }
        
        # 完成提醒格式：提醒完成+ID
        complete_pattern = r'^提醒完成\s+(\d+)$'
        complete_match = re.match(complete_pattern, text)
        if complete_match:
            reminder_id = int(complete_match.group(1))
            return {
                'type': 'complete_reminder',
                'reminder_id': reminder_id
            }
        
        # 刪除提醒格式：提醒刪除+ID
        delete_reminder_pattern = r'^提醒刪除\s+(\d+)$'
        delete_reminder_match = re.match(delete_reminder_pattern, text)
        if delete_reminder_match:
            reminder_id = int(delete_reminder_match.group(1))
            return {
                'type': 'delete_reminder',
                'reminder_id': reminder_id
            }
        
        return None

    @staticmethod
    def process_note_command(text, user_id):
        """處理記事相關命令"""
        command = NoteService.parse_note_command(text)
        
        if not command:
            return None
        
        if command['type'] == 'error':
            return command['message']
        
        elif command['type'] == 'add_note':
            return NoteService.add_note(
                user_id=user_id,
                title=command['title'],
                content=command['content'],
                tags=command['tags']
            )
        
        elif command['type'] == 'list_notes':
            return NoteService.get_notes(user_id, command.get('tag'))
        
        elif command['type'] == 'note_detail':
            return NoteService.get_note_detail(user_id, command['note_id'])
        
        elif command['type'] == 'update_note':
            return NoteService.update_note(
                user_id=user_id,
                note_id=command['note_id'],
                title=command['title'],
                content=command['content'],
                tags=command['tags']
            )
        
        elif command['type'] == 'delete_note':
            return NoteService.delete_note(user_id, command['note_id'])
        
        elif command['type'] == 'add_reminder':
            return NoteService.add_reminder(
                user_id=user_id,
                content=command['content'],
                reminder_time=command['reminder_time'],
                repeat_type=command['repeat_type']
            )
        
        elif command['type'] == 'list_reminders':
            return NoteService.get_reminders(user_id, command['include_completed'])
        
        elif command['type'] == 'complete_reminder':
            return NoteService.complete_reminder(user_id, command['reminder_id'])
        
        elif command['type'] == 'delete_reminder':
            return NoteService.delete_reminder(user_id, command['reminder_id'])
        
        return None 