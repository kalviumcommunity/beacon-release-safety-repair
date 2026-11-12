# Beacon release review

## Pipeline audit
Gap / risk / repaired dependency:
- Gap: The `production` job in `.github/workflows/release.yml` lacked a `needs:` dependency declaration referencing the `validate` job.
- Risk: Without an explicit `needs:` dependency, GitHub Actions executes jobs concurrently in parallel. If unit tests failed in the `validate` job, the `production` review job would still execute, risking evaluation or promotion of unverified, failing code.
- Repaired dependency: Added `needs: validate` under the `production` job in `.github/workflows/release.yml`. This enforces sequential pipeline ordering, guaranteeing that any test failure in `validate` blocks the `production` job from running.

Production reviewer control to configure (not demonstrated locally):
- An environment declaration (`environment: production`) in workflow YAML registers the environment name but does not enforce approvals on its own.
- Required reviewer setting: In GitHub repository settings, navigate to **Settings > Environments > production**. Under **Deployment protection rules**, enable **Required reviewers** and designate specific approvers or review teams. In addition, configure deployment branch protection to restrict execution to approved branches (e.g., `main`). (Note: Configuration must be completed in GitHub; no actual Actions execution or reviewer setup is demonstrated locally).

Secret handling and scope:
- Environment scope: Production secrets (such as `REGISTRY_TOKEN`) must be scoped strictly as environment secrets within the `production` environment in GitHub Settings, rather than global repository or organization secrets. This ensures only jobs referencing the approved `production` environment can access them.
- Step injection: Secrets must only be passed into specific job steps that require them via scoped environment variables (`env: REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}`).
- Masking & security: Secrets must never be printed, echoed (e.g., avoid `echo $REGISTRY_TOKEN`), logged in build output, or written to unencrypted disks or build artifacts.

## Traceability
Why PATCH is appropriate:
- Under Semantic Versioning (SemVer: `MAJOR.MINOR.PATCH`), a PATCH increment indicates backward-compatible bug fixes.
- Candidate `v2.3.1` increments the patch digit from `v2.3.0`. Per `release-contract.json`, the release is explicitly classified as a "backward-compatible bug fix" introducing no breaking changes (which would require a MAJOR increment) and no new features (which would require a MINOR increment).

Candidate image and annotated Git tag:
- Candidate image: `beacon-service:v2.3.1` (repaired in `k8s/deployment.json`, replacing the untraceable moving pointer `beacon-service:latest`).
- Annotated Git tag: `v2.3.1` created using `git tag -a v2.3.1 -m "Release candidate v2.3.1: bug-fix with repaired safety contract"`.

Record tag -> code commit in PDF using git rev-parse commands:
- Verification using git rev-parse:
  - Command: `git rev-parse HEAD`
  - Command: `git rev-parse "v2.3.1^{commit}"`
- Proof: Both commands resolve to the exact same final code commit SHA, demonstrating that annotated tag `v2.3.1` resolves directly to the final code commit.
- Provenance limitation: An annotated Git tag resolves to a Git source commit only; it does NOT inherently prove Docker/OCI container image provenance, registry identity, or artifact integrity without cryptographic signing (such as Cosign signatures) and attestable build provenance (such as SLSA).

Image-tag mutability limitation:
- A version image tag (such as `:v2.3.1` or `:latest`) is a mutable pointer in a container registry. Tags can be reassigned, overwritten, or modified in the registry without changing the tag string.
- In contrast, a verified image digest (e.g., `beacon-service@sha256:<digest>`) is a cryptographic hash of the image manifest and layer content. An immutable digest guarantees content integrity, deterministic pulling, and tamper resistance, providing a far stronger identity than a mutable tag.

