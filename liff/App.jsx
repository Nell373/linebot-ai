import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import TaskForm from './TaskForm';
import TermsConsent from './TermsConsent';
import TermsOfService from './TermsOfService';
import PrivacyPolicy from './PrivacyPolicy';
import { checkLoginStatus, redirectToLineLogin } from './apiService';

const App = () => {
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const isAuthenticated = await checkLoginStatus();
        
        if (!isAuthenticated) {
          // 如果在開發環境中，我們可以假設用戶已登入
          if (process.env.NODE_ENV === 'development') {
            setIsLoggedIn(true);
          } else {
            // 在生產環境中，我們需要重定向到 LINE 登錄頁面
            redirectToLineLogin();
            return;
          }
        } else {
          setIsLoggedIn(true);
        }
      } catch (error) {
        console.error('驗證狀態檢查失敗:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  // 處理條款同意
  const handleTermsAccept = () => {
    setTermsAccepted(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#FFFBE6]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#FFC940] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">載入中...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={
          isLoggedIn ? (
            <>
              <TermsConsent onAccept={handleTermsAccept} />
              <TaskForm />
            </>
          ) : (
            <Navigate to="/login" />
          )
        } />
        <Route path="/login" element={
          <div className="flex items-center justify-center min-h-screen bg-[#FFFBE6] p-4">
            <div className="bg-white p-6 rounded-xl shadow-lg max-w-sm w-full">
              <h1 className="text-2xl font-bold text-center mb-6">歡迎使用 Kimi 任務管理</h1>
              <p className="text-gray-600 mb-6 text-center">請使用 LINE 帳號登入以繼續使用服務</p>
              <button 
                onClick={redirectToLineLogin}
                className="w-full py-3 bg-[#06C755] text-white rounded-lg font-bold flex items-center justify-center"
              >
                <svg className="w-6 h-6 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19.952,12.003c0-5.031-5.049-9.125-11.256-9.125S-2.56,6.972-2.56,12.003c0,4.511,4.004,8.29,9.412,9.003c1.339,0.289,1.183,0.775,0.883,2.573c-0.039,0.188-0.18,0.736,0.646,0.406c0.827-0.329,4.46-2.627,6.086-4.5l0,0C17.608,16.408,19.952,14.34,19.952,12.003z" />
                </svg>
                使用 LINE 登入
              </button>
            </div>
          </div>
        } />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
      </Routes>
    </Router>
  );
};

export default App; 