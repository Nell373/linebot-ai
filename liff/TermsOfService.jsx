import React from 'react';

const TermsOfService = () => {
  return (
    <div className="bg-white min-h-screen p-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-center">服務條款</h1>
        
        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-xl font-semibold mb-2">1. 接受條款</h2>
            <p>歡迎使用 Kimi 任務管理服務（以下簡稱「本服務」）。通過訪問或使用我們的網站、服務或應用程序，您同意遵守本服務條款（以下簡稱「條款」）。如果您不同意這些條款，請不要使用本服務。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">2. 服務描述</h2>
            <p>本服務提供任務管理功能，允許用戶創建、查看、編輯和刪除任務，設置提醒，並與 LINE 機器人集成。我們保留隨時修改、暫停或終止全部或部分服務的權利，恕不另行通知。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">3. 用戶帳戶</h2>
            <p>為了使用本服務的某些功能，您可能需要使用 LINE 帳號登錄。您有責任維護您帳戶的機密性，並對在您帳戶下發生的所有活動負全責。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">4. 用戶行為</h2>
            <p>您同意不會使用本服務進行任何非法或未經授權的活動，包括但不限於：</p>
            <ul className="list-disc pl-6 mt-2">
              <li>收集或收穫用戶數據</li>
              <li>干擾服務的正常運行</li>
              <li>上傳惡意代碼或試圖破壞系統安全</li>
              <li>使用本服務分發垃圾郵件或廣告</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">5. 知識產權</h2>
            <p>本服務及其原始內容、功能和設計受國際著作權、商標、專利、商業秘密和其他知識產權或專有權利法律的保護。您同意不會複制、修改、分發、銷售或出租本服務的任何部分。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">6. 責任限制</h2>
            <p>在法律允許的最大範圍內，我們對因使用或無法使用本服務而引起的任何直接、間接、偶然、特殊、衍生或懲罰性損害不承擔責任，包括但不限於數據丟失、利潤損失或業務中斷。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">7. 終止</h2>
            <p>我們可以根據自己的判斷，以任何理由隨時終止或暫停您對本服務的訪問，恕不另行通知，包括但不限於違反這些條款。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">8. 變更</h2>
            <p>我們保留隨時修改或替換這些條款的權利。如果修訂是重大的，我們將嘗試提前至少 30 天通知您。重大變更的定義由我們自行決定。</p>
          </section>
          
          <section>
            <h2 className="text-xl font-semibold mb-2">9. 聯繫我們</h2>
            <p>如果您對這些條款有任何疑問，請通過 example@example.com 聯繫我們。</p>
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

export default TermsOfService; 