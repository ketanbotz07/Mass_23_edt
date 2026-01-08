FROM python:3.12-slim-bookworm

# Build tools aur FFmpeg install karein (Tgcrypto aur editing ke liye zaroori hai)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Leapcell Start Command
CMD ["python", "main.py"]
