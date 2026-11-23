# Beacon release review

## Pipeline audit
Gap / risk / repaired dependency: The production job originally had no dependency on
`validate`, so it could run even when the application validation job failed. Added
`needs: validate`; a failed validation now blocks production review. This is a
static workflow repair only; GitHub Actions was not executed.
Production reviewer control to configure (not demonstrated locally): Configure
required reviewers for the `production` environment in GitHub Settings > Environments
> production. The environment name alone does not enforce approval. Approval is NOT
REQUESTED for this review.
Secret handling and scope: Keep `REGISTRY_TOKEN` as a GitHub Actions environment
secret scoped to `production`, grant it only to the job that needs it, and never
print its value. No secret value was added or exposed.

## Traceability
Why PATCH is appropriate: The contract describes v2.3.1 as a backward-compatible
bug fix with no application API or migration change, so the patch component changes
while compatibility is preserved.
Candidate image and annotated Git tag: The candidate image is
`beacon-service:v2.3.1`; the final annotated Git tag is `v2.3.1` and its target is
recorded in the PDF. The Git tag identifies source history, not image provenance.
Record tag -> code commit in PDF using git rev-parse commands.
Image-tag mutability limitation: A version tag can be moved or overwritten and is
weaker identity than a verified immutable digest. Registry verification and image
existence were not performed here.

## Incident recovery
Evidence and rollback vs forward decision: The incident data below is a supplied
training fixture, not observed runtime evidence: 35% request failures, rising
errors, and two of three readiness checks failing after candidate promotion. Roll
back rather than forward because impact is broad and rising, readiness is failing,
and the root cause is unknown; the fixture confirms rollback compatibility.
Known-good target: `beacon-service:v2.3.0`, available and verified healthy in the
supplied fixture.
Proposed kubectl command (not executed): `kubectl -n production set image
deployment/beacon beacon=beacon-service:v2.3.0`.
Recovery checks after action: inspect rollout status and pod readiness, verify error
rate and request success, confirm the deployment image, and monitor service health
before considering recovery complete. No cluster action was executed.

## Release note and decision
Change scope: Only pipeline ordering, candidate image reference, rollback target,
and this readiness review changed; application, checker, contract, fixture, labels,
ports, and workload names remain unchanged.
Local validation proof: `python3 -m unittest -v`, each scoped release check, and
`python3 check_release.py all` passed locally. These checks do not prove approval,
registry availability, schema validity, or runtime health.
Open risk / owner / mitigation: Owner: release engineer. The candidate image's
registry existence and immutable digest were not verified; verify the registry
artifact and pin a reviewed digest before any production release.
Current production decision and blocker: **NO-GO**. Approval is NOT REQUESTED and
the candidate is NOT DEPLOYED; required environment reviewers, registry/image
verification, and live health evidence are still blockers. Passing local checks does
not establish production readiness.
Terraform vs Kubernetes responsibilities: Terraform provisions infrastructure and
its supporting resources, while Kubernetes operates the application workload and
its rollout/rollback.
