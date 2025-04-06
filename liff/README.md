# Kimi 任務建立 LIFF 應用

這是一個使用 React 和 Tailwind CSS 建立的 LIFF 應用，用於在 LINE 中創建任務。

## 功能特點

- 符合 Kimi 的品牌風格（黃色系、圓角大、間距寬鬆）
- 支援多種任務設定選項：
  - 任務名稱
  - 提醒時間（早上、下午、晚上、自訂時間）
  - 提醒日期（今天、明天、每週一三五、自訂週期）
  - 重複週期（不重複、每日、每週、每月、每月最後一天）
  - 結束條件（無結束、重複 N 次、到某日為止）
  - 是否加入 Check Box 清單
- 表單驗證和錯誤提示
- 使用 LIFF SDK 將任務資料傳回 LINE Bot

## 前置需求

- Node.js 14.x 或更高版本
- 已創建的 LINE LIFF 應用（需要 LIFF ID）

## 安裝與使用

1. 安裝依賴：

```bash
cd liff
npm install
```

2. 設定環境變數：

創建 `.env` 文件並添加您的 LIFF ID：

```
REACT_APP_LIFF_ID=your-liff-id-here
```

3. 啟動開發伺服器：

```bash
npm start
```

4. 建置用於生產環境的應用：

```bash
npm run build
```

建置後的文件將位於 `build` 資料夾中。

## 部署

您可以將建置後的應用程序部署到任何靜態網站託管服務，例如：

- Vercel
- Netlify
- GitHub Pages
- Firebase Hosting
- 您自己的 Web 伺服器

部署後，請確保在 LINE Developers Console 中更新您的 LIFF 應用程序的 Endpoint URL。

## 資料格式

當用戶填寫並提交表單時，應用會透過 LIFF 的 `sendMessages()` API 將資料以 JSON 格式傳回 LINE Bot：

```json
{
  "type": "task",
  "data": {
    "name": "任務名稱",
    "reminderTime": "早上",
    "reminderDate": "今天",
    "repeatCycle": "不重複",
    "endCondition": "無結束",
    "repeatTimes": null,
    "endDate": null,
    "addToCheckboxList": false
  }
}
```

## 開發須知

- 若要修改表單欄位，請編輯 `TaskForm.jsx` 文件。
- 若要調整樣式，可以在 `tailwind.config.js` 中修改主題配置，或直接在組件中使用 Tailwind CSS 類名。
- 若要測試非 LINE 環境中的表單行為，請查看瀏覽器控制台，應用會在其中輸出表單資料。 