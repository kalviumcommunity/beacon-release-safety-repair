# Training incident fixture, not live telemetry

Candidate v2.3.1 is assumed deployed in this hypothetical incident only.
- 10:00: candidate promoted; previous image beacon-service:v2.3.0 healthy.
- 10:03: 35% of requests fail across all users; errors still rising.
- Two of three readiness checks fail. Root cause not yet understood.
- v2.3.0 is available and verified healthy in this scenario.
- No database/schema migration; rollback compatibility confirmed in fixture.

Use these supplied facts to decide recovery. Do not claim to have observed
these errors or performed a real rollback. Actual repo exercise deploys nothing.
