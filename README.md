# CA-3: Beacon Release Safety Repair

Standalone DevOps Foundation Module 3 CA. Exactly three planted faults:
pipeline ordering, candidate image traceability, and rollback target.
No application edits, cloud, registry login, real secret, Docker, or cluster needed.
Use Python 3.10+ and Git. JSON is valid Kubernetes manifest syntax.

## Contract

Read release-contract.json and incident-fixture.md. Candidate is a compatible
bug fix. Validation must finish successfully before the production review job.
Production job must retain its production environment and safe secret reference.
Image must identify candidate, not a moving default. Rollback must identify the
provided known-good image, not the failing candidate.

Workflow is a manual review simulation only: it never deploys anything.
An environment name does not itself enforce approval. Required reviewers must be
configured separately in GitHub Settings > Environments > production.
No actual approval or deployment is required for this CA. Do not add secrets.
Version image tags remain mutable unless protected; a digest gives stronger identity.

## Work in your fork

Fork, clone your fork, create fix/ca3-beacon. Read adjacent assessment from instructor.

```sh
python3 -m unittest -v
python3 check_release.py all
# Inspect each failure independently.
python3 check_release.py pipeline
python3 check_release.py image
python3 check_release.py rollback
git diff
```

Checker tests only this exercise's fixed-format contract. It does not validate
GitHub settings, Kubernetes schema, registry image existence, or runtime health.
Do not edit checker, release contract, incident fixture, or app to bypass faults.
Complete readiness.md briefly. Production sign-off is NOT REQUESTED, deployment
NOT DEPLOYED. Local PASS does not authorize production. Propose recovery only.

Commit repairs before creating annotated v2.3.1 on your final code commit.
Push branch and that tag only to your fork. Do not create upstream PR.
Submit one labelled PDF with genuine before/after evidence and explanations.
