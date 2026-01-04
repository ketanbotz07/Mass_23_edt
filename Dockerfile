# Python ka official image use karein
FROM python:3.10-slim

# System updates aur FFmpeg install karein (MoviePy ke liye zaroori hai)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# App directory banayein
WORKDIR /app

# Requirements copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saara code copy karein
COPY . .

# Bot ko start karne ki command
CMD ["python", "main.py"]
