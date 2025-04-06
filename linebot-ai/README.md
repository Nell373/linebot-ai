# LINE Bot AI

這是一個使用 Python 和 Flask 開發的 LINE Bot 應用程式。

## 功能

- 處理 LINE 的 webhook 請求
- 回覆使用者的訊息
- 計算午餐預算

## 本地運行

1. 安裝依賴：
   ```
   pip install -r requirements.txt
   ```

2. 設置環境變數：
   ```
   export LINE_CHANNEL_SECRET=你的頻道密鑰
   export LINE_CHANNEL_ACCESS_TOKEN=你的頻道存取令牌
   export LOG_LEVEL=INFO
   ```

3. 運行應用程式：
   ```
   python app.py
   ```

## 部署到 Render

1. 在 Render 上創建一個新的 Web Service
2. 連接到 GitHub 倉庫
3. 設置以下配置：
   - **Name**: linebot-ai（或你喜歡的名稱）
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -c gunicorn.conf.py app:app`

4. 添加環境變數：
   - `LINE_CHANNEL_SECRET`: 你的頻道密鑰
   - `LINE_CHANNEL_ACCESS_TOKEN`: 你的頻道存取令牌
   - `LOG_LEVEL`: INFO

5. 點擊 "Create Web Service" 按鈕

部署完成後，將生成的 URL + `/api/webhook` 設置為 LINE Developers Console 中的 Webhook URL。 