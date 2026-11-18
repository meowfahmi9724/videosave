#!/data/data/com.termux/files/usr/bin/bash
# ঘরের সার্ভার চালু করার স্ক্রিপ্ট (Termux)
termux-wake-lock
cd ~
[ -f ~/.vd.conf ] && . ~/.vd.conf   # REG="https://....workers.dev"  KEY="গোপন-পাসওয়ার্ড"
pkill -f "python app.py" 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 1
nohup python app.py > server.log 2>&1 &
sleep 2
echo "✅ সার্ভার চালু।"
if command -v cloudflared >/dev/null 2>&1; then
  nohup cloudflared tunnel --url http://localhost:8000 > tunnel.log 2>&1 &
  U=""
  for i in $(seq 1 30); do
    U=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' tunnel.log 2>/dev/null | head -1)
    [ -n "$U" ] && break
    sleep 1
  done
  if [ -z "$U" ]; then
    echo "⚠️ টানেল লিংক পাওয়া যায়নি (tunnel.log দেখুন)"
  else
    echo "টানেল: $U"
    if [ -n "$REG" ] && [ -n "$KEY" ]; then
      R=$(curl -s -m 15 -X POST "$REG/url" -H "X-Key: $KEY" -H "Content-Type: application/json" -d "{\"url\":\"$U\"}")
      [ "$R" = "ok" ] && echo "✅ অ্যাপে নতুন লিংক পাঠানো হয়েছে" || echo "⚠️ লিংক পাঠানো যায়নি: $R"
    fi
  fi
fi
