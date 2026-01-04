FROM python:3.9-slim

# FFmpeg install karna zaroori hai
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
