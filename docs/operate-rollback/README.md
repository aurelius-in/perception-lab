# Operate & Rollback

- Startup: deploy via `make deploy.dev` (kustomize overlay)
- Health: check `/v1/healthz` and `/metrics`
- Rollback: use Argo Rollouts to rollback to previous stable
- Blast radius: limit namespace `ml` and resource quotas
- Playbooks: triage CI failures (policy, build-sign), revert or fix quickly
