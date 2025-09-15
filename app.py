from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

def download_with_yt_dlp(url, opts):
    """Helper function to download using yt_dlp and return filename or error"""
    try:
        # Ensure unique filename
        unique_id = str(uuid.uuid4())
        if "outtmpl" not in opts or "%(id)s" in opts["outtmpl"]:
            opts["outtmpl"] = f"{DOWNLOAD_FOLDER}/{unique_id}.%(ext)s"

        # Use ffmpeg-python compatible postprocessor
        if "ffmpeg_location" not in opts:
            opts["ffmpeg_location"] = "/usr/bin/ffmpeg"  # Render Linux path

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get actual downloaded filename
            filename = ydl.prepare_filename(info)
        return filename, None
    except Exception as e:
        return None, str(e)

# Instagram route
@app.route("/download/instagram", methods=["POST"])
def download_instagram():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(id)s.%(ext)s",
        "format": "mp4",
    }
    filename, error = download_with_yt_dlp(url, opts)
    if error:
        return jsonify({"success": False, "error": error})
    return jsonify({"success": True, "download_url": f"/file/{os.path.basename(filename)}"})

# YouTube download route
@app.route("/download/youtube", methods=["POST"])
def download_youtube():
    data = request.get_json()
    url = data.get("url")
    option = data.get("option")  # 'audio' or 'video'

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    # Default yt-dlp options
    opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(id)s.%(ext)s",
        "ffmpeg_location": "/usr/bin/ffmpeg",  # Required for Render free plan
        "noplaylist": True,  # Only single video/short
    }

    if option == "audio":
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:  # Audio + Video
        opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        })

    filename, error = download_with_yt_dlp(url, opts)
    if error:
        return jsonify({"success": False, "error": error})

    return jsonify({"success": True, "download_url": f"/file/{os.path.basename(filename)}"})

# Facebook route
@app.route("/download/facebook", methods=["POST"])
def download_facebook():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    # Video + audio merging
    opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(id)s.%(ext)s",
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
    }
    filename, error = download_with_yt_dlp(url, opts)
    if error:
        return jsonify({"success": False, "error": error})
    return jsonify({"success": True, "download_url": f"/file/{os.path.basename(filename)}"})

# Serve downloaded files
@app.route("/file/<filename>")
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
