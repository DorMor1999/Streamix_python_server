from flask import Blueprint, request, jsonify
from youtubesearchpython import VideosSearch
import logging

search_bp = Blueprint('search', __name__)
logger = logging.getLogger(__name__)


@search_bp.route('/', methods=['GET'])
def search_videos():
    query = request.args.get('query')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        search = VideosSearch(query, limit=10)
        search_results = search.result()

        if "result" not in search_results:
            return jsonify({"error": "Unexpected response from YouTube search API"}), 502

        results = []
        for v in search_results["result"]:
            try:
                results.append({
                    "title": v.get("title", "N/A"),
                    "duration": v.get("duration", "N/A"),
                    "views": v.get("viewCount", {}).get("short", "N/A"),
                    "channel": v.get("channel", {}).get("name", "N/A"),
                    "published": v.get("publishedTime", "N/A"),
                    "link": v.get("link", "N/A"),
                    "thumbnails": v.get("thumbnails", [])
                })
            except Exception as e:
                logger.warning(f"Skipping malformed result: {e}")

        return jsonify(results)

    except Exception as e:
        logger.error(f"Error during YouTube search: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500