# hyperframes-runner: Node + Chromium + FFmpeg. Every snapshot, render and page capture runs in this image on the VM.
#   docker build -t hyperframes-runner -f tools/render/Dockerfile .
FROM node:22-bookworm
RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium ffmpeg fonts-liberation ca-certificates python3 \
 && rm -rf /var/lib/apt/lists/*
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    PUPPETEER_SKIP_DOWNLOAD=1 \
    CHROME_PATH=/usr/bin/chromium
RUN npm install -g hyperframes@0.8.223
WORKDIR /work
