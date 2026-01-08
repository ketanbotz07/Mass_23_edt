# Step 1: Python ka official image use karein
FROM python:3.12-slim-bookworm

# Step 2: System dependencies install karein (FFmpeg + Compiler)
# Ye line video editing aur tgcrypto ke errors ko fix karegi
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Working directory set karein
WORKDIR /app

# Step 4: Sari files ko container mein copy karein
COPY . .

# Step 5: Python libraries install karein
# Isse requirements.txt wali sari libraries install ho jayengi
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Step 6: Leapcell ke liye Port expose karein
EXPOSE 8080

# Step 7: Bot ko start karne ki command
CMD ["python", "main.py"]
