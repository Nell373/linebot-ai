#!/bin/bash
set -e

# 設置環境變數
export DATABASE_URL=${DATABASE_URL:-sqlite:///data/finances.db}
export PORT=${PORT:-8080}
export PYTHONUNBUFFERED=1
export LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
export LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
export LIFF_ID=2007212914-e3vNnYno

# 確保數據目錄存在
mkdir -p /app/data

# 設置正確的權限
chmod -R 777 /app/data

# 顯示數據庫文件狀態
echo "=== 數據庫文件狀態 ==="
if [ -f /app/data/finances.db ]; then
  echo "資料庫文件存在，大小: $(ls -lh /app/data/finances.db | awk '{print $5}')"
else
  echo "資料庫文件不存在，將在首次運行時創建"
fi

# 啟動應用
echo "=== 啟動應用 ==="
exec gunicorn --bind 0.0.0.0:$PORT app:app 