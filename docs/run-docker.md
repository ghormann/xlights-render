# Running xLights Render Locally via Docker

Use this to test the image on your local machine before deploying to k8s.

## Prerequisites

- Docker installed and running
- A `greglights_config.json` file with your MQTT credentials
- A VNC client (e.g., RealVNC Viewer, TigerVNC, macOS built-in Screen Sharing)

## Build the Image

Use the default xLights version (2025.13):

```bash
docker build -t xlights-render:2025.13 .
```

To build with a different xLights version:

```bash
docker build \
  --build-arg XLIGHTS_APPIMAGE_URL=https://github.com/xLightsSequencer/xLights/releases/download/2025.14/xLights-2025.14-x86_64.AppImage \
  -t xlights-render:2025.14 .
```

## Run the Container

```bash
docker run -d \
  --name xlights-render \
  -p 5900:5900 \
  -v /path/to/greglights_config.json:/app/greglights_config.json:ro \
  xlights-render:2025.13
```

Replace `/path/to/greglights_config.json` with the absolute path to your config file.

## Connect via VNC

Open your VNC client and connect to:

```
localhost:5900
```

No password is required. You will see the virtual desktop where xLights renders sequences. When the Python app triggers a render, the xLights GUI will appear here.

## View Logs

```bash
docker logs -f xlights-render
```

## Stop and Remove

```bash
docker stop xlights-render && docker rm xlights-render
```
