import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const TermsConsent = ({ onAccept }) => {
  const [accepted, setAccepted] = useState(false);
  
  useEffect(() => {
    // 檢查用戶是否已接受條款
    const hasAccepted = localStorage.getItem('termsAccepted');
    if (hasAccepted) {
      setAccepted(true);
      onAccept();
    }
  }, [onAccept]);
  
  const handleAccept = () => {
    localStorage.setItem('termsAccepted', 'true');
    setAccepted(true);
    onAccept();
  };
  
  if (accepted) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl p-4 max-w-md max-h-[90vh] overflow-auto">
        <h2 className="text-xl font-bold text-center mb-4">服務條款與隱私政策</h2>
        
        <div className="mb-4">
          <h3 className="font-bold">服務條款摘要</h3>
          <p className="text-sm mb-2">
            使用本應用即表示您同意我們的服務條款。我們提供任務管理服務，
            您需要負責任地使用本服務，不得用於非法活動。
          </p>
          <Link to="/terms" className="text-[#FFC940] text-sm underline">查看完整服務條款</Link>
        </div>
        
        <div className="mb-6">
          <h3 className="font-bold">隱私政策摘要</h3>
          <p className="text-sm mb-2">
            我們收集您的任務數據和使用信息以提供和改進服務。我們不會
            未經您的許可將您的個人數據共享給第三方。
          </p>
          <Link to="/privacy" className="text-[#FFC940] text-sm underline">查看完整隱私政策</Link>
        </div>
        
        <button
          onClick={handleAccept}
          className="w-full bg-[#FFC940] text-white py-2 rounded-lg font-bold"
        >
          我已閱讀並同意
        </button>
      </div>
    </div>
  );
};

export default TermsConsent; 