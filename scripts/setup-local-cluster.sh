#!/usr/bin/env bash
# Bootstrap a local Kind cluster with nginx ingress and optional cert-manager for Wisecow.
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-wisecow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if ! command -v kind >/dev/null 2>&1; then
  echo "kind is required. Install: https://kind.sigs.k8s.io/"
  exit 1
fi

if ! kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  kind create cluster --name "$CLUSTER_NAME" --config "$REPO_ROOT/kind-config.yaml"
fi

kubectl config use-context "kind-${CLUSTER_NAME}"

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s

bash "$SCRIPT_DIR/generate-tls-secret.sh" wisecow.local wisecow wisecow-tls

echo "Cluster '${CLUSTER_NAME}' is ready. Deploy with: make deploy IMAGE=ghcr.io/<user>/wisecow:latest"
