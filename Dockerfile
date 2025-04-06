FROM python:3.9-slim

WORKDIR /app

# 複製依賴文件
COPY requirements-simplified.txt ./requirements.txt

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建資料目錄並設置權限
RUN mkdir -p data && chmod -R 777 data

# 設置啟動腳本權限
RUN chmod +x start.sh

# 設置環境變數
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# 暴露端口
EXPOSE 8080

# 啟動命令
CMD ["./start.sh"] 