# Monitoring and recovery

Record existing capabilities and choose checks from application risks. Deterministic collectors produce repeatable observations; agent analysis interprets evidence and changes.

| Trigger | Purpose | Limitation |
|---|---|---|
| Relevant commit/merge request | Code, dependency and configuration changes/regressions | Repository may differ from deployment |
| Build/release/deployment | Bind artifact and inventory to target environment | Release success is not a security verdict |
| Relevant advisory update | Reevaluate locked/deployed libraries, runtime and images | Feed freshness and version matching matter |
| Periodic check | Advisories, drift, certificates, patch state, expired exceptions and overdue work | Interval leaves detection gaps |
| Runtime telemetry | Selected application/host/network incident indicators | Only integrated sensors and tested rules provide coverage |
| Independent heartbeat | Missed checks, stale evidence, expired credentials, failed delivery | Must operate outside the job it observes |

Cadence, freshness and SLA thresholds follow application policy. Suggested defaults need rationale and remain proposed until agreed. Record timezone and next expected run. Periodic posture assessment does not imply real-time intrusion detection.

## State and activation

- **designed:** plan exists; no installed job claimed.
- **configured:** configuration installed/read back; recurring execution or missed-run handling unverified.
- **verified-active:** observed recurring execution completed for the expected target, evidence persisted, and an independent missed-run/freshness alert was exercised and observed at the operator destination.
- **degraded:** active coverage is missing, stale, failing or unable to deliver required signals. Keep last good evidence and its age.
- **inactive:** deliberately disabled/retired; record owner, time and reason.

Use per-area states. Repository coverage may be active while host coverage is unavailable. One manual scan or timer registration is not activation evidence.

## Executor contract

Name the runtime/runner, exact targets, credential references and destinations. Preserve the user's deployment policy. Specify schedule/events, no-overlap locking, unique run IDs, atomic evidence/state commits, duration/output limits, bounded retry/backoff, rate limits, retention, access controls and independently observed heartbeat. Do not interpolate untrusted text into shell commands.

Generate runnable CI/timer/service configuration only for a known runtime with inspected commands. Otherwise return a design and missing setup facts. Markdown instructions do not provision a monitor.

## Failures and retests

Failed/skipped checks cannot erase findings. Stale feeds cannot produce current clean results. Unknown deployed identity limits claims to the observed subject. Lost state requires trusted recovery or an explicitly new baseline with reconciliation, not silent reset. Unavailable APIs produce bounded coverage/delivery errors. Reconcile uncertain writes before retry.

Use finding states `open`, `in_progress`, `mitigated`, `accepted_risk`, `suppressed`, `verified_resolved`. Reopen recurrence under the documented identity policy. Exceptions need owner, reason, scope and expiry; expiry queues review/retest rather than silently extending acceptance.

Verify fixes on the affected revision/artifact/environment using the specified test before closure. Proposed/merged patches and closed tickets are insufficient. Missing sensors indicate coverage loss. Dependency removal needs evidence of removal from the affected deployed artifact. Keep mitigation distinct from full correction; confirmed failures become regressions.

Test missed runs, expired credentials, stale feeds, overlapping jobs, partial state commits, lost state, destination failures and failed retests before operational acceptance. These require integration evidence from the chosen executor; text evaluations cannot certify them.
