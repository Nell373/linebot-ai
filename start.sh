#!/bin/bash
set -e

# 設置環境變數 - 硬編碼憑證（在生產環境中應該使用環境變數或秘密管理）
export DATABASE_URL=${DATABASE_URL:-sqlite:///data/finances.db}
export PORT=${PORT:-8080}
export PYTHONUNBUFFERED=1
export LINE_CHANNEL_SECRET="1d260f0f95e6bc35878578a46ab05558"
export LINE_CHANNEL_ACCESS_TOKEN="dcHUu60hxSgZGL1cEM/FxzuoSkwrO6lbUVR/yjiysMm8CMahMjWMl7vRsEjvcabnl53oPoAqy/meJTyjwQ2Ie7MXv6sqlbwewb9k9154UF7g89S+4sbqkwjaKLV9RNQ6L6MBcmdACE/WlPCLG+LkhwdB04t89/1O/w1cDnyilFU="
export LIFF_ID="2007212914-e3vNnYno"

# 顯示環境變數檢查
echo "=== 環境變數檢查 ==="
echo "LINE_CHANNEL_SECRET: [已設定，長度: ${#LINE_CHANNEL_SECRET}]"
echo "LINE_CHANNEL_ACCESS_TOKEN: [已設定，長度: ${#LINE_CHANNEL_ACCESS_TOKEN}]"
echo "LIFF_ID: ${LIFF_ID}"
echo "PORT: ${PORT}"
echo "DATABASE_URL: ${DATABASE_URL}"

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