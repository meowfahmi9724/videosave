#!/data/data/com.termux/files/usr/bin/bash
# ঘরের সার্ভার চালু করার স্ক্রিপ্ট (Termux)
termux-wake-lock
cd ~
pkill -f "python app.py" 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 1
nohup python app.py > server.log 2>&1 &
sleep 2
echo "✅ সার্ভার চালু। এই ফোনের অ্যাপ এখনই এটা ব্যবহার করবে (টানেল লাগবে না)।"
# ঐচ্ছিক: অন্য ডিভাইসের জন্য টানেল (ব্যাকগ্রাউন্ডে)
if command -v cloudflared >/dev/null 2>&1; then
  nohup cloudflared tunnel --url http://localhost:8000 > tunnel.log 2>&1 &
  for i in $(seq 1 20); do
    U=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' tunnel.log 2>/dev/null | head -1)
    [ -n "$U" ] && break
    sleep 1
  done
  [ -n "$U" ] && echo "টানেল লিংক (অন্য ডিভাইসের জন্য): $U"
fi
