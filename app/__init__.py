"""
應用程式初始化
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import config

# 初始化擴展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    """創建應用程式實例"""
    
    # 創建應用程式
    app = Flask(__name__)
    
    # 載入配置
    app.config.from_object(config[config_name])
    
    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)
    
    # 註冊藍圖 - 修正URL前綴
    from app.routes.line_webhook import webhook_bp
    app.register_blueprint(webhook_bp)  # 移除URL前綴，直接註冊到根路徑
    
    # 註冊錯誤處理器
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # 設置日誌系統
    from app.utils.logger import setup_logger
    setup_logger(app)
    
    # 設置安全性
    from app.security import setup_security
    setup_security(app)
    
    # 創建必要的目錄
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    
    return app 