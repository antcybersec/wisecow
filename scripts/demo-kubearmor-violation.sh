#!/usr/bin/env bash
# Trigger a KubeArmor policy violation inside the Wisecow pod for screenshot evidence.
set -euo pipefail

NAMESPACE="${NAMESPACE:-wisecow}"
POD="$(kubectl get pods -n "$NAMESPACE" -l app=wisecow -o jsonpath='{.items[0].metadata.name}')"

if [[ -z "$POD" ]]; then
  echo "No Wisecow pod found in namespace ${NAMESPACE}."
  exit 1
fi

echo "=== Triggering blocked binary (curl) in pod: ${POD} ==="
kubectl exec -n "$NAMESPACE" "$POD" -- curl -s http://example.com 2>&1 || true

echo ""
echo "=== Recent KubeArmor alerts (last 20 lines) ==="
kubectl logs -n kube-system -l kubearmor-app=kubearmor --tail=50 2>/dev/null \
  | grep -i -E "wisecow|curl|Blocked|Alert" | tail -20 \
  || echo "Install KubeArmor and check: kubectl get kubearmorpolicies -n ${NAMESPACE}"

echo ""
echo "Capture a screenshot of the output above for PS3 submission."
