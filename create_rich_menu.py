#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LINE Rich Menu 設置腳本
用於創建和上傳 LINE Bot 的圖文選單
"""

import os
import json
import requests
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    RichMenuRequest,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    URIAction
)

# 載入環境變數
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
LIFF_ID = os.environ.get('LIFF_ID', '')

# 如果環境變數未設置，嘗試從 .env 文件讀取
if not CHANNEL_ACCESS_TOKEN or not LIFF_ID:
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('LINE_CHANNEL_ACCESS_TOKEN='):
                    CHANNEL_ACCESS_TOKEN = line.strip().split('=')[1]
                elif line.startswith('LIFF_ID='):
                    LIFF_ID = line.strip().split('=')[1]
    except:
        print('無法讀取 .env 文件')

if not CHANNEL_ACCESS_TOKEN:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN 未設置")
if not LIFF_ID:
    raise ValueError("LIFF_ID 未設置")

# 初始化 LINE API
configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

def create_rich_menu():
    """創建 Rich Menu"""
    
    # 網站 URL (改用部署的網站而非LIFF)
    app_url = "https://linebot-ai.fly.dev"
    
    # Rich Menu 資料結構
    rich_menu_data = {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": True,
        "name": "Kimi 助手選單",
        "chatBarText": "點擊開啟選單",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 1250,
                    "height": 843
                },
                "action": {
                    "type": "message",
                    "text": "任務管理",
                    "label": "任務管理"
                }
            },
            {
                "bounds": {
                    "x": 1250,
                    "y": 0,
                    "width": 1250,
                    "height": 843
                },
                "action": {
                    "type": "message",
                    "text": "財務管理",
                    "label": "財務管理"
                }
            },
            {
                "bounds": {
                    "x": 0,
                    "y": 843,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "message",
                    "text": "kimi",
                    "label": "選單"
                }
            },
            {
                "bounds": {
                    "x": 833,
                    "y": 843,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "message",
                    "text": "kimi help",
                    "label": "幫助"
                }
            },
            {
                "bounds": {
                    "x": 1666,
                    "y": 843,
                    "width": 834,
                    "height": 843
                },
                "action": {
                    "type": "message",
                    "text": "設定",
                    "label": "設定"
                }
            }
        ]
    }
    
    # 使用 v3 SDK 創建 Rich Menu
    try:
        headers = {
            'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        response = requests.post(
            'https://api.line.me/v2/bot/richmenu',
            headers=headers,
            json=rich_menu_data
        )
        
        if response.status_code == 200:
            rich_menu_id = response.json().get('richMenuId')
            print(f"Rich Menu 創建成功: {rich_menu_id}")
            return rich_menu_id
        else:
            print(f"創建 Rich Menu 失敗: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"創建 Rich Menu 失敗: {e}")
        return None

def upload_rich_menu_image(rich_menu_id, image_path):
    """上傳 Rich Menu 圖片"""
    if not os.path.exists(image_path):
        print(f"找不到圖片: {image_path}")
        return False
    
    try:
        # 使用原始 requests 上傳圖片
        with open(image_path, 'rb') as f:
            url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
            headers = {
                'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
                'Content-Type': 'image/png'  # 或 'image/jpeg'，取決於圖片類型
            }
            response = requests.post(url, headers=headers, data=f.read())
            
            if response.status_code == 200:
                print(f"Rich Menu 圖片上傳成功")
                return True
            else:
                print(f"上傳 Rich Menu 圖片失敗: {response.status_code} {response.text}")
                return False
    except Exception as e:
        print(f"上傳圖片時發生錯誤: {e}")
        return False

def set_default_rich_menu(rich_menu_id):
    """設置為預設 Rich Menu"""
    try:
        headers = {
            'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
        }
        response = requests.post(
            f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"已設置為預設 Rich Menu")
            return True
        else:
            print(f"設置預設 Rich Menu 失敗: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"設置預設 Rich Menu 失敗: {e}")
        return False

if __name__ == "__main__":
    # 1. 創建 Rich Menu
    rich_menu_id = create_rich_menu()
    if not rich_menu_id:
        exit(1)
    
    # 2. 上傳圖片
    image_path = 'rich_menu.png'  # 替換為您的 Rich Menu 圖片路徑
    if not upload_rich_menu_image(rich_menu_id, image_path):
        print("圖片上傳失敗，但繼續設置預設選單")
    
    # 3. 設置為預設選單
    set_default_rich_menu(rich_menu_id) 