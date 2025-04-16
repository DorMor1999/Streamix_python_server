from flask import Blueprint, request, jsonify, send_file
from pytubefix import YouTube
import io
import re

download_bp = Blueprint('download', __name__)

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.*(v=|e/(.*)/)?([^"&?/\s]{11})'
    return re.match(youtube_regex, url) is not None

@download_bp.route('/', methods=['POST'])
def download_video():
    data = request.get_json()
    print(f"Received data: {data}")
    url = data.get('url')
    format = data.get('format', 'video')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if not is_valid_youtube_url(url):
        print(f"Invalid URL: {url}")
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        yt = YouTube(url)
        print(f"Video title: {yt.title}")

        if format == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
            suffix = "_audio"
            print(f"Selected audio stream: {stream}")
        else:
            stream = yt.streams.get_highest_resolution()
            suffix = "_video"
            print(f"Selected video stream: {stream}")

        if not stream:
            return jsonify({"error": "No streams found for the requested format"}), 400

        file_buffer = io.BytesIO()
        stream.stream_to_buffer(file_buffer)
        file_buffer.seek(0)

        ext = stream.subtype or stream.mime_type.split('/')[-1]
        base_title = yt.title.replace('/', '_').replace('\\', '_')  # sanitize filename
        filename = f"{base_title}{suffix}.{ext}"
        mimetype = stream.mime_type

        return send_file(
            file_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
