# KubeArmor Zero-Trust Policy (PS3)

## Prerequisites

```bash
# Install KubeArmor on your cluster (see https://docs.kubearmor.io/kubearmor/)
kubectl apply -f https://raw.githubusercontent.com/kubearmor/kubearmor/main/deployments/kubearmor.yaml
kubectl wait --for=condition=ready pod -l kubearmor-app=kubearmor -n kube-system --timeout=120s
```

## Apply policy

```bash
kubectl apply -f kubearmor/wisecow-zero-trust-policy.yaml
kubectl get kubearmorpolicies -n wisecow
```

## Generate a policy violation (for screenshot)

```bash
bash scripts/demo-kubearmor-violation.sh
```

Or manually:

```bash
POD=$(kubectl get pods -n wisecow -l app=wisecow -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n wisecow "$POD" -- curl http://example.com
```

Expected: execution of `curl` is **blocked** by `wisecow-block-dangerous-binaries`.

## Screenshot

Save evidence as `kubearmor/screenshots/policy-violation.png` showing:

1. The blocked `kubectl exec` command
2. KubeArmor alert/log output referencing the violation

Commit both the policy YAML and the screenshot to your repository.
