from flask import Flask, request, jsonify, render_template, send_file, Response, url_for
import yt_dlp
import os
import uuid
import imageio_ffmpeg as ffmpeg
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

#==============================
# Instagram route
#==============================
@app.route("/download/instagram", methods=["POST"])
def download_instagram():
    data = request.get_json()
    url = data.get("url")
    cookies = data.get("cookies")  # Optional: path to cookies.txt or None

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    # Default yt-dlp options
    opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(id)s.%(ext)s",
        "format": "mp4",
    }

    # Add cookies if provided
    if cookies:
        opts["cookies"] = cookies

    filename, error = download_with_yt_dlp(url, opts)
    if error:
        return jsonify({"success": False, "error": error})

    return jsonify({"success": True, "download_url": f"/file/{os.path.basename(filename)}"})

#==============================
# YouTube download route
#==============================
@app.route("/download/youtube", methods=["POST"])
def download_youtube():
    data = request.get_json()
    url = data.get("url")
    option = data.get("option")  # 'audio' or 'video'

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    unique_id = str(uuid.uuid4())

    opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/{unique_id}.%(ext)s",
        "ffmpeg_location": ffmpeg_path,
        "noplaylist": True,
        "quiet": True,
        "merge_output_format": "mp4",
    }

    if option == "audio":
        opts.update({
            "format": "bestaudio[ext=m4a]/bestaudio",
            "postprocessors": [
                {   # Extract audio as mp3
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {   # Normalize / boost audio after extraction
                    "key": "FFmpegMetadata",
                },
                {
                    "key": "FFmpegAudioFix",
                }
            ],
        })
        final_ext = "mp3"
    else:
        # Video (max 1080p) + audio merged
        opts.update({
            "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[height<=1080]",
            "postprocessors": [
                {   # Ensure metadata is written
                    "key": "FFmpegMetadata",
                },
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }
            ],
        })
        final_ext = "mp4"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.{final_ext}")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    if not os.path.exists(filename):
        return jsonify({"success": False, "error": "Download failed or file not found."})

    return jsonify({
        "success": True,
        "download_url": f"/file/{os.path.basename(filename)}"
    })

#==============================
# Facebook download route
#==============================
@app.route("/download/facebook", methods=["POST"])
def download_facebook():
    data = request.get_json()
    url = data.get("url")
    option = data.get("option")  # 'audio' or 'video'

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    unique_id = str(uuid.uuid4())

    opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/{unique_id}.%(ext)s",
        "ffmpeg_location": ffmpeg_path,
        "noplaylist": True,
        "quiet": True,
        "merge_output_format": "mp4",
    }

    if option == "audio":
        opts.update({
            "format": "bestaudio[ext=m4a]/bestaudio",
            "postprocessors": [
                {   # Extract audio as mp3
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {   # Add metadata
                    "key": "FFmpegMetadata",
                }
            ],
        })
        final_ext = "mp3"
    else:
        # Video (max 1080p) + audio merged
        opts.update({
            "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[height<=1080]",
            "postprocessors": [
                {   # Ensure metadata is written
                    "key": "FFmpegMetadata",
                },
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }
            ],
        })
        final_ext = "mp4"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.{final_ext}")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    if not os.path.exists(filename):
        return jsonify({"success": False, "error": "Download failed or file not found."})

    return jsonify({
        "success": True,
        "download_url": f"/file/{os.path.basename(filename)}"
    })

#==============================
# Serve downloaded files
#==============================
@app.route("/file/<filename>")
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

#==============================
# SiteMap route
#==============================

@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    """Generate sitemap.xml dynamically."""
    pages = [
        "/", 
        "/download/instagram", 
        "/download/youtube",
        "/download/facebook"
    ]
    
    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>',
                   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    
    for page in pages:
        full_url = request.url_root[:-1] + page  # Build full URL
        sitemap_xml.append("<url>")
        sitemap_xml.append(f"<loc>{full_url}</loc>")
        sitemap_xml.append(f"<changefreq>weekly</changefreq>")
        sitemap_xml.append(f"<priority>0.8</priority>")
        sitemap_xml.append("</url>")
    
    sitemap_xml.append("</urlset>")
    
    sitemap_str = "\n".join(sitemap_xml)
    
    return Response(sitemap_str, mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
