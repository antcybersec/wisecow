# AccuKnox DevOps Trainee Assessment — Submission Checklist

Use this checklist before submitting your **public** GitHub repository.

## Problem Statement 1

- [x] `Dockerfile` builds Wisecow (fortune, cowsay, netcat on port 4499)
- [x] `k8s/` — Deployment, Service, Ingress with TLS
- [x] `.github/workflows/ci-cd.yaml` — build/push to GHCR + deploy to K8s
- [ ] Push repo to GitHub (public)
- [ ] Set secret `KUBE_CONFIG` (base64 kubeconfig) for CD
- [ ] Verify workflow run is green on `main`

## Problem Statement 2

- [x] **Objective 1** — `scripts/system_health_monitor.py`
- [x] **Objective 4** — `scripts/app_health_checker.py`

## Problem Statement 3 (bonus)

- [x] `kubearmor/wisecow-zero-trust-policy.yaml`
- [ ] Install KubeArmor on cluster
- [ ] Run `bash scripts/demo-kubearmor-violation.sh`
- [ ] Save screenshot as `kubearmor/screenshots/policy-violation.png`
- [ ] Commit screenshot to repo

## Quick demo commands for evaluators

```bash
make build && make run
make local-cluster && make deploy IMAGE=wisecow:local
python3 scripts/system_health_monitor.py
python3 scripts/app_health_checker.py http://localhost:4499
kubectl apply -f kubearmor/wisecow-zero-trust-policy.yaml
```
