# Deploying xLights Render to Kubernetes

## Prerequisites

- Docker installed locally (for building the image)
- `kubectl` configured to talk to your home cluster
- MetalLB installed and configured with an IP address pool
- Your `greglights_config.json` MQTT credentials file

## 1. Build the Docker Image

Use the default xLights version (2025.13):

    docker build -t xlights-render:2025.13 .

To use a different xLights version:

    docker build \
      --build-arg XLIGHTS_APPIMAGE_URL=https://github.com/xLightsSequencer/xLights/releases/download/2025.14/xLights-2025.14-x86_64.AppImage \
      -t xlights-render:2025.14 .

## 2. Load the Image onto Your Cluster

**If using k3s:**

    docker save xlights-render:2025.13 | sudo k3s ctr images import -

**If using a local registry (e.g., registry running at 192.168.1.10:5000):**

    docker tag xlights-render:2025.13 192.168.1.10:5000/xlights-render:2025.13
    docker push 192.168.1.10:5000/xlights-render:2025.13

Then update `image:` in `k8s/deployment.yaml` to match the registry path.

## 3. Create the MQTT Config Secret

Copy `k8s/secret-template.yaml` and fill in your MQTT credentials:

    cp k8s/secret-template.yaml k8s/secret.yaml
    # Edit k8s/secret.yaml — set host, port, username, password
    kubectl apply -f k8s/secret.yaml

Do not commit `k8s/secret.yaml` — it contains credentials. It is listed in `.gitignore`.

## 4. Deploy

    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml

Check that the pod is running:

    kubectl get pods -l app=xlights-render
    kubectl logs -f deployment/xlights-render

## 5. Find the VNC IP

    kubectl get service xlights-render-vnc

Look at the `EXTERNAL-IP` column — MetalLB assigns this from your address pool.
To pin a specific IP, uncomment and set the annotation in `k8s/service.yaml` before applying.

## 6. Connect via VNC

Open any VNC client and connect to:

    <EXTERNAL-IP>:5900

No password is required. You will see the virtual desktop. When the Python app
triggers a render, the xLights GUI will appear here in real time.

## 7. Upgrading xLights

1. Build a new image with the new AppImage URL (see step 1)
2. Load it onto the cluster (see step 2)
3. Update `image:` in `k8s/deployment.yaml` to the new tag
4. Apply: `kubectl apply -f k8s/deployment.yaml`
5. Kubernetes performs a rolling restart with zero downtime

## Troubleshooting

**Pod stuck in Pending:** Check resource availability — the pod needs 4 CPU and 4Gi memory on one node.

    kubectl describe pod -l app=xlights-render

**VNC not reachable:** Confirm MetalLB assigned an IP (`kubectl get svc xlights-render-vnc`). Check that port 5900 is not blocked by a firewall on the node.

**xLights render fails:** Check pod logs for the return code from `xLights -r`:

    kubectl logs -f deployment/xlights-render

**MQTT not connecting:** Verify the Secret was created correctly:

    kubectl get secret xlights-render-config -o jsonpath='{.data.greglights_config\.json}' | base64 -d
