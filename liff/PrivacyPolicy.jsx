import React from 'react';

const PrivacyPolicy = () => {
  return (
    <div className="bg-white min-h-screen p-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-center">隱私政策</h1>
        
        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-xl font-semibold mb-2">1. 引言</h2>
            <p>我們尊重您的隱私並致力於保護您的個人數據。本隱私政策說明了我們如何收集、使用、處理和保護您通過我們的應用程序「Kimi 任務管理」（以下簡稱「應用程序」）提供的信息。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">2. 收集的信息</h2>
            <p>我們可能會收集以下類型的信息：</p>
            <ul className="list-disc pl-6 mt-2">
              <li><strong>個人信息</strong>：當您使用 LINE 登錄我們的應用程序時，我們可能會收到您的 LINE 用戶 ID、顯示名稱和頭像。</li>
              <li><strong>任務數據</strong>：您在應用程序中創建的任務信息，包括任務名稱、截止日期、提醒時間和重複設置。</li>
              <li><strong>使用數據</strong>：關於您如何使用我們的應用程序的信息，包括訪問時間、使用的功能和偏好設置。</li>
              <li><strong>設備信息</strong>：設備類型、操作系統版本和瀏覽器類型等技術信息。</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">3. 信息使用</h2>
            <p>我們使用收集的信息：</p>
            <ul className="list-disc pl-6 mt-2">
              <li>提供、維護和改進我們的應用程序和服務</li>
              <li>處理和管理您的任務和提醒</li>
              <li>與您溝通，包括通過 LINE 提供任務提醒</li>
              <li>監控和分析使用趨勢，以改善用戶體驗</li>
              <li>檢測、預防和解決技術問題和安全問題</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">4. 信息共享</h2>
            <p>我們不會出售或出租您的個人數據給第三方。但在以下情況下，我們可能會共享您的信息：</p>
            <ul className="list-disc pl-6 mt-2">
              <li><strong>服務提供商</strong>：我們使用第三方服務提供商來幫助我們運營我們的應用程序，這些提供商可能會訪問您的信息以執行這些功能。</li>
              <li><strong>LINE 平台</strong>：作為 LINE 集成的一部分，某些數據會通過 LINE Messaging API 共享。</li>
              <li><strong>法律要求</strong>：如果我們相信披露是必要的，以遵守適用法律、法規或法律程序。</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">5. 數據安全</h2>
            <p>我們實施了合理的安全措施來保護您的個人數據不被未經授權的訪問、使用或披露。然而，沒有任何互聯網傳輸或電子存儲方法是 100% 安全的。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">6. 數據保留</h2>
            <p>我們將只在必要時保留您的個人數據，以實現本隱私政策中概述的目的，除非法律要求或允許更長的保留期。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">7. 您的權利</h2>
            <p>根據您所在地區的適用法律，您可能擁有以下權利：</p>
            <ul className="list-disc pl-6 mt-2">
              <li>訪問您的個人數據</li>
              <li>更正不准確的數據</li>
              <li>刪除您的數據</li>
              <li>限制或反對處理</li>
              <li>數據可攜性</li>
            </ul>
            <p className="mt-2">如果您希望行使這些權利，請通過以下「聯繫我們」部分中的詳細信息與我們聯繫。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">8. Cookie 政策</h2>
            <p>我們的網絡應用程序使用 cookie 和類似技術來提供和改進我們的服務。您可以通過瀏覽器設置控制這些技術的使用。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">9. 兒童隱私</h2>
            <p>我們的服務不針對 13 歲以下的兒童。我們不會故意收集 13 歲以下兒童的個人可識別信息。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">10. 隱私政策變更</h2>
            <p>我們可能會不時更新我們的隱私政策。我們將通過在應用程序中發布新的隱私政策通知您任何變更。建議您定期查看此隱私政策是否有任何變更。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">11. 聯繫我們</h2>
            <p>如果您對本隱私政策有任何疑問，請通過 example@example.com 聯繫我們。</p>
          </section>
        </div>
        
        <div className="mt-8 pb-10">
          <button 
            onClick={() => window.history.back()} 
            className="bg-[#FFC940] text-white font-bold py-2 px-6 rounded-full shadow-md hover:bg-[#FFB800] transition duration-300"
          >
            返回
          </button>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy; 