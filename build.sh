#!/usr/bin/env bash
set -e

echo "==> Downloading static FFmpeg binary..."
mkdir -p bin
curl -sL "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz" -o /tmp/ffmpeg.tar.xz
tar -xf /tmp/ffmpeg.tar.xz -C /tmp --strip-components=1 --wildcards '*/ffmpeg' '*/ffprobe'
mv /tmp/ffmpeg /tmp/ffprobe bin/
chmod +x bin/ffmpeg bin/ffprobe
echo "==> FFmpeg ready: $(bin/ffmpeg -version 2>&1 | head -1)"

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Build complete."
