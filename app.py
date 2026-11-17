import os, shutil, tempfile, glob, re
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])

# ঐচ্ছিক: cookies.txt (Render Secret File হলে /etc/secrets/cookies.txt)
def find_cookies():
    for p in (os.environ.get("COOKIES_FILE"), "/etc/secrets/cookies.txt", "cookies.txt"):
        if p and os.path.exists(p):
            # yt-dlp কুকি ফাইলে লেখার চেষ্টা করে, Secret File রিড-অনলি, তাই কপি করে নিচ্ছি
            dst = os.path.join(tempfile.gettempdir(), "yt_cookies.txt")
            shutil.copyfile(p, dst)
            return dst
    return None

COOKIES = find_cookies()

def attempts():
    """একের পর এক চেষ্টা: প্রথমে ইউটিউবের বট-চেক এড়ানো ক্লায়েন্ট, ব্যর্থ হলে ডিফল্ট।"""
    base = {"quiet": True, "no_warnings": True, "noplaylist": True,
            "retries": 3, "socket_timeout": 30}
    if COOKIES:
        base["cookiefile"] = COOKIES
    tuned = dict(base)
    if not COOKIES:
        tuned["extractor_args"] = {"youtube": {"player_client": ["android_vr", "tv", "mweb"]}}
    yield tuned
    yield dict(base)

def clean_url(u):
    u = (u or "").strip()
    return u if re.match(r"^https?://", u) else None

def friendly(e):
    m = str(e)
    if "Sign in to confirm" in m or "not a bot" in m:
        return "ইউটিউব এই সার্ভারকে আটকে দিয়েছে। কিছুক্ষণ পরে আবার চেষ্টা করুন।"
    if "Private video" in m or "private" in m.lower():
        return "ভিডিওটি প্রাইভেট, ডাউনলোড করা যাবে না।"
    if "Unsupported URL" in m:
        return "এই লিংক সাপোর্ট করে না।"
    return m[:200]

@app.get("/")
def health():
    return {"ok": True, "cookies": bool(COOKIES)}

@app.get("/api/info")
def info():
    url = clean_url(request.args.get("url"))
    if not url:
        return jsonify(error="সঠিক লিংক দিন"), 400
    d, err = None, None
    for opts in attempts():
        try:
            with yt_dlp.YoutubeDL(opts) as y:
                d = y.extract_info(url, download=False)
            break
        except Exception as e:
            err = e
    if d is None:
        return jsonify(error="ভিডিও পাওয়া যায়নি: " + friendly(err)), 422
    heights = sorted({f["height"] for f in d.get("formats", [])
                      if f.get("height") and f.get("vcodec") not in (None, "none")}, reverse=True)
    return jsonify(title=d.get("title"), thumbnail=d.get("thumbnail"),
                   duration=d.get("duration"), uploader=d.get("uploader"),
                   heights=heights)

@app.get("/api/download")
def download():
    url = clean_url(request.args.get("url"))
    kind = request.args.get("type", "video")
    if not url:
        return jsonify(error="সঠিক লিংক দিন"), 400
    try:
        h = int(request.args.get("height", 720))
    except ValueError:
        h = 720
    tmp = tempfile.mkdtemp()
    path, err = None, None
    for opts in attempts():
        opts["outtmpl"] = os.path.join(tmp, "%(title).80s.%(ext)s")
        if kind == "audio":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                       "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            opts["format"] = (f"bv*[height<={h}][vcodec^=avc1]+ba[ext=m4a]/"
                              f"bv*[height<={h}]+ba/b[height<={h}]/b")
            opts["merge_output_format"] = "mp4"
        try:
            with yt_dlp.YoutubeDL(opts) as y:
                y.download([url])
            files = glob.glob(os.path.join(tmp, "*"))
            if not files:
                raise RuntimeError("ফাইল তৈরি হয়নি")
            path = files[0]
            break
        except Exception as e:
            err = e
    if path is None:
        shutil.rmtree(tmp, ignore_errors=True)
        return jsonify(error="ডাউনলোড ব্যর্থ: " + friendly(err)), 422

    @after_this_request
    def cleanup(resp):
        shutil.rmtree(tmp, ignore_errors=True)
        return resp
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
