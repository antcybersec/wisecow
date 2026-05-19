.PHONY: build run deploy local-cluster tls-secret clean

IMAGE ?= wisecow:local
NAMESPACE ?= wisecow

build:
	docker build -t $(IMAGE) .

run: build
	docker run --rm -p 4499:4499 $(IMAGE)

local-cluster:
	bash scripts/setup-local-cluster.sh

tls-secret:
	bash scripts/generate-tls-secret.sh wisecow.local $(NAMESPACE) wisecow-tls

deploy:
	cd k8s && kustomize edit set image wisecow=$(IMAGE) && kubectl apply -k .
	kubectl rollout status deployment/wisecow -n $(NAMESPACE) --timeout=120s

clean:
	-kind delete cluster --name wisecow 2>/dev/null || true
