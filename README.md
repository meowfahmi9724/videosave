# ভিডিও সেভার

## ১. ব্যাকএন্ড (ফ্রি, Render)
1. এই ফোল্ডার GitHub রিপোতে আপলোড করুন।
2. render.com এ লগইন → New → Blueprint → রিপো সিলেক্ট করুন (`render.yaml` নিজে থেকে কাজ করবে; সব ফাইল একই জায়গায়)।
3. ডিপ্লয় শেষে পাওয়া লিংক (যেমন `https://videosave-api.onrender.com`) কপি করুন।

## ২. ফ্রন্টএন্ড (ফ্রি, GitHub Pages)
1. `config.js` এ `window.API_URL` এর ভেতর ওই লিংক বসান (শেষে `/` দেবেন না)।
2. রিপো Settings → Pages → Branch: main, root → Save।

## নোট
- Render ফ্রি সার্ভার ১৫ মিনিট অব্যবহৃত থাকলে ঘুমায়, প্রথম রিকোয়েস্টে ~১ মিনিট লাগে।
- ইউটিউব ডেটাসেন্টার আইপি ব্লক করলে ("Sign in to confirm you're not a bot"): আলাদা একটা গুগল অ্যাকাউন্টে ইউটিউবে লগইন করে "Get cookies.txt LOCALLY" এক্সটেনশন দিয়ে `cookies.txt` এক্সপোর্ট করুন। Render → আপনার সার্ভিস → Environment → Secret Files → Add → নাম `cookies.txt`, ভেতরে ফাইলের লেখা পেস্ট → Save। সার্ভার নিজে `/etc/secrets/cookies.txt` পড়ে নেবে। কুকি পুরোনো হলে আবার দিন।
- সার্ভারের লিংক খুললে `{"ok":true,"cookies":true}` এলে কুকি লোড হয়েছে।
- মাঝে মাঝে ডিপ্লয় রিবিল্ড করুন, যাতে yt-dlp আপডেট হয়।

## ঘরের সার্ভার (ঐচ্ছিক, ইউটিউবের জন্য)
Render-এর আইপি ইউটিউব ব্লক করলে ঘরের ওয়াইফাইয়ে থাকা পিসি/ফোনে `app.py` চালিয়ে ক্লাউডফ্লেয়ার টানেল খুলুন, তারপর `config.js` এ যোগ করুন:
```
window.API_URL_HOME = "https://আপনার-টানেল-লিংক";
```
- ইউটিউব লিংকে সাইট আগে ঘরের সার্ভারে চেষ্টা করে (১২ সেকেন্ডে সাড়া না পেলে Render-এ যায়)। অন্য সাইটের লিংক সরাসরি Render-এ যায়।
- ঘরের সার্ভার বন্ধ থাকলে সাইট নিজে নিজে Render ব্যবহার করে, কিছু করতে হয় না।
- Termux: `pkg install python ffmpeg cloudflared && pip install flask flask-cors yt-dlp`, তারপর `python app.py` ও আলাদা সেশনে `cloudflared tunnel --url http://localhost:8000`। টেম্পরারি টানেলের লিংক প্রতিবার বদলায়, তাই `config.js` আপডেট করতে হবে।
