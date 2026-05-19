# Wisecow — AccuKnox DevOps Trainee Assessment

Containerized deployment of the [Wisecow](https://github.com/nyrahul/wisecow) cow-wisdom HTTP server on Kubernetes, with CI/CD, TLS, monitoring scripts, and KubeArmor zero-trust policies.

## Repository structure

| Path | Description |
|------|-------------|
| `Dockerfile` | Container image for Wisecow |
| `k8s/` | Kubernetes manifests (Deployment, Service, Ingress, TLS) |
| `.github/workflows/ci-cd.yaml` | Build, push to GHCR, deploy to Kubernetes |
| `scripts/system_health_monitor.py` | PS2 — system health monitoring |
| `scripts/app_health_checker.py` | PS2 — HTTP application uptime checker |
| `kubearmor/` | PS3 — zero-trust KubeArmor policies |

---

## Problem Statement 1 — Docker & Kubernetes

### Prerequisites

- Docker
- `kubectl`, `kustomize`
- Kind or Minikube (local)
- nginx Ingress Controller (installed by `make local-cluster`)

### Build and run locally

```bash
make build
make run
# Browser: http://localhost:4499
```

### Deploy to Kind with TLS

```bash
make local-cluster    # Kind + nginx ingress + TLS secret
make build IMAGE=wisecow:local
make deploy IMAGE=wisecow:local

# Add to /etc/hosts:
# 127.0.0.1 wisecow.local

curl -k https://wisecow.local:8443/
```

TLS is provided via a self-signed certificate (`scripts/generate-tls-secret.sh`) and the Ingress in `k8s/ingress.yaml` with `ssl-redirect` enabled.

For **cert-manager** (automatic renewal), apply `k8s/certificate.yaml` after installing cert-manager and a ClusterIssuer.

### Kubernetes resources

- **Deployment** — Wisecow pod on port 4499, non-root, dropped capabilities
- **Service** — ClusterIP, port 80 → 4499
- **Ingress** — HTTPS via `wisecow-tls` secret, host `wisecow.local`

### CI/CD (GitHub Actions)

Workflow: `.github/workflows/ci-cd.yaml`

| Job | Trigger | Action |
|-----|---------|--------|
| `build-and-push` | push/PR to `main` | Build image, push to `ghcr.io/<owner>/<repo>` |
| `deploy` | push to `main` | Apply manifests, rollout with commit SHA tag |

**Required GitHub configuration:**

1. **Repository → Settings → Actions → General** — Workflow permissions: read/write packages.
2. **Repository secret `KUBE_CONFIG`** (optional, for remote CD only) — Base64-encoded kubeconfig:
   ```bash
   cat ~/.kube/config | base64 | pbcopy   # macOS
   ```
   **Important:** Kind, Minikube, and Docker Desktop kubeconfigs use `127.0.0.1`. GitHub Actions runs in the cloud and **cannot** reach your Mac. The workflow skips deploy for localhost kubeconfigs. Use a cloud cluster (EKS, GKE, AKS, etc.) for automated deploy, or deploy locally with `make deploy`.
3. Update `k8s/kustomization.yaml` image `newName` to match your GitHub username/repo, or rely on CI `kustomize edit set image`.

**Image pull (private GHCR):** If the package is private, create an image pull secret in the `wisecow` namespace.

---

## Problem Statement 2 — Automation scripts

Chosen objectives: **(1) System Health Monitoring** and **(4) Application Health Checker**.

### System health monitor

```bash
pip install -r scripts/requirements.txt
python3 scripts/system_health_monitor.py --log-file /tmp/health.log
python3 scripts/system_health_monitor.py --cpu-threshold 80 --memory-threshold 85
```

Checks: CPU %, memory %, disk %, process count. Alerts go to console and optional log file.

### Application health checker

```bash
python3 scripts/app_health_checker.py http://localhost:4499
python3 scripts/app_health_checker.py --json http://wisecow.local:8443
```

Reports **UP** / **DOWN** based on HTTP status codes (default: 200).

---

## Problem Statement 3 — KubeArmor (optional)

See [kubearmor/README.md](kubearmor/README.md).

```bash
kubectl apply -f kubearmor/wisecow-zero-trust-policy.yaml
bash scripts/demo-kubearmor-violation.sh
```

Commit `kubearmor/wisecow-zero-trust-policy.yaml` and a screenshot under `kubearmor/screenshots/`.

---

## Original application

```bash
sudo apt install fortune-mod cowsay -y
./wisecow.sh
```

## License

See [LICENSE](LICENSE).
