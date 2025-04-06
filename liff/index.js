import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom';
import liff from '@line/liff';
import './index.css';
import App from './App';

// 初始化 LIFF
const initializeLiff = async () => {
  try {
    const liffId = process.env.REACT_APP_LIFF_ID;
    console.log('LIFF ID:', liffId);
    await liff.init({ liffId });
    console.log('LIFF initialization succeeded');
    
    // 檢查是否在 LINE 環境中
    if (liff.isInClient()) {
      console.log('Running in LINE client');
    } else {
      console.log('Running in external browser');
    }
    
    // 如果用戶未登錄且不在 LINE App 內，進行登錄
    if (!liff.isLoggedIn() && !liff.isInClient()) {
      liff.login();
    }
  } catch (err) {
    console.error('LIFF initialization failed', err);
  }
};

// 渲染應用程序前初始化 LIFF
initializeLiff().then(() => {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <Router>
        <App />
      </Router>
    </React.StrictMode>
  );
});

// 註冊 Service Worker 實現 PWA 功能
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/serviceWorker.js')
      .then(registration => {
        console.log('Service Worker 註冊成功:', registration);
      })
      .catch(error => {
        console.error('Service Worker 註冊失敗:', error);
      });
  });
} 