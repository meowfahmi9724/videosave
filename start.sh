#!/data/data/com.termux/files/usr/bin/bash
# ঘরের সার্ভার চালু করার স্ক্রিপ্ট (Termux)
termux-wake-lock
cd ~
# আগের পুরনো সার্ভার/টানেল থাকলে বন্ধ করে নতুন করে চালু
pkill -f "python app.py" 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 1
python app.py > server.log 2>&1 &
sleep 3
echo "-----------------------------------------"
echo "নিচে trycloudflare.com লিংকটা কপি করুন"
echo "-----------------------------------------"
cloudflared tunnel --url http://localhost:8000
