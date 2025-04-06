"""
設置 LINE Bot 的 Rich Menu（圖文選單）
這個腳本創建並設置一個基本的 Rich Menu，用於快速訪問常用功能
"""
import os
import logging
import json
import requests
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, URIAction, MessageAction, PostbackAction

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置 LINE API
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
LIFF_ID = os.environ.get('LIFF_ID', '')

# LINE API 客戶端
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def create_rich_menu():
    """創建並註冊圖文選單"""
    # 定義圖文選單 (1200x810 像素)
    rich_menu = RichMenu(
        size_full=True,  # 全螢幕選單
        selected=True,   # 預設顯示
        name='主選單',    # 選單名稱
        chat_bar_text='展開選單',  # 底部文字
        areas=[  # 可點擊區域設置
            # 左上 - 記帳功能
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=400, height=405),
                action=PostbackAction(label='記帳', display_text='記帳', data='action=record&type=expense')
            ),
            # 中上 - 記錄查詢
            RichMenuArea(
                bounds=RichMenuBounds(x=400, y=0, width=400, height=405),
                action=MessageAction(label='查詢記錄', text='記錄')
            ),
            # 右上 - 主選單(Flex)
            RichMenuArea(
                bounds=RichMenuBounds(x=800, y=0, width=400, height=405),
                action=MessageAction(label='主選單', text='kimi')
            ),
            # 左下 - 任務管理
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=405, width=400, height=405),
                action=PostbackAction(label='任務管理', display_text='任務管理', data='action=task_menu')
            ),
            # 中下 - 月度報表 
            RichMenuArea(
                bounds=RichMenuBounds(x=400, y=405, width=400, height=405),
                action=MessageAction(label='月度報表', text='月報')
            ),
            # 右下 - 幫助
            RichMenuArea(
                bounds=RichMenuBounds(x=800, y=405, width=400, height=405),
                action=MessageAction(label='幫助', text='help')
            ),
        ]
    )

    # 建立選單
    try:
        rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu)
        logger.info(f"圖文選單已創建，ID: {rich_menu_id}")
        
        # 上傳圖片
        with open('richmenu_image.png', 'rb') as f:
            line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)
        logger.info("圖文選單圖片已上傳")
        
        # 設置為默認選單
        line_bot_api.set_default_rich_menu(rich_menu_id)
        logger.info("圖文選單已設置為默認選單")
        
        return rich_menu_id
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
    if not LINE_CHANNEL_ACCESS_TOKEN:
        logger.error("LINE_CHANNEL_ACCESS_TOKEN 未設置")
        return False
    
    # 檢查是否有現有的 Rich Menu
    try:
        rich_menu_list = line_bot_api.get_rich_menu_list()
        if rich_menu_list:
            logger.info(f"發現 {len(rich_menu_list)} 個現有的圖文選單")
            for menu in rich_menu_list:
                logger.info(f"刪除圖文選單: {menu.rich_menu_id}")
                line_bot_api.delete_rich_menu(menu.rich_menu_id)
            logger.info("已清除所有現有圖文選單")
    except Exception as e:
        logger.error(f"檢查或刪除圖文選單時發生錯誤: {str(e)}")
    
    # 創建示例圖片
    if not os.path.exists('richmenu_image.png'):
        if not create_sample_richmenu_image():
            logger.error("無法創建示例圖片，請提供一個 1200x810 像素的 PNG 圖片")
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