## Incident recovery
Evidence and rollback vs forward decision:
- Incident signals (Labeled as supplied training fixture, not observed live runtime telemetry):
  - 10:00: Candidate v2.3.1 promoted; previous image `beacon-service:v2.3.0` was healthy.
  - 10:03: 35% of requests fail across all users; errors still rising.
  - Two of three readiness checks fail; root cause not yet understood.
  - No database or schema migration; rollback compatibility confirmed in fixture.
- Decision: Immediate **Rollback** to known-good image `beacon-service:v2.3.0` (rather than roll forward).
- Reason: High-severity customer impact (35% error rate, rising) with failing readiness probes and an unknown root cause requires immediate restoration of service availability. Because no schema migrations occurred and rollback compatibility is confirmed, rollback to `v2.3.0` is safe and fast. Fixing forward with an unknown root cause introduces unpredictable delays and severe operational risk.

Known-good target:
- `beacon-service:v2.3.0` (as specified in `release-contract.json` and verified healthy in the training fixture; repaired in `rollback.json`).

Proposed kubectl command (not executed):
- `kubectl set image deployment/beacon beacon=beacon-service:v2.3.0`
- (Proposed recovery command only; not executed against any live cluster).

Recovery checks after action:
- `kubectl rollout status deployment/beacon` (verify rollback deployment rollout finishes successfully).
- `kubectl get pods -l app=beacon` (confirm all pods transition to `Running` and `Ready` 1/1 without CrashLoopBackOff).
- `kubectl describe deployment/beacon` (verify replica set reconciliation and deployment events).
- `kubectl logs -l app=beacon --tail=100` (inspect container logs to verify clean startup and cessation of errors).
- Application endpoint probe: Verify service health endpoint returns HTTP 200 OK (`curl -f http://<service-ip>:8080/health`).
- Metrics & telemetry monitoring: Confirm user request error rates drop from 35% back to baseline 0% and latency stabilizes.

## Release note and decision
Change scope:
- Pipeline ordering: Repaired `.github/workflows/release.yml` by adding `needs: validate` to the `production` job.
- Release traceability: Repaired `k8s/deployment.json` by updating container image from `beacon-service:latest` to candidate `beacon-service:v2.3.1`.
- Rollback target: Repaired `rollback.json` by updating `target_image` from candidate `beacon-service:v2.3.1` to known-good `beacon-service:v2.3.0`.
- Governance documentation: Completed comprehensive audit, traceability, recovery, and release review in `readiness.md`.
- Unchanged components: `app.py`, `test_app.py`, `release-contract.json`, `incident-fixture.md`, and `check_release.py` remain strictly unchanged.

Local validation proof:
- `python -m unittest -v`: 1/1 test passed (`test_health` OK).
- `python check_release.py all`: All static contract checks passed (`pipeline: PASS`, `image: PASS`, `rollback: PASS`).
- Note: Local checks prove only this exercise's static contract, not Kubernetes schema validity, live gates, image existence, or runtime health.

Open risk / owner / mitigation:
- Open risk: Absence of enforced required reviewer protection rules on the `production` environment in GitHub repository settings, which could permit manual workflow dispatch to execute the production review without human sign-off.
- Owner: DevOps / Release Engineering Lead.
- Mitigation: Configure Required Reviewers in GitHub Settings > Environments > `production` and enforce deployment branch protection rules before triggering the release workflow.

Current production decision and blocker:
- Current production decision: **NO-GO**
- Blocker: Release approval status is `NOT REQUESTED` and deployment status is `NOT DEPLOYED` per `release-contract.json`. Passing local static checks does not constitute production readiness or authorize deployment; formal stakeholder approval, configured GitHub environment gates, and root cause investigation of the incident fixture are required blockers.

Terraform vs Kubernetes responsibilities:
- Terraform provisions and manages underlying cloud and cluster infrastructure (such as VPCs, subnets, IAM policies, and Kubernetes clusters), whereas Kubernetes orchestrates and operates containerized application workloads running on top of that infrastructure (such as Deployments, Pods, Services, and rollouts).
