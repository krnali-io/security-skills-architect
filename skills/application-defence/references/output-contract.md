# Per-application output

Generate one private `defend-<application-id>` package, usable without the builder installed:

```text
defend-<application-id>/
  SKILL.md
  SPEC.md
  README.md
  references/application.md
  references/operations.md
  profile.json
  checks.json
  findings.json
  monitoring.json
  itsm.json
  runbook.md
  evals/triggers.json
  evals/scenarios.json
```

Use versioned schema labels such as `application-defence.profile/v1`. These are agent-authored contracts, not shipped machine-validated schemas or universal vendor imports. Define exact types/enums and validate consistency before connecting a machine consumer. Add host UI metadata only when useful for the chosen host.

| Artifact | Required content |
|---|---|
| SKILL.md | Application-specific discovery; refresh/check/triage workflow; authorization/evidence rules; local references; response/retest contract |
| SPEC/README | Scope, inputs/outputs, tools, permissions, setup/use, acceptance, owner/version, removal and limitations |
| Application reference | Purpose, architecture, code locations, data/trust boundaries, dependencies, environments and unknowns |
| Operations/runbook | Verified tool invocations, compare/triage, failure recovery, escalation, retest and retirement |
| profile.json | Stable app ID; repos/revisions, environments/artifacts, owners, components/relationships, evidence index and per-area coverage |
| checks.json | Stable ID; risk/control; target; inspected collector/version; input/output; event/cadence/timezone; timeout/freshness; owner; failure route and retest |
| findings.json | Stable identity/correlation; app/environment/component/control; evidence; severity/confidence; first/last seen; status, owner/due date; remedy/retest; exceptions; external ticket IDs |
| monitoring.json | Executor/state location; per-area state; triggers; last run/success/next expected; independent heartbeat; failure route; retention and gaps |
| itsm.json | Destination/secret references; service/CI mapping; field/status/priority policy; correlation/reconciliation; routing; delivery state/setup gaps |
| Evaluations | Positive/paraphrased/near-miss triggers; application control paths; failures, injection, stale evidence and recovery |

Material observations need an evidence ID, source/path/query, subject/revision/artifact, observed-at UTC, source timestamp where relevant, confidence, freshness/expiry and status: observed, supplied, inferred, unavailable or stale. Store secret references only. Artifact hashes identify content; they do not attest trustworthiness.

Keep append-only private run history outside the installable package: run ID, skill/check/tool versions, target, evidence digests, completed/failed/skipped checks, timestamps, coverage, findings changes and delivery outcomes. The executor owns locks, atomic commits, access control and integrity. Initial baseline files do not prove an executor exists. Preserve prior baselines and open findings on refresh; record accepted exceptions separately.

Acceptance requires real code/configuration evidence supporting the risk model, a repeatable check or named gap for priority risks, and a useful first-run operator report. Do not manufacture application details to satisfy a file checklist.
