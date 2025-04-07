"""
應用程式安全設定
"""
import logging
from flask import Flask, request, abort
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class RateLimiter:
    """請求速率限制器"""
    
    def __init__(self, max_requests=100, time_window=60):
        """初始化
        
        Args:
            max_requests: 在時間窗口內允許的最大請求數
            time_window: 時間窗口大小（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}  # {ip: [timestamp1, timestamp2, ...]}
        
    def is_allowed(self, ip):
        """檢查IP是否被允許請求
        
        Args:
            ip: 客戶端IP地址
            
        Returns:
            bool: 是否允許
        """
        now = time.time()
        
        # 初始化
        if ip not in self.requests:
            self.requests[ip] = []
            
        # 移除過期的請求記錄
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.time_window]
        
        # 檢查請求數
        if len(self.requests[ip]) >= self.max_requests:
            return False
            
        # 添加新請求
        self.requests[ip].append(now)
        return True

def setup_security(app: Flask):
    """設置應用程式安全性
    
    Args:
        app: Flask應用程式實例
    """
    logger.info("設置應用程式安全性")
    
    # 創建速率限制器
    rate_limiter = RateLimiter(max_requests=app.config.get('RATE_LIMIT_MAX_REQUESTS', 100),
                             time_window=app.config.get('RATE_LIMIT_TIME_WINDOW', 60))
    
    # 請求前處理
    @app.before_request
    def before_request():
        # 速率限制
        if not rate_limiter.is_allowed(request.remote_addr):
            logger.warning(f"請求速率超過限制: {request.remote_addr}")
            abort(429, "Too many requests")
    
    # 添加安全響應頭
    @app.after_request
    def add_security_headers(response):
        # 內容安全策略
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; frame-ancestors 'none'"
        
        # 防止點擊劫持
        response.headers['X-Frame-Options'] = 'DENY'
        
        # 防止MIME類型嗅探
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS保護
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 引用策略
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    logger.info("應用程式安全性設置完成") 