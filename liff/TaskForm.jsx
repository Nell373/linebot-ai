import React, { useState } from 'react';
import { createTask } from './apiService';

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
        name: formData.taskName,
        reminderTime: formData.reminderTime === '自訂時間' ? formData.customTime : formData.reminderTime,
        reminderDate: formData.reminderDate === '自訂週期' ? formData.customDate : formData.reminderDate,
        repeatCycle: formData.repeatCycle,
        endCondition: formData.endCondition,
        repeatTimes: formData.endCondition === '重複 N 次' ? formData.repeatTimes : null,
        endDate: formData.endCondition === '到某日為止' ? formData.endDate : null,
        addToCheckboxList: formData.addToCheckboxList
      };
      
      // 使用 API 服務發送任務數據
      await createTask(taskData);
      
      setSubmitSuccess(true);
      
      // 延遲重置表單，讓用戶有時間看到成功訊息
      setTimeout(() => {
        handleReset();
      }, 3000);
    } catch (error) {
      console.error('提交表單時發生錯誤', error);
      setErrors({
        ...errors,
        submit: error.message || '提交失敗，請稍後再試'
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
            <label htmlFor="taskName" className="block text-gray-700 font-medium mb-2">
              任務名稱
            </label>
            <input
              type="text"
              id="taskName"
              name="taskName"
              value={formData.taskName}
              onChange={handleInputChange}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                errors.taskName ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-[#FFC940]'
              }`}
              placeholder="請輸入任務名稱"
            />
            {errors.taskName && (
              <p className="text-red-500 text-sm mt-1">{errors.taskName}</p>
            )}
          </div>
          
          {/* 提醒時間 */}
          <div className="mb-6">
            <label htmlFor="reminderTime" className="block text-gray-700 font-medium mb-2">
              提醒時間
            </label>
            <select
              id="reminderTime"
              name="reminderTime"
              value={formData.reminderTime}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFC940]"
            >
              <option value="早上">早上</option>
              <option value="中午">中午</option>
              <option value="下午">下午</option>
              <option value="晚上">晚上</option>
              <option value="自訂時間">自訂時間</option>
            </select>
            
            {showCustomTime && (
              <div className="mt-3">
                <input
                  type="time"
                  id="customTime"
                  name="customTime"
                  value={formData.customTime}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                    errors.customTime ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-[#FFC940]'
                  }`}
                />
                {errors.customTime && (
                  <p className="text-red-500 text-sm mt-1">{errors.customTime}</p>
                )}
              </div>
            )}
          </div>
          
          {/* 提醒日期 */}
          <div className="mb-6">
            <label htmlFor="reminderDate" className="block text-gray-700 font-medium mb-2">
              提醒日期
            </label>
            <select
              id="reminderDate"
              name="reminderDate"
              value={formData.reminderDate}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFC940]"
            >
              <option value="今天">今天</option>
              <option value="明天">明天</option>
              <option value="後天">後天</option>
              <option value="本週末">本週末</option>
              <option value="下週一">下週一</option>
              <option value="自訂週期">自訂日期</option>
            </select>
            
            {showCustomDate && (
              <div className="mt-3">
                <input
                  type="date"
                  id="customDate"
                  name="customDate"
                  value={formData.customDate}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                    errors.customDate ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-[#FFC940]'
                  }`}
                />
                {errors.customDate && (
                  <p className="text-red-500 text-sm mt-1">{errors.customDate}</p>
                )}
              </div>
            )}
          </div>
          
          {/* 重複週期 */}
          <div className="mb-6">
            <label htmlFor="repeatCycle" className="block text-gray-700 font-medium mb-2">
              重複週期
            </label>
            <select
              id="repeatCycle"
              name="repeatCycle"
              value={formData.repeatCycle}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFC940]"
            >
              <option value="不重複">不重複</option>
              <option value="每天">每天</option>
              <option value="每週">每週</option>
              <option value="每兩週">每兩週</option>
              <option value="每月">每月</option>
              <option value="每年">每年</option>
            </select>
          </div>
          
          {/* 如果選擇重複，顯示結束條件 */}
          {formData.repeatCycle !== '不重複' && (
            <div className="mb-6">
              <label htmlFor="endCondition" className="block text-gray-700 font-medium mb-2">
                結束條件
              </label>
              <select
                id="endCondition"
                name="endCondition"
                value={formData.endCondition}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFC940]"
              >
                <option value="無結束">無結束</option>
                <option value="重複 N 次">重複 N 次</option>
                <option value="到某日為止">到某日為止</option>
              </select>
              
              {showRepeatTimes && (
                <div className="mt-3">
                  <input
                    type="number"
                    id="repeatTimes"
                    name="repeatTimes"
                    min="1"
                    value={formData.repeatTimes}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.repeatTimes ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-[#FFC940]'
                    }`}
                  />
                  {errors.repeatTimes && (
                    <p className="text-red-500 text-sm mt-1">{errors.repeatTimes}</p>
                  )}
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
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      errors.endDate ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-[#FFC940]'
                    }`}
                  />
                  {errors.endDate && (
                    <p className="text-red-500 text-sm mt-1">{errors.endDate}</p>
                  )}
                </div>
              )}
            </div>
          )}
          
          {/* 加入到待辦清單 */}
          <div className="mb-6">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="addToCheckboxList"
                name="addToCheckboxList"
                checked={formData.addToCheckboxList}
                onChange={handleInputChange}
                className="w-5 h-5 text-[#FFC940] border-gray-300 rounded focus:ring-[#FFC940]"
              />
              <label htmlFor="addToCheckboxList" className="ml-2 block text-gray-700">
                同時加入到待辦清單
              </label>
            </div>
          </div>
          
          {/* 錯誤訊息 */}
          {errors.submit && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {errors.submit}
            </div>
          )}
          
          {/* 成功訊息 */}
          {submitSuccess && (
            <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
              任務建立成功！
            </div>
          )}
          
          {/* 提交按鈕 */}
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={handleReset}
              className="flex-1 py-2 px-4 border border-[#FFC940] text-[#FFC940] rounded-lg hover:bg-[#FFF8D6] focus:outline-none focus:ring-2 focus:ring-[#FFC940] transition duration-200"
              disabled={isSubmitting}
            >
              重置
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 bg-[#FFC940] text-white rounded-lg hover:bg-[#FFB800] focus:outline-none focus:ring-2 focus:ring-[#FFC940] transition duration-200"
              disabled={isSubmitting}
            >
              {isSubmitting ? '處理中...' : '建立任務'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskForm; 