import React, { useState, useEffect } from 'react';
import { liff } from '@line/liff';

const TaskForm = () => {
  // 表單狀態
  const [formData, setFormData] = useState({
    taskName: '',
    reminderTime: '早上',
    customTime: '',
    reminderDate: '今天',
    customDate: '',
    repeatCycle: '不重複',
    endCondition: '無結束',
    repeatTimes: 1,
    endDate: '',
    addToCheckboxList: false,
  });

  // 錯誤訊息狀態
  const [errors, setErrors] = useState({});
  
  // 是否顯示自訂時間選擇器
  const [showCustomTime, setShowCustomTime] = useState(false);
  
  // 是否顯示自訂日期選擇器
  const [showCustomDate, setShowCustomDate] = useState(false);
  
  // 是否顯示重複次數輸入框
  const [showRepeatTimes, setShowRepeatTimes] = useState(false);
  
  // 是否顯示結束日期選擇器
  const [showEndDate, setShowEndDate] = useState(false);
  
  // 表單提交狀態
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // 初始化 LIFF
  useEffect(() => {
    const initializeLiff = async () => {
      try {
        await liff.init({ liffId: process.env.REACT_APP_LIFF_ID || '' });
        if (!liff.isLoggedIn()) {
          liff.login();
        }
      } catch (error) {
        console.error('LIFF initialization failed', error);
      }
    };
    
    initializeLiff();
  }, []);

  // 處理表單輸入變更
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setFormData({
      ...formData,
      [name]: newValue
    });
    
    // 清除對應欄位的錯誤訊息
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: undefined
      });
    }
    
    // 處理特定欄位的連動邏輯
    if (name === 'reminderTime') {
      setShowCustomTime(value === '自訂時間');
    } else if (name === 'reminderDate') {
      setShowCustomDate(value === '自訂週期');
    } else if (name === 'endCondition') {
      setShowRepeatTimes(value === '重複 N 次');
      setShowEndDate(value === '到某日為止');
    }
  };

  // 表單驗證
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.taskName.trim()) {
      newErrors.taskName = '請輸入任務名稱';
    }
    
    if (showCustomTime && !formData.customTime) {
      newErrors.customTime = '請選擇時間';
    }
    
    if (showCustomDate && !formData.customDate) {
      newErrors.customDate = '請選擇日期';
    }
    
    if (showRepeatTimes && (!formData.repeatTimes || formData.repeatTimes < 1)) {
      newErrors.repeatTimes = '請輸入有效的重複次數';
    }
    
    if (showEndDate && !formData.endDate) {
      newErrors.endDate = '請選擇結束日期';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 重置表單
  const handleReset = () => {
    setFormData({
      taskName: '',
      reminderTime: '早上',
      customTime: '',
      reminderDate: '今天',
      customDate: '',
      repeatCycle: '不重複',
      endCondition: '無結束',
      repeatTimes: 1,
      endDate: '',
      addToCheckboxList: false,
    });
    setErrors({});
    setShowCustomTime(false);
    setShowCustomDate(false);
    setShowRepeatTimes(false);
    setShowEndDate(false);
    setSubmitSuccess(false);
  };

  // 處理表單提交
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // 準備傳送的任務資料
      const taskData = {
        type: 'task',
        data: {
          name: formData.taskName,
          reminderTime: formData.reminderTime === '自訂時間' ? formData.customTime : formData.reminderTime,
          reminderDate: formData.reminderDate === '自訂週期' ? formData.customDate : formData.reminderDate,
          repeatCycle: formData.repeatCycle,
          endCondition: formData.endCondition,
          repeatTimes: formData.endCondition === '重複 N 次' ? formData.repeatTimes : null,
          endDate: formData.endCondition === '到某日為止' ? formData.endDate : null,
          addToCheckboxList: formData.addToCheckboxList
        }
      };
      
      if (liff.isInClient()) {
        // 使用 LIFF sendMessages API 傳送資料回 LINE Bot
        await liff.sendMessages([
          {
            type: 'text',
            text: JSON.stringify(taskData)
          }
        ]);
        
        setSubmitSuccess(true);
        
        // 成功傳送後，2秒後關閉 LIFF
        setTimeout(() => {
          liff.closeWindow();
        }, 2000);
      } else {
        // 開發環境中，顯示資料
        console.log('表單提交數據:', taskData);
        setSubmitSuccess(true);
      }
    } catch (error) {
      console.error('提交表單時發生錯誤', error);
      setErrors({
        ...errors,
        submit: '提交失敗，請稍後再試'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white min-h-screen flex flex-col items-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* 表頭 */}
        <div className="bg-[#FFC940] p-4 text-center">
          <h1 className="text-2xl font-bold text-white">新增任務</h1>
        </div>
        
        {/* 表單區域 */}
        <form onSubmit={handleSubmit} className="p-6 bg-[#FFFBE6] rounded-b-2xl">
          {/* 任務名稱 */}
          <div className="mb-6">
            <label className="block text-[#595959] font-semibold mb-2" htmlFor="taskName">
              📝 任務名稱 <span className="text-[#FAAD14]">*</span>
            </label>
            <input
              type="text"
              id="taskName"
              name="taskName"
              value={formData.taskName}
              onChange={handleInputChange}
              className={`w-full p-3 border ${errors.taskName ? 'border-red-500' : 'border-[#D9D9D9]'} rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FFC940] bg-white`}
              placeholder="輸入任務名稱"
            />
            {errors.taskName && <p className="text-red-500 text-sm mt-1">{errors.taskName}</p>}
          </div>
          
          {/* 提醒時間 */}
          <div className="mb-6">
            <label className="block text-[#595959] font-semibold mb-2">
              ⏰ 提醒時間
            </label>
            <div className="grid grid-cols-2 gap-3 mb-3">
              {['早上', '下午', '晚上', '自訂時間'].map((time) => (
                <label 
                  key={time} 
                  className={`flex items-center justify-center p-3 rounded-xl cursor-pointer transition-all ${
                    formData.reminderTime === time 
                      ? 'bg-[#FFC940] text-white font-medium' 
                      : 'bg-white border border-[#D9D9D9] hover:bg-[#FFFBE6]'
                  }`}
                >
                  <input
                    type="radio"
                    name="reminderTime"
                    value={time}
                    checked={formData.reminderTime === time}
                    onChange={handleInputChange}
                    className="sr-only"
                  />
                  {time}
                </label>
              ))}
            </div>
            
            {showCustomTime && (
              <div className="mt-3">
                <input
                  type="time"
                  id="customTime"
                  name="customTime"
                  value={formData.customTime}
                  onChange={handleInputChange}
                  className={`w-full p-3 border ${errors.customTime ? 'border-red-500' : 'border-[#D9D9D9]'} rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FFC940] bg-white`}
                />
                {errors.customTime && <p className="text-red-500 text-sm mt-1">{errors.customTime}</p>}
              </div>
            )}
          </div>
          
          {/* 提醒日期 */}
          <div className="mb-6">
            <label className="block text-[#595959] font-semibold mb-2">
              📅 提醒日期
            </label>
            <div className="space-y-3">
              {['今天', '明天', '每週一三五', '自訂週期'].map((date) => (
                <label 
                  key={date} 
                  className={`flex items-center p-3 rounded-xl cursor-pointer transition-all ${
                    formData.reminderDate === date 
                      ? 'bg-[#FFC940] text-white font-medium' 
                      : 'bg-white border border-[#D9D9D9] hover:bg-[#FFFBE6]'
                  }`}
                >
                  <input
                    type="radio"
                    name="reminderDate"
                    value={date}
                    checked={formData.reminderDate === date}
                    onChange={handleInputChange}
                    className="sr-only"
                  />
                  {date}
                </label>
              ))}
            </div>
            
            {showCustomDate && (
              <div className="mt-3">
                <input
                  type="date"
                  id="customDate"
                  name="customDate"
                  value={formData.customDate}
                  onChange={handleInputChange}
                  className={`w-full p-3 border ${errors.customDate ? 'border-red-500' : 'border-[#D9D9D9]'} rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FFC940] bg-white`}
                />
                {errors.customDate && <p className="text-red-500 text-sm mt-1">{errors.customDate}</p>}
              </div>
            )}
          </div>
          
          {/* 重複週期 */}
          <div className="mb-6">
            <label className="block text-[#595959] font-semibold mb-2" htmlFor="repeatCycle">
              🔄 重複週期
            </label>
            <select
              id="repeatCycle"
              name="repeatCycle"
              value={formData.repeatCycle}
              onChange={handleInputChange}
              className="w-full p-3 border border-[#D9D9D9] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FFC940] bg-white"
            >
              <option value="不重複">不重複</option>
              <option value="每日">每日</option>
              <option value="每週">每週</option>
              <option value="每月">每月</option>
              <option value="每月最後一天">每月最後一天</option>
            </select>
          </div>
          
          {/* 結束條件 */}
          <div className="mb-6">
            <label className="block text-[#595959] font-semibold mb-2">
              🏁 結束條件
            </label>
            <div className="space-y-3">
              {['無結束', '重複 N 次', '到某日為止'].map((condition) => (
                <label 
                  key={condition} 
                  className={`flex items-center p-3 rounded-xl cursor-pointer transition-all ${
                    formData.endCondition === condition 
                      ? 'bg-[#FFC940] text-white font-medium' 
                      : 'bg-white border border-[#D9D9D9] hover:bg-[#FFFBE6]'
                  }`}
                >
                  <input
                    type="radio"
                    name="endCondition"
                    value={condition}
                    checked={formData.endCondition === condition}
                    onChange={handleInputChange}
                    className="sr-only"
                  />
                  {condition}
                </label>
              ))}
            </div>
            
            {showRepeatTimes && (
              <div className="mt-3">
                <input
                  type="number"
                  id="repeatTimes"
                  name="repeatTimes"
                  value={formData.repeatTimes}
                  onChange={handleInputChange}
                  min="1"
                  className={`w-full p-3 border ${errors.repeatTimes ? 'border-red-500' : 'border-[#D9D9D9]'} rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FFC940] bg-white`}
                  placeholder="請輸入重複次數"
                />
                {errors.repeatTimes && <p className="text-red-500 text-sm mt-1">{errors.repeatTimes}</p>}
              </div>
            )}
            
            {showEndDate && (
              <div className="mt-3">
                <input
                  type="date"
                  id="endDate"
                  name="endDate"
                  value={formData.endDate}
                  onChange={handleInputChange}
                  className={`w-full p-3 border ${errors.endDate ? 'border-red-500' : 'border-[#D9D9D9]'} rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FFC940] bg-white`}
                />
                {errors.endDate && <p className="text-red-500 text-sm mt-1">{errors.endDate}</p>}
              </div>
            )}
          </div>
          
          {/* 加入 Check Box 清單 */}
          <div className="mb-8">
            <label className="flex items-center space-x-3 cursor-pointer">
              <div className="relative">
                <input
                  type="checkbox"
                  name="addToCheckboxList"
                  checked={formData.addToCheckboxList}
                  onChange={handleInputChange}
                  className="sr-only peer"
                />
                <div className="w-12 h-6 bg-gray-200 rounded-full peer peer-checked:bg-[#FFC940] peer-focus:ring-2 peer-focus:ring-[#FFE58F] transition-colors"></div>
                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition peer-checked:translate-x-6"></div>
              </div>
              <span className="text-[#595959] font-medium">加入 Check Box 清單</span>
            </label>
          </div>
          
          {/* 提交錯誤訊息 */}
          {errors.submit && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-xl">
              {errors.submit}
            </div>
          )}
          
          {/* 提交成功訊息 */}
          {submitSuccess && (
            <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-xl">
              任務已成功建立！
            </div>
          )}
          
          {/* 表單按鈕 */}
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={handleReset}
              className="p-3 bg-white border border-[#D9D9D9] rounded-xl text-[#8C8C8C] font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#FFE58F] transition-all"
              disabled={isSubmitting}
            >
              🔁 重新填寫
            </button>
            <button
              type="submit"
              className="p-3 bg-[#FFC940] rounded-xl text-white font-medium hover:bg-[#FAAD14] focus:outline-none focus:ring-2 focus:ring-[#FFE58F] transition-all"
              disabled={isSubmitting}
            >
              {isSubmitting ? '提交中...' : '✅ 確認建立'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskForm; 