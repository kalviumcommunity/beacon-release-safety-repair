# Beacon release review

## Pipeline audit
Gap / risk / repaired dependency: The `production` job had no `needs`, so it could
start in parallel with, or despite a failed, `validate` job. Untested code could reach
the production review step. Repaired with `needs: validate`, so production runs only
after validation finishes successfully.
Production reviewer control to configure (not demonstrated locally): Add required
reviewers in GitHub Settings > Environments > production (and optionally restrict
deployment branches/tags). The `environment: production` name alone enforces nothing.
Secret handling and scope: `REGISTRY_TOKEN` is referenced only via
`${{ secrets.REGISTRY_TOKEN }}`, scoped to the production job step env, and is never
printed. Workflow `permissions` stay at `contents: read`. No secret was added to the repo.

## Traceability
Why PATCH is appropriate: v2.3.0 -> v2.3.1 is a backward-compatible bug fix with no
API or schema change, so SemVer calls for a PATCH increment.
Candidate image and annotated Git tag: Image `beacon-service:v2.3.1` in
k8s/deployment.json (replacing moving `latest`); annotated Git tag `v2.3.1` on the final
code commit.
Record tag -> code commit in PDF using git rev-parse commands.
(`git rev-parse v2.3.1^{commit}` and `git rev-parse HEAD`; `git cat-file -t v2.3.1` shows `tag`.)
Image-tag mutability limitation: `v2.3.1` is still a mutable registry tag unless the
registry enforces immutability; it can be re-pushed to different content. Pinning by
digest (`beacon-service@sha256:...`) gives stronger identity.

## Incident recovery
Evidence and rollback vs forward decision: Per the training fixture, 35% of requests
fail across all users and are rising, 2 of 3 readiness checks fail, and root cause is
unknown. A fix-forward cannot be validated quickly. v2.3.0 is verified healthy and there
is no schema migration, so rollback is safe. Decision: roll back.
Known-good target: `beacon-service:v2.3.0` (rollback.json).
Proposed kubectl command (not executed):
`kubectl set image deployment/beacon beacon=beacon-service:v2.3.0` then
`kubectl rollout status deployment/beacon`
Recovery checks after action: rollout completes; all pods Ready and readiness checks
pass 3/3; error rate back to baseline; running image confirmed as v2.3.0
(`kubectl get deploy beacon -o jsonpath='{..image}'`); keep monitoring, then investigate
v2.3.1 root cause before any re-release.

## Release note and decision
Change scope: Release config only: workflow ordering (`needs: validate`), candidate
image pinned to `beacon-service:v2.3.1`, rollback target set to `beacon-service:v2.3.0`.
No application code changed.
Local validation proof: `python3 -m unittest -v` OK; `python3 check_release.py all`
pipeline/image/rollback PASS (static contract checks only).
Open risk / owner / mitigation: Required reviewers not yet configured on the production
environment and image tag is mutable. Owner: repo admin / release owner. Mitigation:
configure environment reviewers, enable registry tag immutability or pin by digest.
Current production decision and blocker: Production sign-off NOT REQUESTED; deployment
NOT DEPLOYED. Local PASS does not authorize production. Blocker: no reviewer approval and
no runtime/registry verification.
Terraform vs Kubernetes responsibilities: Terraform provisions infrastructure (cluster,
network, registry, IAM). Kubernetes manifests declare workload state on that cluster
(Deployment, image, replicas) and handle rollout/rollback.
