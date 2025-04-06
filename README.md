# 財務與記事 LINE Bot

這是一個透過 LINE 平台提供財務管理和記事功能的聊天機器人。

## 功能

### 財務管理
- 記錄日常收支
- 查詢交易記錄（今天、昨天、本週、本月）
- 查看月度財務報告

### 記事功能
- 添加、查看、更新和刪除筆記
- 支持標籤分類
- 設置提醒

## 技術架構

- **後端**：Flask
- **資料庫**：SQLAlchemy ORM（支持 SQLite, MySQL, PostgreSQL）
- **LINE 介面**：LINE Messaging API
- **部署**：可部署至 Heroku, Railway, Fly.io 或其他平台

## 安裝與設置

### 前置需求
- Python 3.8 或以上
- LINE 開發者帳號和頻道
- 公開可訪問的伺服器（用於接收 LINE 的 webhook）

### 安裝步驟

1. 克隆此儲存庫：
```
git clone https://github.com/your-username/linebot-ai.git
cd linebot-ai
```

2. 安裝依賴：
```
pip install -r requirements.txt
```

3. 設置環境變數（從範例創建）：
```
cp .env.example .env
```
然後編輯 `.env` 文件，填入你的 LINE 頻道密鑰和存取令牌。

4. 初始化資料庫：
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. 運行應用：
```
flask run
```

### 部署至 Heroku

1. 創建 Heroku 應用：
```
heroku create your-app-name
```

2. 添加資料庫（例如，使用 PostgreSQL）：
```
heroku addons:create heroku-postgresql:hobby-dev
```

3. 設置環境變數：
```
heroku config:set LINE_CHANNEL_SECRET=your_line_channel_secret
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
```

4. 部署：
```
git push heroku main
```

5. 執行資料庫遷移：
```
heroku run flask db upgrade
```

## 使用指南

### 財務命令
- 記錄支出：`早餐50` 或 `午餐120 麥當勞`
- 記錄收入：`收入5000 薪資`
- 查詢記錄：`今天` 或 `昨天` 或 `本週` 或 `本月`
- 查看統計：`月報` 或 `月報2023-5`

### 筆記命令
- 添加筆記：`筆記 標題\n內容 #標籤1 #標籤2`
- 查看列表：`筆記列表` 或 `筆記列表 #標籤`
- 查看詳情：`筆記 ID`
- 更新筆記：`筆記更新 ID 新標題\n新內容 #新標籤`
- 刪除筆記：`筆記刪除 ID`

### 提醒命令
- 添加提醒：`提醒 內容 2023-5-20 14:30 每週`
- 查看提醒：`提醒列表` 或 `所有提醒`
- 完成提醒：`提醒完成 ID`
- 刪除提醒：`提醒刪除 ID`

## 貢獻

歡迎提交問題或改進建議。如果你想要貢獻代碼，請遵循以下步驟：

1. Fork 本儲存庫
2. 創建你的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟一個 Pull Request

## 授權

本項目使用 MIT 授權 - 詳情請參閱 [LICENSE](LICENSE) 文件。 