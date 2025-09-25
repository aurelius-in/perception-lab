SHELL := /bin/sh

OWNER ?= aurelius-in
REPO ?= perception-lab
TAG ?= $(shell git rev-parse --short HEAD)
IMAGE ?= ghcr.io/$(OWNER)/$(REPO):$(TAG)

.PHONY: help
help:
	@echo "Targets: init, build, sbom, sign, verify, policy.test, deploy.dev, evals, redteam.run"

.PHONY: init
init:
	@echo "Initialize local dev (placeholder)"
	@mkdir -p artifacts || powershell -NoProfile -Command "New-Item -ItemType Directory -Path artifacts -ErrorAction SilentlyContinue | Out-Null"

.PHONY: build
build:
	@echo "Building image $(IMAGE)"
	docker build -t $(IMAGE) .

.PHONY: sbom
sbom: artifacts
	@echo "Generating SBOM"
	syft packages dir:. -o spdx-json > artifacts/sbom.spdx.json

.PHONY: sign
sign:
	@echo "Signing $(IMAGE)"
	COSIGN_EXPERIMENTAL=1 cosign sign -y $(IMAGE)

.PHONY: verify
verify:
	@echo "Verifying $(IMAGE)"
	cosign verify $(IMAGE)

.PHONY: policy.test
policy.test:
	@echo "Running OPA/Conftest policy checks"
	conftest test serve/kserve/inferenceservice.yaml -p policy/opa
	conftest test serve/rollouts/rollout.yaml -p policy/opa

.PHONY: deploy.dev
deploy.dev:
	@echo "Deploying dev overlay"
	kustomize build gitops/overlays/dev | kubectl apply -f -

.PHONY: evals
evals:
	@echo "Running evals CLI"
	python ../dev/evals_cli.py

.PHONY: redteam.run
redteam.run:
	@echo "Running red-team harness"
	python redteam/runners/run_redteam.py

.PHONY: artifacts
artifacts:
	@mkdir -p artifacts || powershell -NoProfile -Command "New-Item -ItemType Directory -Path artifacts -ErrorAction SilentlyContinue | Out-Null"

