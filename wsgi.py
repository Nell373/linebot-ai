"""
WSGI入口點
用於在部署環境中啟動應用程式
"""
from app import create_app

# 創建應用程式實例
app = create_app()

if __name__ == "__main__":
    app.run() 