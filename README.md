
# DownOwl - Video Downloader Web App

This is a Flask-based web application that allows users to download videos or audio from **YouTube, Facebook, and Instagram**.
It uses **yt-dlp** and **FFmpeg** under the hood to fetch, merge, and process the media.

---

## 🚀 Features

* Download **YouTube videos** in up to **1080p MP4** format.
* Extract **YouTube audio** as **MP3 (192 kbps)**.
* Download **Facebook videos** in HD or extract **MP3 audio**.
* Download **Instagram reels/videos**.
* Unique filenames for each download (UUID-based).
* Integrated with **FFmpeg** for high-quality processing.
* JSON API responses with direct download links.

---

## 📂 Project Structure

```
video-downloader/
│── app.py                  # Main Flask application
│── templates/
│   └── index.html           # Frontend UI
│── downloads/               # All downloaded media stored here
│── requirements.txt         # Python dependencies
│── README.md                # Project documentation
```

---

## 🛠️ Requirements

* Python **3.8+**
* `yt-dlp` (for downloading)
* `Flask` (for web framework)
* `imageio-ffmpeg` (for ffmpeg binary support)
* `gunicorn` (for deployment on Render/Heroku etc.)

---

## 📦 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/video-downloader.git
   cd video-downloader
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / Mac
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:

   ```bash
   python app.py
   ```

5. Visit the app in your browser:

   ```
   http://127.0.0.1:5000
   ```

---

## ⚙️ API Endpoints

### 1. **YouTube Download**

`POST /download/youtube`

**Request JSON**

```json
{
  "url": "https://youtube.com/watch?v=example",
  "option": "video"   // or "audio"
}
```

**Response JSON**

```json
{
  "success": true,
  "download_url": "/file/abcd1234.mp4"
}
```

---

### 2. **Facebook Download**

`POST /download/facebook`

**Request JSON**

```json
{
  "url": "https://facebook.com/watch?v=example",
  "option": "audio"   // or "video"
}
```

**Response JSON**

```json
{
  "success": true,
  "download_url": "/file/xyz987.mp3"
}
```

---

### 3. **Instagram Download**

`POST /download/instagram`

**Request JSON**

```json
{
  "url": "https://instagram.com/reel/example"
}
```

**Response JSON**

```json
{
  "success": true,
  "download_url": "/file/insta123.mp4"
}
```

---

### 4. **Serve Downloaded File**

`GET /file/<filename>`

Downloads the requested file from the `/downloads/` folder.

---

## 🚀 Deployment

For production (e.g., Render, Heroku, Railway):

1. Add **gunicorn** to `requirements.txt`.
2. Create a `Procfile`:

   ```
   web: gunicorn app:app
   ```
3. Deploy via your platform’s GitHub integration or CLI.

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.
Downloading copyrighted content without permission may violate platform terms and laws.
Use responsibly.


