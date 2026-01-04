# 1. Python ka lightweight version use kar rahe hain
FROM python:3.10-slim

# 2. System updates aur FFMPEG install karna (MoviePy ke liye zaroori hai)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Working directory set karein
WORKDIR /app

# 4. Requirements file copy karein aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Baaki saara code copy karein
COPY . .

# 6. Flask server (Koyeb Health Check) ke liye port open karein
EXPOSE 8080

# 7. Bot start karne ki command
CMD ["python", "main.py"]
