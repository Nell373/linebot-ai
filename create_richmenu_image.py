#!/usr/bin/env python3
"""
創建一個簡單的 LINE 圖文選單圖片
使用 Pillow 庫創建一個 1200x810 像素的菜單圖片
"""
from PIL import Image, ImageDraw, ImageFont
import os

# 定義圖片尺寸和顏色
WIDTH = 1200
HEIGHT = 810
BACKGROUND_COLOR = (245, 245, 245)  # 淺灰色背景
BORDER_COLOR = (200, 200, 200)      # 邊框顏色
TEXT_COLOR = (50, 50, 50)           # 文字顏色
BUTTON_COLOR = (255, 255, 226)      # 按鈕顏色
BUTTON_BORDER = (220, 220, 220)     # 按鈕邊框

# 創建一個新圖片
image = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
draw = ImageDraw.Draw(image)

# 嘗試加載字體，如果失敗就使用默認字體
try:
    # 嘗試使用系統字體
    font_path = '/System/Library/Fonts/STHeiti Light.ttc'  # macOS 常見中文字體
    if not os.path.exists(font_path):
        font_path = '/System/Library/Fonts/Arial.ttf'
    
    title_font = ImageFont.truetype(font_path, 40)
    button_font = ImageFont.truetype(font_path, 30)
except Exception:
    # 使用默認字體
    title_font = ImageFont.load_default()
    button_font = ImageFont.load_default()

# 畫出主標題
draw.text((WIDTH // 2, 50), "Kimi 助手選單", fill=TEXT_COLOR, font=title_font, anchor="mt")

# 定義按鈕區域和文字
buttons = [
    # 左上角
    {"text": "記帳", "x": 200, "y": 200},
    # 中上
    {"text": "記錄查詢", "x": 600, "y": 200},
    # 右上
    {"text": "主選單", "x": 1000, "y": 200},
    # 左下
    {"text": "任務管理", "x": 200, "y": 600},
    # 中下
    {"text": "月度報表", "x": 600, "y": 600},
    # 右下
    {"text": "幫助", "x": 1000, "y": 600}
]

# 畫出網格線分隔區域
# 垂直線
draw.line([(400, 0), (400, HEIGHT)], fill=BORDER_COLOR, width=2)
draw.line([(800, 0), (800, HEIGHT)], fill=BORDER_COLOR, width=2)
# 水平線
draw.line([(0, 405), (WIDTH, 405)], fill=BORDER_COLOR, width=2)

# 繪製按鈕
for button in buttons:
    # 計算按鈕中心位置
    x, y = button["x"], button["y"]
    
    # 畫一個圓形按鈕
    button_radius = 80
    draw.ellipse((x - button_radius, y - button_radius, x + button_radius, y + button_radius), 
                fill=BUTTON_COLOR, outline=BUTTON_BORDER, width=2)
    
    # 添加按鈕文字
    draw.text((x, y), button["text"], fill=TEXT_COLOR, font=button_font, anchor="mm")

# 保存圖片
image.save('richmenu_image.png')
print("圖文選單圖片已創建：richmenu_image.png") 