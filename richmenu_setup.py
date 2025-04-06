"""
設置 LINE Bot 的 Rich Menu（圖文選單）
這個腳本創建並設置一個基本的 Rich Menu，用於快速訪問常用功能
"""
import os
import logging
import json
import requests
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, URIAction, MessageAction, PostbackAction, RichMenuSize

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置 LINE API (直接硬編碼以確保正確性)
LINE_CHANNEL_ACCESS_TOKEN = "dcHUu60hxSgZGL1cEM/FxzuoSkwrO6lbUVR/yjiysMm8CMahMjWMl7vRsEjvcabnl53oPoAqy/meJTyjwQ2Ie7MXv6sqlbwewb9k9154UF7g89S+4sbqkwjaKLV9RNQ6L6MBcmdACE/WlPCLG+LkhwdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "1d260f0f95e6bc35878578a46ab05558"
LIFF_ID = "2007212914-e3vNnYno"

# LINE API 客戶端
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def create_rich_menu():
    """創建並註冊圖文選單"""
    # 定義圖文選單 (1200x810 像素)
    rich_menu = {
        "size": {
            "width": 1200,
            "height": 810
        },
        "selected": True,
        "name": "主選單",
        "chatBarText": "展開選單",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 400,
                    "height": 405
                },
                "action": {
                    "type": "postback",
                    "label": "記帳",
                    "data": "action=record&type=expense",
                    "displayText": "記帳"
                }
            },
            {
                "bounds": {
                    "x": 400,
                    "y": 0,
                    "width": 400,
                    "height": 405
                },
                "action": {
                    "type": "message",
                    "label": "查詢記錄",
                    "text": "記錄"
                }
            },
            {
                "bounds": {
                    "x": 800,
                    "y": 0,
                    "width": 400,
                    "height": 405
                },
                "action": {
                    "type": "message",
                    "label": "主選單",
                    "text": "kimi"
                }
            },
            {
                "bounds": {
                    "x": 0,
                    "y": 405,
                    "width": 400,
                    "height": 405
                },
                "action": {
                    "type": "postback",
                    "label": "任務管理",
                    "data": "action=task_menu",
                    "displayText": "任務管理"
                }
            },
            {
                "bounds": {
                    "x": 400,
                    "y": 405,
                    "width": 400,
                    "height": 405
                },
                "action": {
                    "type": "message",
                    "label": "月度報表",
                    "text": "月報"
                }
            },
            {
                "bounds": {
                    "x": 800,
                    "y": 405,
                    "width": 400,
                    "height": 405
                },
                "action": {
                    "type": "message",
                    "label": "幫助",
                    "text": "help"
                }
            }
        ]
    }

    # 建立選單
    try:
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # 使用 requests 直接向 LINE API 發起請求
        response = requests.post(
            'https://api.line.me/v2/bot/richmenu',
            headers=headers,
            json=rich_menu
        )
        
        # 檢查響應
        if response.status_code == 200:
            rich_menu_id = response.json()['richMenuId']
            logger.info(f"圖文選單已創建，ID: {rich_menu_id}")
            
            # 上傳圖片
            with open('richmenu_image.png', 'rb') as f:
                image_response = requests.post(
                    f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content',
                    headers={
                        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
                        'Content-Type': 'image/png'
                    },
                    data=f.read()
                )
            
            if image_response.status_code == 200:
                logger.info("圖文選單圖片已上傳")
            else:
                logger.error(f"上傳圖片失敗: {image_response.status_code} {image_response.text}")
                return None
            
            # 設置為默認選單
            default_response = requests.post(
                f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}',
                headers={
                    'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
                }
            )
            
            if default_response.status_code == 200:
                logger.info("圖文選單已設置為默認選單")
                return rich_menu_id
            else:
                logger.error(f"設置默認選單失敗: {default_response.status_code} {default_response.text}")
                return None
        else:
            logger.error(f"創建圖文選單失敗: {response.status_code} {response.text}")
            return None
    except Exception as e:
        logger.error(f"創建圖文選單時發生錯誤: {str(e)}")
        return None

def create_sample_richmenu_image():
    """創建一個簡單的選單圖片"""
    try:
        # 使用 requests 下載現成的圖片作為示範
        sample_url = "https://github.com/line/line-bot-sdk-python/raw/master/examples/rich-menu/richmenu-template-guide-01.png"
        response = requests.get(sample_url)
        if response.status_code == 200:
            with open('richmenu_image.png', 'wb') as f:
                f.write(response.content)
            logger.info("示例圖文選單圖片已下載")
            return True
        else:
            logger.error(f"下載示例圖片失敗，狀態碼: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"創建示例圖片時發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    # 檢查是否有現有的 Rich Menu
    try:
        response = requests.get(
            'https://api.line.me/v2/bot/richmenu/list',
            headers={
                'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
            }
        )
        
        if response.status_code == 200:
            rich_menu_list = response.json().get('richmenus', [])
            if rich_menu_list:
                logger.info(f"發現 {len(rich_menu_list)} 個現有的圖文選單")
                for menu in rich_menu_list:
                    menu_id = menu.get('richMenuId')
                    logger.info(f"刪除圖文選單: {menu_id}")
                    delete_response = requests.delete(
                        f'https://api.line.me/v2/bot/richmenu/{menu_id}',
                        headers={
                            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
                        }
                    )
                    if delete_response.status_code == 200:
                        logger.info(f"已刪除圖文選單: {menu_id}")
                    else:
                        logger.error(f"刪除圖文選單失敗: {delete_response.status_code} {delete_response.text}")
                logger.info("已清除所有現有圖文選單")
    except Exception as e:
        logger.error(f"檢查或刪除圖文選單時發生錯誤: {str(e)}")
    
    # 檢查圖片是否存在
    if not os.path.exists('richmenu_image.png'):
        logger.error("找不到 richmenu_image.png，請先執行 create_richmenu_image.py 創建圖片")
        return False
    
    # 創建圖文選單
    rich_menu_id = create_rich_menu()
    if rich_menu_id:
        logger.info("圖文選單設置成功!")
        return True
    else:
        logger.error("圖文選單設置失敗")
        return False

if __name__ == "__main__":
    main() 