from flask import Blueprint, request, jsonify, send_file
from pytubefix import YouTube
import io
import zipfile
import json
import re

download_bp = Blueprint('download', __name__)

def is_valid_youtube_url(url):
    # Basic regex to validate YouTube URL
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.*(v=|e/(.*)/)?([^"&?/\s]{11})'
    return re.match(youtube_regex, url) is not None

@download_bp.route('/', methods=['POST'])
def download_video():
    data = request.get_json()
    print(f"Received data: {data}")  # Debugging line
    url = data.get('url')
    format = data.get('format', 'video')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Validate the URL format
    if not is_valid_youtube_url(url):
        print(f"Invalid URL: {url}")  # Debugging line
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        yt = YouTube(url)
        print(f"Video title: {yt.title}")  # Debugging line

        # Debugging: print available streams
        streams = yt.streams.all()
        print(f"Available streams: {streams}")

        # Select the appropriate stream based on the requested format
        if format == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
            print(f"Selected audio stream: {stream}")
        else:
            stream = yt.streams.get_highest_resolution()
            print(f"Selected video stream: {stream}")

        # If no stream is found, return an error
        if not stream:
            return jsonify({"error": "No streams found for the requested format"}), 400

        # Create a memory buffer to store the file
        file_buffer = io.BytesIO()

        # Download the selected stream directly into the buffer
        stream.stream_to_buffer(file_buffer)
        file_buffer.seek(0)  # Reset the buffer pointer to the beginning

        # Prepare metadata for the download
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

        # Create a zip file containing the video/audio and metadata in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Write the file to the zip
            zipf.writestr(f"{yt.title}.{stream.subtype}", file_buffer.read())
            # Write the metadata JSON
            zipf.writestr("info.json", json.dumps(metadata, indent=4))

        zip_buffer.seek(0)  # Reset the buffer pointer to the beginning

        # Send the zip file directly as the response
        return send_file(zip_buffer, as_attachment=True, download_name=f"{yt.title}.zip", mimetype='application/zip')

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging line
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500