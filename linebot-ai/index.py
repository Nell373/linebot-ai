from flask import Flask, Response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return Response('LINE Bot is running!', status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080) 