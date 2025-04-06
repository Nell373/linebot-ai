"""
應用入口點
啟動 Flask 應用和初始化數據庫
"""
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from message_handler import create_app
from api_routes import register_api_routes

# 獲取當前環境
env = os.environ.get('FLASK_ENV', 'development')
app = create_app()

# 啟用 CORS 以允許 PWA 訪問 API
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 定義資料庫檔案路徑
# 使用持久化存儲目錄來存儲數據庫文件
data_dir = os.path.join(os.getcwd(), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    
db_path = os.path.join(data_dir, 'finances.db')
database_url = f'sqlite:///{db_path}'

# 配置數據庫
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    database_url
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化數據庫
from models import db
db.init_app(app)
migrate = Migrate(app, db)

# 註冊 API 路由
register_api_routes(app)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 確保目錄結構存在
with app.app_context():
    try:
        # 檢查 services 目錄是否存在
        if not os.path.exists('services'):
            os.makedirs('services')
            logger.info("創建 services 目錄")
        
        # 創建數據庫表（如果不存在）
        db.create_all()
        logger.info(f"數據庫表創建或已存在，數據庫文件位置: {db_path}")
    except Exception as e:
        logger.error(f"初始化過程中發生錯誤: {str(e)}")

if __name__ == '__main__':
    # 開發環境使用調試模式
    debug_mode = env == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"啟動應用於 {port} 端口，調試模式：{debug_mode}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 