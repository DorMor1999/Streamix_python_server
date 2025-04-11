
# YouTube Downloader and Search API

This project is a Flask web application that provides two main features:
- **Search** for YouTube videos based on a query.
- **Download** YouTube videos or audio as `.mp4` or `.mp3` files and package them into a `.zip` file along with metadata.

## Features
- **Search Videos**: Given a search query, you can retrieve the top 5 video results from YouTube.
- **Download Videos**: Download videos or audio in different formats and package them with metadata into a zip file.
- Secret key authentication ("API-KEY") for secure access to the API.

## Installation

## 🛠️ Setup & Installation

```bash
git clone https://github.com/DorMor1999/face_recognition_service
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Running the Application

```bash
python app.py
```

The application will be accessible at `http://localhost:5000`.

## Endpoints

### 1. `/search`
- **Method**: POST
- **Request Body**:
    ```json
    {
        "query": "search term"
    }
    ```
- **Response**:
    ```json
    [
        {
            "title": "Video Title",
            "url": "https://www.youtube.com/watch?v=xxx",
            "description": "Video description"
        },
        ...
    ]
    ```
- **Description**: This endpoint allows you to search for YouTube videos by providing a query. It will return the top 5 search results with their titles, URLs, and descriptions.

### 2. `/download`
- **Method**: POST
- **Request Body**:
    ```json
    {
        "url": "https://www.youtube.com/watch?v=xxx",
        "format": "video"  # or "audio"
    }
    ```
- **Response**: A `.zip` file containing the requested video/audio and metadata.
- **Description**: This endpoint allows you to download a YouTube video or audio file. You can specify whether you want the video or audio by setting the `"format"` parameter. It will return a `.zip` file containing the video/audio and metadata.

### Example cURL Request:
To **search** for videos:
```bash
curl -X POST http://localhost:5000/search -H "Content-Type: application/json" -d '{"query": "Flask tutorial"}'
```

To **download** a video:
```bash
curl -X POST http://localhost:5000/download -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=xxx", "format": "video"}'
```
