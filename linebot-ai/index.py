from flask import Flask, Response
import logging
import os

# Configure logging
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 Flask 應用
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    logger.info("Home route accessed")
    return Response('LINE Bot is running!', status=200)

# Vercel 需要這個處理函數
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 