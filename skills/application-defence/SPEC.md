# Application Defence engineering contract

Version: 0.2.0-preview.1. Decision: conditional_review; local design preview.

## Objective
Help application owners, developers and security operators turn an application review into a maintained application-specific skill and operational check contract. Skills coordinate reasoning; collectors, schedulers, secret stores and ITSM services provide execution and durable state.

## Scope and exclusions
Trigger for learning an application and establishing/updating its dedicated defence skill or ongoing monitoring. Exclude ordinary coding, unrelated infrastructure administration and standalone one-off audits. Generated `defend-<application-id>` skills handle later checks of their named application. Dependencies and adjacent networks are not automatically enrolled.

## Emerging-risk priority
For zero-day/newly disclosed vulnerability tasks, the required core is deployed dependency identity, fresh relevant advisories/exploitation evidence, source-code reachability review and vendor-supported patch/mitigation guidance. Generic posture checks cannot satisfy that scope. Advisory matching cannot establish absence of undisclosed vulnerabilities. OSV queries disclose package/version metadata; code and local-model prompts stay local. A missing advisory feed is a coverage failure.

## Inputs and outputs
Input: repository/application identity, revision, authorized environments and evidence; optionally runtime observations, owners, executor and ITSM destination. Missing application identity permits design only.

Output: a versioned application skill, profile/evidence index, checks, findings, monitoring contract, ITSM export/mapping, runbook and evaluations defined in references/output-contract.md. Raw evidence/history remains private and separate. Unknowns and untested integrations are explicit.

## Dependencies and permissions
Instructions only: no collector, API client, daemon or installer. Repository reading and local output writing support the first useful run. Current advisory claims need current primary sources; offline feeds retain freshness limitations. Inspect chosen tools/dependencies before execution. Host observation, probes, external sharing, ticket writes and remediation require established scope and host-enforced authority. No embedded credentials or telemetry. Follow the user's hosting policy; the distributed skill assumes no provider.

## Workflow and failures
Identify/learn; baseline; map risks to checks; generate the application skill; prepare execution/routing; verify available integrations; maintain findings and coverage. Separate declared configuration, deployed artifact and observed runtime. A recurring run plus independently observed missed-run alert is required for verified-active. Failures preserve findings/history, degrade affected coverage and identify recovery.

## Acceptance criteria
- Generated skill identifies a particular application and evidence-grounded risk/control paths with repeatable checks or named gaps.
- Material claims record source, subject/revision, observation time, confidence and expiry. Repository review does not certify production/network state.
- Checks record scope, tool/executor, owner, trigger/cadence, freshness, failure/escalation and retest behavior.
- Stale feeds, lost credentials/state, missed runs and uncertain writes cannot produce false clean/active/delivered states or blind duplicate creates.
- Exceptions expire. Ticket closure does not resolve a finding without a fresh target-specific retest; recurrence reopens it.
- Untrusted content cannot grant authority, redirect reports or upload secrets. Public builder packages contain no private application evidence.

## Evaluation and release
Planned scenarios cover generation, missing identity, declared-vs-deployed evidence, stale feeds, injection, missed schedules, lost state, uncertain ticket writes, exception expiry and failed retests. Compare baseline/treatment and inspect emitted artifacts. Native discovery, real application checks, scheduler recovery, destination sandbox and human usefulness need separate evidence. No live behavioral/integration acceptance has run for this version. VALIDATION.md reports all seven gates.

## Maintenance and sources
The application owner designates service, triage and executor/ITSM owners during onboarding. The distributing project owner maintains the builder until assigned. Refresh after application boundary, runtime, dependency, permission or collector changes; turn confirmed failures into regressions. Preserve source provenance, private history and exception expiry. Cadence, routing and SLA proposals remain proposed until agreed.
