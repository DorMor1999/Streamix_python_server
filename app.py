from flask import Flask, request, jsonify
from routes.search import search_bp
from routes.download import download_bp
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
API_KEY = os.getenv("API_KEY")

@app.before_request
def check_api_key():
    key = request.headers.get('API-KEY')
    if not key or key != API_KEY:
        return jsonify({"error": "Unauthorized. Missing or invalid 'API_KEY'."}), 401

@app.route('/')
def home():
    return "Hello from Flask Streamix-python-server"

# Register Blueprints
app.register_blueprint(search_bp, url_prefix="/search")
app.register_blueprint(download_bp, url_prefix="/download")



if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)