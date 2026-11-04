# Beacon release review

## Pipeline audit
Gap / risk / repaired dependency: production could run before validation passed.
Added `needs: validate`; failed validation blocks production review by default.
Production reviewer control to configure (not demonstrated locally): repository
admin must configure required reviewers in Settings > Environments > production.
The environment name alone does not enforce approval.
Secret handling and scope: retained the production environment, read-only contents
permission and `${{ secrets.REGISTRY_TOKEN }}` reference scoped to the review step.
No real secret added, used or printed.

## Traceability
Why PATCH is appropriate: v2.3.0 -> v2.3.1 is the contract's backward-compatible
bug fix, without a new feature or breaking API change.
Candidate image and annotated Git tag: `beacon-service:v2.3.1`; annotated `v2.3.1`
created after committing repairs on `fix/ca3-beacon`.
Record tag -> code commit in PDF using `git rev-parse v2.3.1` (tag object),
`git rev-parse 'v2.3.1^{commit}'` (code commit), and `git rev-parse HEAD`.
Image-tag mutability limitation: version tags can be overwritten. Release owner
must protect tags and verify provenance; a verified digest gives stronger identity.
Registry contents and image provenance are not verified locally.

## Incident recovery
Evidence and rollback vs forward decision: the hypothetical fixture reports 35%
failures, rising errors and two of three readiness checks failing after promotion.
Cause is unknown; verified healthy v2.3.0 is available, rollback compatibility is
confirmed and no migration occurred. Propose rollback for faster restoration than
an unverified forward fix. These are supplied fixture facts, not live observations.
Known-good target: `beacon-service:v2.3.0` in `rollback.json`.
Proposed kubectl command (not executed):
`kubectl set image deployment/beacon beacon=beacon-service:v2.3.0`
Recovery checks after action: first verify cluster and namespace; then check
`kubectl rollout status deployment/beacon`, pod images, readiness, events, logs,
request error rate and latency against baseline. Confirm user recovery and monitor
stability; investigate the candidate before proposing another release.

## Release note and decision
Change scope: pipeline dependency, candidate image, rollback target and readiness
notes. Application, checker, release contract and incident fixture unchanged.
Local validation proof: `python3 -m unittest -v` passes (1 test);
`python3 check_release.py all` and each individual scope pass. PDF records actual
before/after command output and the annotated tag's final code commit identity.
Open risk / owner / mitigation: repository admin owns reviewer configuration;
release owner owns image digest/provenance verification; incident owner owns real
runtime recovery checks. These unverified controls block production readiness.
Current production decision and blocker: approval NOT REQUESTED; deployment
NOT DEPLOYED. Local PASS does not authorize production. Reviewer configuration,
image verification and an authorized production decision remain outstanding.
Terraform vs Kubernetes responsibilities: Terraform provisions infrastructure;
Kubernetes manages application workload configuration, image rollout, readiness
and recovery. Neither is executed here.
