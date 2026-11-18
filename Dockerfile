FROM python:3.12-slim-trixie
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg nodejs && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt
COPY app.py .
CMD sh -c "pip install -q -U 'yt-dlp[default]' || true; exec gunicorn -b 0.0.0.0:${PORT:-8000} -w 1 --threads 4 --timeout 600 app:app"
