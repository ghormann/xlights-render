FROM ubuntu:22.04

ARG XLIGHTS_APPIMAGE_URL=https://github.com/xLightsSequencer/xLights/releases/download/2025.13/xLights-2025.13-x86_64.AppImage

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    libgl1 \
    libglu1-mesa \
    libglib2.0-0 \
    libfontconfig1 \
    libdbus-1-3 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpulse0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libatk1.0-0 \
    libgbm1 \
    libegl1 \
    python3 \
    python3-pip \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download and extract xLights AppImage (--appimage-extract avoids needing FUSE at runtime)
RUN wget -q -O /tmp/xLights.AppImage "${XLIGHTS_APPIMAGE_URL}" \
    && chmod +x /tmp/xLights.AppImage \
    && cd /tmp && /tmp/xLights.AppImage --appimage-extract \
    && mv /tmp/squashfs-root /opt/xlights \
    && rm /tmp/xLights.AppImage \
    && printf '#!/bin/bash\nexec /opt/xlights/AppRun "$@"\n' > /usr/local/bin/xLights \
    && chmod +x /usr/local/bin/xLights

# Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Application files
COPY entrypoint.sh /entrypoint.sh
COPY main.py generate_names.py /app/
COPY *.xsq *.xml /app/
COPY Shaders/ /app/Shaders/

WORKDIR /app
ENV DISPLAY=:99

ENTRYPOINT ["/entrypoint.sh"]
