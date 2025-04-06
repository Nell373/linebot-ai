"""Gunicorn 配置文件"""
import os

# 綁定的 IP 和端口
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# 工作進程數
workers = 2

# 每個工作進程的執行緒數
threads = 2

# 超時設置
timeout = 30

# 訪問日誌格式
accesslog = "-"  # 輸出到 stdout
errorlog = "-"   # 輸出到 stderr

# 應用模塊
wsgi_app = "app:app" 