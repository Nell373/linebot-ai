// API 服務，用於與後端通信
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.example.com';

// 儲存使用者識別資訊的函數
const saveUserToken = (token) => {
  localStorage.setItem('user_token', token);
};

// 獲取使用者識別資訊的函數
const getUserToken = () => {
  return localStorage.getItem('user_token');
};

// 創建任務的函數
const createTask = async (taskData) => {
  try {
    const token = getUserToken();
    if (!token) {
      throw new Error('未登入，請先登入');
    }

    const response = await fetch(`${API_BASE_URL}/api/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(taskData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || '創建任務失敗');
    }

    return await response.json();
  } catch (error) {
    console.error('API 錯誤:', error);
    throw error;
  }
};

// 使用者登入函數
const login = async (lineCode) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/line`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code: lineCode })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || '登入失敗');
    }

    const data = await response.json();
    if (data.token) {
      saveUserToken(data.token);
    }
    return data;
  } catch (error) {
    console.error('登入錯誤:', error);
    throw error;
  }
};

// 獲取 URL 參數的輔助函數
const getUrlParameter = (name) => {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
};

// 檢查並處理登入狀態
const checkLoginStatus = async () => {
  // 檢查是否有儲存的 token
  const token = getUserToken();
  if (token) {
    return true;
  }

  // 檢查 URL 中是否有 LINE 授權碼
  const code = getUrlParameter('code');
  if (code) {
    try {
      await login(code);
      return true;
    } catch (error) {
      console.error('自動登入失敗:', error);
      return false;
    }
  }

  return false;
};

// 導向到 LINE 登入頁面
const redirectToLineLogin = () => {
  const LINE_CLIENT_ID = process.env.REACT_APP_LINE_CLIENT_ID;
  const REDIRECT_URI = encodeURIComponent(window.location.origin);
  
  window.location.href = `https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=${LINE_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&state=12345&scope=profile%20openid&bot_prompt=aggressive`;
};

export {
  createTask,
  checkLoginStatus,
  redirectToLineLogin,
  getUserToken
}; 