"""
API 路由模塊 - 為 PWA 提供 API 接口
"""
import os
import jwt
import json
import logging
import traceback
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from models import db, User

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 LINE API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))

# JWT 密鑰
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 7  # 天數

# 創建藍圖
api = Blueprint('api', __name__)

# 認證裝飾器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 從請求頭中獲取 token
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': '缺少認證 token'}), 401
        
        try:
            # 解碼 token
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = data['user_id']
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'message': '用戶不存在'}), 401
        except:
            return jsonify({'message': '無效或過期的 token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# LINE 登錄路由
@api.route('/auth/line', methods=['POST'])
def line_login():
    try:
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({'message': '缺少 LINE 授權碼'}), 400
        
        # TODO: 使用 code 獲取 LINE 用戶信息
        # 這裡應該調用 LINE Login API 獲取 user profile
        # 為了簡化，我們假設已獲取到 LINE 用戶 ID
        line_user_id = "mock_line_id_from_code"  # 實際應從 LINE API 獲取
        line_display_name = "LINE 用戶"
        
        # 檢查用戶是否存在，不存在則創建
        user = User.query.filter_by(line_user_id=line_user_id).first()
        if not user:
            user = User(line_user_id=line_user_id, display_name=line_display_name)
            db.session.add(user)
            db.session.commit()
        
        # 生成 JWT
        token = jwt.encode({
            'user_id': user.id,
            'line_user_id': user.line_user_id,
            'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION)
        }, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'display_name': user.display_name
            }
        })
    except Exception as e:
        logger.error(f"LINE 登錄錯誤: {str(e)}")
        return jsonify({'message': f'登錄失敗: {str(e)}'}), 500

# 創建任務
@api.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    try:
        data = request.get_json()
        
        # 檢查必要字段
        if not data or 'name' not in data:
            return jsonify({'message': '缺少必要參數: name'}), 400
        
        # 取得數據
        task_name = data.get('name')
        reminder_time = data.get('reminderTime')
        reminder_date = data.get('reminderDate')
        repeat_cycle = data.get('repeatCycle')
        end_condition = data.get('endCondition')
        repeat_times = data.get('repeatTimes')
        end_date = data.get('endDate')
        add_to_checkbox_list = data.get('addToCheckboxList', False)
        
        # 格式化任務數據，轉換為 LINE Bot 能理解的格式
        task_data = {
            "type": "task",
            "data": {
                "name": task_name,
                "reminderTime": reminder_time,
                "reminderDate": reminder_date,
                "repeatCycle": repeat_cycle,
                "endCondition": end_condition,
                "repeatTimes": repeat_times,
                "endDate": end_date,
                "addToCheckboxList": add_to_checkbox_list
            }
        }
        
        # 通過 LINE Bot 發送消息
        try:
            line_bot_api.push_message(
                current_user.line_user_id,
                TextSendMessage(text=json.dumps(task_data))
            )
            logger.info(f"已成功發送任務通知: {task_name} 給用戶 {current_user.line_user_id}")
        except LineBotApiError as line_error:
            logger.error(f"LINE API 錯誤: {str(line_error)}")
            return jsonify({'message': f'無法發送消息: {str(line_error)}'}), 500
        
        return jsonify({
            'message': '任務已創建',
            'task': {
                'name': task_name,
                'created_at': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"創建任務錯誤: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'message': f'創建任務失敗: {str(e)}'}), 500

# 獲取用戶資料
@api.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    try:
        return jsonify({
            'id': current_user.id,
            'line_user_id': current_user.line_user_id,
            'display_name': current_user.display_name
        })
    except Exception as e:
        logger.error(f"獲取用戶資料錯誤: {str(e)}")
        return jsonify({'message': f'獲取用戶資料失敗: {str(e)}'}), 500

def register_api_routes(app):
    """註冊 API 路由到 Flask 應用"""
    app.register_blueprint(api, url_prefix='/api')
    logger.info("API 路由已註冊") 