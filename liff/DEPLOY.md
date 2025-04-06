# Kimi 任務 PWA 部署指南

本文檔提供將 Kimi 任務 PWA 應用程序部署到生產環境的詳細步驟。

## 前置準備

1. **安裝依賴項**

   ```bash
   cd liff
   npm install
   ```

2. **配置環境變數**

   複製 `.env.example` 文件為 `.env`，並填入相關配置：

   ```bash
   cp .env.example .env
   ```

   主要配置項：
   - `REACT_APP_API_URL`: 後端 API 的 URL
   - `REACT_APP_LINE_CLIENT_ID`: LINE Login 的 client ID
   - `REACT_APP_LINE_CALLBACK_URL`: LINE Login 的回調 URL

## 構建 PWA

1. **生成生產環境構建**

   ```bash
   npm run build
   ```

   這將在 `build` 目錄中創建優化的生產版本。

2. **測試生產構建**

   您可以使用如下命令在本地測試構建：

   ```bash
   npx serve -s build
   ```

## 部署選項

### 1. 使用 Vercel 部署

[Vercel](https://vercel.com/) 提供簡單的一鍵式部署：

1. 安裝 Vercel CLI：

   ```bash
   npm install -g vercel
   ```

2. 登錄並部署：

   ```bash
   vercel login
   vercel
   ```

### 2. 使用 Netlify 部署

[Netlify](https://www.netlify.com/) 也是一個很好的選擇：

1. 安裝 Netlify CLI：

   ```bash
   npm install -g netlify-cli
   ```

2. 登錄並部署：

   ```bash
   netlify login
   netlify deploy --prod
   ```

### 3. 使用 Firebase Hosting 部署

Firebase 提供可靠的靜態網站託管：

1. 安裝 Firebase CLI：

   ```bash
   npm install -g firebase-tools
   ```

2. 登錄並初始化：

   ```bash
   firebase login
   firebase init hosting
   ```

3. 部署：

   ```bash
   firebase deploy --only hosting
   ```

## 配置後端 API

1. **部署 Flask 後端**

   確保 Flask 應用已經部署並可訪問。您可以使用 Heroku, Fly.io, 或其他服務。

2. **安裝後端所需的包**

   ```bash
   pip install flask flask-cors pyjwt
   ```

3. **設置環境變數**

   在後端服務器上設置必要的環境變數：

   ```bash
   # LINE Bot 設置
   export LINE_CHANNEL_SECRET=your_line_channel_secret
   export LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
   
   # JWT 設置
   export JWT_SECRET=your_jwt_secret_key
   
   # CORS 設置
   export CORS_ALLOWED_ORIGINS=https://your-pwa-domain.com
   ```

## 配置 LINE Login

1. **在 LINE Developer Console 中設置**

   - 訪問 [LINE Developers Console](https://developers.line.biz/console/)
   - 在您的 Provider 中創建或選擇一個 Channel（類型：LINE Login）
   - 設置 Callback URL: `https://your-pwa-domain.com`
   - 啟用相關權限：profile, openid
   - 確保 LINE Login Channel 已經公開發布

2. **獲取並設置 Channel ID**

   將 LINE Login Channel ID 添加到您的 `.env` 文件：

   ```
   REACT_APP_LINE_CLIENT_ID=your_line_login_channel_id
   ```

## 驗證部署

部署完成後，請測試以下功能以確保一切正常：

1. PWA 安裝按鈕是否顯示並且能夠正常工作
2. 離線功能是否正常
3. LINE 登錄是否工作正常
4. 創建任務並通過 LINE 接收通知是否成功

## 故障排除

如果遇到問題，請檢查：

1. 控制台錯誤日誌
2. 網絡請求是否成功（檢查 Network 選項卡）
3. 環境變數是否正確設置
4. CORS 設置是否正確
5. Service Worker 是否正確註冊

## 進一步優化

1. **配置 SSL**
   
   確保您的 PWA 和 API 都通過 HTTPS 提供服務。

2. **設置自定義域名**

   為您的 PWA 配置自定義域名以提升品牌形象。

3. **實現分析**

   添加 Google Analytics 或其他分析工具來跟踪使用情況。 