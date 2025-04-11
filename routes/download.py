from flask import Blueprint, request, jsonify, send_file
from pytubefix import YouTube
import io
import zipfile
import json
import re
import requests


download_bp = Blueprint('download', __name__)


def is_valid_youtube_url(url):
    # Basic regex to validate YouTube URL
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.*(v=|e/(.*)/)?([^"&?/\s]{11})'
    return re.match(youtube_regex, url) is not None

def set_proxies(proxy_data):
    proxies = {}
    if proxy_data:
        http_proxy = proxy_data.get('http', '')
        https_proxy = proxy_data.get('https', '')
        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
    return proxies

@download_bp.route('/', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    format = data.get('format', 'video')
    proxies_data = data.get('proxies', {})

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        # Set proxies globally for all requests
        proxies = set_proxies(proxies_data)
        if proxies:
            requests.Session().proxies.update(proxies)

        yt = YouTube(url)
        streams = yt.streams.all()

        if format == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            stream = yt.streams.get_highest_resolution()

        if not stream:
            return jsonify({"error": "No streams found for the requested format"}), 400

        file_buffer = io.BytesIO()
        stream.stream_to_buffer(file_buffer)
        file_buffer.seek(0)

        metadata = {
            "title": yt.title,
            "author": yt.author,
            "views": yt.views,
            "length": yt.length,
            "publish_date": str(yt.publish_date),
            "description": yt.description,
            "mime_type": stream.mime_type,
            "filesize": stream.filesize,
            "filename": f"{yt.title}.{stream.subtype}"
        }

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(f"{yt.title}.{stream.subtype}", file_buffer.read())
            zipf.writestr("info.json", json.dumps(metadata, indent=4))

        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name=f"{yt.title}.zip", mimetype='application/zip')

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500