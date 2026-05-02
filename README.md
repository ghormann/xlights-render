# xLights Render — Personalized Sequence Generator

Automatically generates and deploys personalized xLights light-show sequences in real time, driven by visitor name requests submitted via text message. Visitors text their name to a dedicated number; within minutes, their name appears on the light display synchronized to the current song.

For full background on the project — how the display works, the text-message integration, and a video — see the project write-up at **https://thehormanns.net/technology/text-message/**

---

## How It Works

1. A visitor texts their name to the show's phone number.
2. An external service publishes the name to an MQTT broker on the `/christmas/personsName` topic.
3. `main.py` listens to MQTT, queues the name, and waits for a `GENERATE` action message.
4. On generation, `generate_names.py` fills in placeholders in an xLights sequence template (`.xsq`) with up to 13 names plus a seasonal greeting.
5. xLights is invoked headlessly (`xLights -r`) to render the `.xsq` file into an `.fseq` binary sequence.
6. The rendered `.fseq` is uploaded via HTTP POST to the Falcon Player (FPP) instances on the network.

Special cases are also handled:
- **Birthday sequences** — triggered by the `/christmas/nameBirthday` topic, renders a personalized "Happy Birthday" sequence.
- **Midnight sequences** — triggered by `GENERATE_MIDNIGHT`, renders a long scrolling sequence of all names received during the night with a "Merry Christmas" or "Happy New Year" greeting depending on the date.

---

## Repository Layout

```
main.py                     # MQTT client, name queue, state machine
generate_names.py           # Template filling, xLights invocation, FPP upload
config.py                   # GregLightsConfig — reads and validates greglights_config.json
Wish_Name_Template.xsq      # Template for the standard 13-name sequence
Happy_Birthday_Name_Template.xsq  # Template for birthday sequences
wish_long_template.xsq      # Template for the midnight all-names sequence
xLights.conf                # Pre-seeded xLights config for docker (show directory, etc.)
xlights_rgbeffects.xml      # xLights effects/model layout
xlights_networks.xml        # Controller network definitions
xlights_keybindings.xml     # xLights keybindings
name_list_full.txt          # Full fallback name list if 13 not given
requirements.txt            # Python dependencies
Dockerfile                  # Container image definition
entrypoint.sh               # Container startup: Xvfb + VNC + Python app
Shaders/                    # xLights shader files
media/                      # Audio and media assets used by sequences
k8s/                        # Example  Kubernetes manifests
  deployment.yaml
  service.yaml
  secret-template.yaml
docs/
  run-docker.md             # Running the container locally for testing
  kubernetes.md             # Deploying to a home Kubernetes cluster
```

---

## MQTT Topics

| Topic | Direction | Payload |
|---|---|---|
| `/christmas/personsName` | Subscribe | JSON `{"name": "ALICE", "ts": ..., "from": "..."}` |
| `/christmas/personsNameFront` | Subscribe | Same as above — inserts name at front of queue |
| `/christmas/personsNameRemove` | Subscribe | JSON `{"name": "ALICE"}` — removes from queue |
| `/christmas/personsNameLow` | Subscribe | Same as personsName — lower-priority queue |
| `/christmas/nameBirthday` | Subscribe | Plain text name string |
| `/christmas/nameAction` | Subscribe | `GENERATE`, `GENERATE_MIDNIGHT`, or `RESET` |
| `/christmas/nameQueue` | Publish | JSON snapshot of all queues and current status |

---

## Name Queue Logic

- Up to 13 names are pulled per generation cycle: first from the normal queue, then from the low-priority queue, then padded with names from a built-in fallback list (`baseNames`).
- Names already in the queue are deduplicated automatically.
- Midnight sequences collect all names received throughout the night (up to 150) and render them as a single long scrolling sequence.

---

## FPP Upload Targets

Rendered `.fseq` files are uploaded via HTTP POST to the FPP instances listed in the `fpp_ips` field of `greglights_config.json`.

---

## Configuration

The app reads all configuration from `greglights_config.json` at startup:

```json
{
  "host": "mqtt.example.com",
  "port": 1883,
  "username": "user",
  "password": "secret",
  "fpp_ips": ["192.168.1.150", "192.168.1.156", "192.168.1.160"],
  "base_names": [
    "JEFF", "BRADY", "MARY", "NANCY", "JERRY", "HENERY",
    "ALEX", "TIM", "ABBIE", "MELISSA", "JUDY", "BRODY",
    "EMILY", "MATT", "WILL", "JULIA", "SOPHIE", "LONDON",
    "MAX", "BENNY", "LUIS", "KORIE"
  ]
}
```

- `fpp_ips` — list of Falcon Player HTTP endpoints to receive rendered `.fseq` files (at least 1 required)
- `base_names` — fallback names used to pad a generation cycle to 13 when the queue is short (at least 13 required)

This file is never committed. When running in Docker or Kubernetes, it is injected at runtime (see the docs below).

---

## Running Locally (Python)

**NOTE**: Must have X11 ui for xLights to launch

```bash
pip install -r requirements.txt
# Place greglights_config.json in the project root
python main.py
```

---

## Running in Docker

See **[docs/run-docker.md](docs/run-docker.md)** for full instructions.

Quick start:

```bash
docker build -t xlights-render:2025.13 .

docker run -d \
  --name xlights-render \
  -p 5900:5900 \
  -v /path/to/greglights_config.json:/app/greglights_config.json:ro \
  xlights-render:2025.13
```

Connect a VNC client to `localhost:5900` to watch xLights render sequences in real time. No VNC password is required.

---

## Deploying to Kubernetes

See **[docs/kubernetes.md](docs/kubernetes.md)** for full instructions, including loading the image into k3s, creating the MQTT credentials Secret, applying the manifests, and connecting via VNC through a MetalLB-assigned external IP.

Quick start:

```bash
docker build -t xlights-render:2025.13 .
docker save xlights-render:2025.13 | sudo k3s ctr images import -

cp k8s/secret-template.yaml k8s/secret.yaml
# Edit k8s/secret.yaml with your MQTT credentials
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

The pod requires **4 CPU / 2 Gi memory** on a single node.

---

## Upgrading xLights

Pass a different AppImage URL at build time:

```bash
docker build \
  --build-arg XLIGHTS_APPIMAGE_URL=https://github.com/xLightsSequencer/xLights/releases/download/2025.14/xLights-2025.14-x86_64.AppImage \
  -t xlights-render:2025.14 .
```

Then redeploy using the new image tag. In Kubernetes, update `image:` in `k8s/deployment.yaml` and `kubectl apply` — a rolling restart handles the upgrade with zero downtime.

---

## License

See [LICENSE](LICENSE).
