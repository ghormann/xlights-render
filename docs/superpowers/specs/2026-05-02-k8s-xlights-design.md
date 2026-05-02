# xLights Render: Kubernetes Deployment Design

**Date:** 2026-05-02  
**Status:** Approved

## Overview

Run the xLights render service as a long-running pod on a home k8s cluster. The service listens to MQTT, generates xLights sequences from templates, renders them to `.fseq` files using the xLights GUI application, and uploads them to FPP instances on the local network. A virtual framebuffer (Xvfb) satisfies xLights' display requirement; x11vnc exposes that display for live debugging via VNC.

## Container Image

### Base Image

Ubuntu 22.04. Provides stable AppImage support and all required system packages.

### xLights AppImage

xLights is installed from an AppImage, parameterized via a Docker build argument with a default of version 2025.13:

```dockerfile
ARG XLIGHTS_APPIMAGE_URL=https://github.com/xLightsSequencer/xLights/releases/download/2025.13/xLights-2025.13-x86_64.AppImage
```

Override at build time to target a different release:

```bash
docker build \
  --build-arg XLIGHTS_APPIMAGE_URL=https://github.com/xLightsSequencer/xLights/releases/download/2025.14/xLights-2025.14-x86_64.AppImage \
  -t xlights-render:2025.14 .
```

**AppImage extraction:** AppImages normally require FUSE, which is unavailable in containers. The Dockerfile extracts the AppImage at build time using `--appimage-extract`, producing a `squashfs-root/` directory. `squashfs-root/AppRun` is symlinked to `/usr/local/bin/xLights`. This means the existing `subprocess.run(["xLights", "-r", name])` calls in `generate_names.py` work with no code changes.

### System Packages

- `xvfb` — virtual framebuffer X server
- `x11vnc` — VNC server over X11 for live debugging
- Mesa OpenGL libraries — xLights requires GL for rendering
- xLights runtime shared library dependencies
- Python 3, pip
- curl (used by `generate_names.py` to upload `.fseq` to FPP)

### Virtual Display

Xvfb runs on display `:99` at resolution `1920x1080x24`. This is large enough for xLights' UI to render correctly without the memory overhead of a full 2560x1600 display.

### Entrypoint

The container entrypoint script:

1. Starts `Xvfb :99 -screen 0 1920x1080x24`
2. Sets `DISPLAY=:99`
3. Starts `x11vnc` in shared/forever mode on `:99`
4. `exec python3 main.py`

### Image Contents

| Source | Destination | How |
|--------|-------------|-----|
| xLights AppImage (extracted) | `/opt/xlights/` | Downloaded at build time via build arg |
| `/usr/local/bin/xLights` symlink | → `/opt/xlights/AppRun` | Created at build time |
| Application code (`main.py`, `generate_names.py`, templates, Shaders/) | `/app/` | Copied from repo |
| `entrypoint.sh` | `/entrypoint.sh` | Copied from repo |

Working directory is `/app`. Template files (`.xsq` templates, `Shaders/`) are baked into the image. Generated files (`Wish_Name.xsq`, `.fseq`, `name_list.txt`, `greg.log`) are written to `/app` at runtime in the container's writable layer. No persistent volume is needed — `.fseq` files are uploaded to FPP immediately after rendering and are ephemeral. Logs are emitted to both file and stdout; `kubectl logs` captures them.

## Configuration & Secrets

`greglights_config.json` contains MQTT connection details (host, port, username, password). It is stored as a k8s Secret and mounted as a file at `/app/greglights_config.json`. The existing `open('greglights_config.json')` call in `main.py` works with no changes.

## Kubernetes Resources

### Deployment

- **Replicas:** 1
- **Image:** `xlights-render:<version>` (tagged by xLights version, e.g., `2025.13`)
- **Env:** `DISPLAY=:99`
- **Volume mount:** `greglights_config.json` Secret → `/app/greglights_config.json`
- **Resources:**
  - requests/limits: `4Gi` memory, `4` CPU
  - xLights is a heavy renderer; these are firm requirements, not advisory

### Service

- **Type:** `LoadBalancer` (served by MetalLB)
- MetalLB assigns a stable IP from the configured address pool
- VNC port 5900 is exposed on that IP
- Connect any VNC client to `<metallb-ip>:5900`
- Optionally annotate the Service to request a specific IP (e.g., `192.168.1.200`) for predictability

## Data Flow

```
MQTT broker ──► pod (main.py)
                  │
                  ├─► generates Wish_Name.xsq / wish_long_name.xsq
                  │
                  ├─► subprocess: xLights -r <file>
                  │     └─► renders on Xvfb :99
                  │     └─► writes .fseq to /app/
                  │
                  └─► curl POST .fseq → 192.168.1.150 / .156 / .160 (FPP)

VNC client ◄── x11vnc ◄── Xvfb :99   (observe rendering in real time)
```

## New Files

No changes to existing Python code. New files added to the repo:

| File | Purpose |
|------|---------|
| `Dockerfile` | Image build, AppImage extraction, system deps |
| `entrypoint.sh` | Start Xvfb, x11vnc, then Python app |
| `docs/kubernetes.md` | Operational guide: build, deploy, connect VNC |
| `k8s/deployment.yaml` | Example Deployment manifest |
| `k8s/service.yaml` | Example LoadBalancer Service manifest |
| `k8s/secret-template.yaml` | Template for greglights_config Secret |

## Out of Scope

- TLS for VNC (home network, acceptable risk)
- Persistent log storage (stdout via `kubectl logs` is sufficient)
- Multiple replicas (xLights render is stateful per-job; single replica is correct)
- Building xLights from source
