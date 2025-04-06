# LINE LIFF 應用配置指南

本文檔提供如何在 LINE Developers Console 中創建和配置 LIFF 應用的詳細步驟。

## 第一部分：創建 LIFF 應用

### 1. 登錄 LINE Developers Console

1. 訪問 [LINE Developers Console](https://developers.line.biz/console/)
2. 使用您的 LINE 帳戶登錄

### 2. 創建或選擇 Provider

1. 如果您還沒有 Provider，點擊「Create a new provider」
2. 輸入 Provider 名稱（例如：「Kimi TaskBot」）
3. 點擊「Create」

### 3. 創建 LIFF 應用

1. 在您的 Provider 頁面中，點擊「Create a new channel」
2. 選擇「LINE Login」類型
3. 填寫基本資訊：
   - Channel name：「Kimi 任務 PWA」
   - Channel description：簡短描述您的應用
   - App types：選擇「Web app」
   - Email address：您的聯繫郵箱
4. 閱讀並同意條款和條件，然後點擊「Create」

### 4. 配置 LIFF 設置

1. 創建完成後，點擊剛創建的 LINE Login channel
2. 在側邊欄中點擊「LIFF」
3. 點擊「Add」按鈕創建一個新的 LIFF 應用
4. 填寫 LIFF 應用信息：
   - LIFF app name：「Kimi 任務管理」
   - Size：選擇「Full」（全屏體驗）
   - Endpoint URL：輸入您的 PWA 部署 URL，例如 `https://your-pwa-domain.com`
   - Scope：勾選 `profile` 和 `openid`
   - Bot link feature：開啟並選擇您的 LINE Bot
   - Scan QR：可根據需要啟用
5. 點擊「Add」保存設置

## 第二部分：獲取 LIFF ID 並配置前端

### 1. 獲取 LIFF ID

1. 在 LIFF 頁面上，您會看到剛剛創建的 LIFF 應用
2. 複製 LIFF ID（格式如：`1234567890-AbCdEfGh`）

### 2. 配置前端環境變數

1. 在您的 PWA 項目的 `.env` 文件中添加 LIFF ID：

```
REACT_APP_LIFF_ID=您的LIFF_ID
```

2. 如果您已經部署了應用，請在您的托管平台（如 Vercel、Netlify 等）中添加相同的環境變數

## 第三部分：初始化 LIFF SDK

確保您的前端代碼正確初始化 LIFF SDK：

1. 安裝 LIFF SDK：

```bash
npm install @line/liff
```

2. 在 React 應用的入口文件中初始化 LIFF：

```javascript
import liff from '@line/liff';

// 初始化 LIFF
const initializeLiff = async () => {
  try {
    await liff.init({ liffId: process.env.REACT_APP_LIFF_ID });
    console.log("LIFF initialization succeeded");
    
    // 檢查是否在 LINE 環境中
    if (liff.isInClient()) {
      console.log("Running in LINE client");
    } else {
      console.log("Running in external browser");
    }
    
    // 如果用戶未登錄，進行登錄
    if (!liff.isLoggedIn()) {
      liff.login();
    }
  } catch (err) {
    console.error("LIFF initialization failed", err);
  }
};

initializeLiff();
```

## 第四部分：添加到 LINE 官方帳號選單

### 1. 設置 Rich Menu

1. 登錄 [LINE Official Account Manager](https://manager.line.biz/)
2. 選擇您的 LINE Bot 帳號
3. 點擊「設計」 > 「Rich Menu」
4. 創建一個新的 Rich Menu，添加一個區域用於啟動 LIFF 應用
5. 設置該區域的動作為「LIFF」並輸入您的 LIFF URL：`https://liff.line.me/您的LIFF_ID`

### 2. 設置回復訊息按鈕

在您的 LINE Bot 回復訊息中添加打開 LIFF 的按鈕：

```json
{
  "type": "template",
  "altText": "任務管理",
  "template": {
    "type": "buttons",
    "title": "Kimi 任務管理",
    "text": "請選擇操作",
    "actions": [
      {
        "type": "uri",
        "label": "打開任務 App",
        "uri": "https://liff.line.me/您的LIFF_ID"
      }
    ]
  }
}
```

## 第五部分：測試與故障排除

### 1. 測試 LIFF 應用

1. 在 LINE 應用中打開您的官方帳號
2. 點擊選單中的 LIFF 按鈕
3. 確認 LIFF 應用正確加載並運行

### 2. 常見問題排除

#### LIFF 不能正常加載：

- 檢查 Endpoint URL 是否正確
- 確認您的 PWA 使用 HTTPS 協議
- 檢查瀏覽器控制台錯誤訊息

#### 權限問題：

- 確保已勾選正確的 scope 權限
- 確認 Bot 鏈接功能已正確配置

#### 登錄問題：

- 確保 LIFF 初始化代碼正確
- 測試 `liff.login()` 功能是否正常工作

## 第六部分：安全與最佳實踐

### 1. 安全建議

- 使用 HTTPS 端點 URL
- 不要在客戶端代碼中存儲敏感信息
- 在後端驗證 LIFF 的 ID token

### 2. 最佳實踐

- 使用 Loading 指示器顯示 LIFF 初始化過程
- 實現錯誤處理機制
- 考慮在非 LINE 環境中的用戶體驗
- 保持 LIFF SDK 版本更新

## 第七部分：進階功能

### 1. 共享目標選擇器

如果您希望用戶能夠共享內容到聊天，可以使用：

```javascript
liff.shareTargetPicker([
  {
    type: "text",
    text: "查看我的任務：https://liff.line.me/您的LIFF_ID"
  }
]);
```

### 2. 獲取用戶資料

獲取登錄用戶的個人資料：

```javascript
const getUserProfile = async () => {
  if (liff.isLoggedIn()) {
    const profile = await liff.getProfile();
    return profile;
  }
};
```

### 3. 向 LINE Bot 發送消息

從 LIFF 應用向 LINE Bot 發送消息：

```javascript
liff.sendMessages([
  {
    type: 'text',
    text: '任務已創建！'
  }
]);
```

## 結論

正確配置 LIFF 應用是 LINE 平台整合的關鍵部分。通過本指南，您應該能夠成功創建、配置和部署 LIFF 應用，實現與 LINE 平台的無縫集成。請確保定期檢查 [LINE Developers 文檔](https://developers.line.biz/en/docs/liff/) 以獲取最新的 API 更新和最佳實踐。 