# PWA 圖標需求

為了讓 PWA 在各種平台上顯示正確的圖標，您需要準備以下圖標檔案並放置在此目錄中：

1. `favicon.ico` - 16x16, 32x32, 48x48 像素的網站圖標
2. `logo192.png` - 192x192 像素的 PWA 圖標
3. `logo512.png` - 512x512 像素的 PWA 圖標
4. `maskable_icon.png` - 用於 Android 的自適應圖標 (至少 512x512 像素)

您可以使用設計工具如 Figma, Sketch, Photoshop 等創建這些圖標，
或使用線上工具如 https://app-manifest.firebaseapp.com/ 或 https://www.pwabuilder.com/imageGenerator
來自動生成所需的所有尺寸。

確保所有圖像都具有相同的品牌風格，且在各種背景上都能清晰可見。

對於 maskable 圖標，請確保重要內容位於安全區域內（中心 80% 的區域），
因為在某些平台上圖標可能會被裁剪成圓形或圓角方形。 