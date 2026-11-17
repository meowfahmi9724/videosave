import os, shutil, tempfile, glob, re
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])
COOKIES = os.environ.get("COOKIES_FILE")  # ঐচ্ছিক: cookies.txt এর পাথ

def base_opts():
    o = {"quiet": True, "no_warnings": True, "noplaylist": True}
    if COOKIES and os.path.exists(COOKIES):
        o["cookiefile"] = COOKIES
    return o

def clean_url(u):
    u = (u or "").strip()
    return u if re.match(r"^https?://", u) else None

@app.get("/")
def health():
    return {"ok": True}

@app.get("/api/info")
def info():
    url = clean_url(request.args.get("url"))
    if not url:
        return jsonify(error="সঠিক লিংক দিন"), 400
    try:
        with yt_dlp.YoutubeDL(base_opts()) as y:
            d = y.extract_info(url, download=False)
    except Exception as e:
        return jsonify(error="ভিডিও পাওয়া যায়নি: " + str(e)[:200]), 422
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
    tmp = tempfile.mkdtemp()
    opts = base_opts()
    opts["outtmpl"] = os.path.join(tmp, "%(title).80s.%(ext)s")
    if kind == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                   "preferredcodec": "mp3", "preferredquality": "192"}]
    else:
        h = int(request.args.get("height", 720))
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
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        return jsonify(error="ডাউনলোড ব্যর্থ: " + str(e)[:200]), 422

    @after_this_request
    def cleanup(resp):
        shutil.rmtree(tmp, ignore_errors=True)
        return resp
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
