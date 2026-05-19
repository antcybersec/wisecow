#!/usr/bin/env bash
# Generate a self-signed TLS certificate and create the wisecow-tls secret in Kubernetes.
set -euo pipefail

HOST="${1:-wisecow.local}"
NAMESPACE="${2:-wisecow}"
SECRET_NAME="${3:-wisecow-tls}"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$TMPDIR/tls.key" \
  -out "$TMPDIR/tls.crt" \
  -subj "/CN=${HOST}/O=AccuKnox Assessment" \
  -addext "subjectAltName=DNS:${HOST}"

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

kubectl -n "$NAMESPACE" create secret tls "$SECRET_NAME" \
  --cert="$TMPDIR/tls.crt" \
  --key="$TMPDIR/tls.key" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "TLS secret '${SECRET_NAME}' created in namespace '${NAMESPACE}' for host '${HOST}'."
