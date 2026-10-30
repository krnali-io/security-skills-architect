# Application Defence — 0.2.0-preview.2

**Status:** published preview / conditional review. The reusable builder has structural checks and planned behavioural cases. A separate private application pilot has exercised deployed-package advisory queries and local-model interpretation; broader builder behaviour, native discovery, recovery and live krnali Ops delivery remain unverified. This package installs no collector, background service or credentials.

## Value

Learn a specific application and generate or maintain its dedicated defence skill, evidence profile, recurring check plan and operator handoff. Prioritize newly disclosed vulnerabilities and zero-day exposure triage using deployed versions, current advisories, relevant code paths and vendor-supported response guidance. See [the emerging-risk workflow](references/emerging-vulnerabilities.md). Container posture alone cannot satisfy this scope, and advisory matching cannot discover an undisclosed flaw.

## Install and use

Use the [project installation guide](https://github.com/krnali-io/security-skills-architect#install-in-codex) or your host's documented mechanism. Test actual host activation and resource access.

> Use $application-defence to learn the application in /path/to/repository and create its dedicated defence skill in /path/to/private-output. Prioritize exact deployed dependencies, fresh advisories and exploitation evidence, affected code/configuration paths, and vendor patches or mitigations. Record source freshness and unknown reachability. Prepare recurring checks and a local operator export; report what is verified.

The result is a `defend-<application-id>` skill plus its evidence/check profile. Begin with authorized repository review and private output. Supply the selected executor and operator destination for concrete setup. Later use the generated application skill to refresh evidence and triage changes. The builder does not have to remain installed to use the generated package.

## Execution, permissions and privacy

Skill instructions run on invocation. Recurrence needs separately configured collectors, an executor, durable state and an independent freshness check. Record configured, verified-active and degraded coverage separately. The private pilot uses a fixed collector, systemd and local Ollama; that runtime and its application profile are not bundled here.

Current advisory checks require source retrieval. OSV queries can disclose package names/versions or commit identity to the service; document the actual egress. Keep source, model prompts, secrets and raw histories private unless sharing is explicitly authorized. A local model does not make all connected tools offline. Keep credentials in the executor's secret store. No telemetry or automatic trace uploads are installed by this package.

Use the operator's existing destination. Our pilot intends to use krnali Ops; its adapter remains unconnected. A separate ITSM product is unnecessary. Other destinations need their own authorized mapping and tested delivery. Local exports stay unsent until then. Runtime incident detection requires actual telemetry and tested rules.

## Evidence and feedback

Read [SPEC.md](SPEC.md) and [VALIDATION.md](VALIDATION.md) for scope, structural checks, pilot evidence boundaries and open gates. The [project review](https://github.com/krnali-io/security-skills-architect/blob/main/docs/review-2026-10-30.md) records lessons from the private pilot without publishing its raw profile or findings.

Use [GitHub issues](https://github.com/krnali-io/security-skills-architect/issues) for sanitized reports containing version, host, expected/actual result and a minimal reproduction. Confirmed failures become regressions. A public reuse licence is still awaiting an owner decision; publication does not assert an open-source licence grant. Native host support requires acceptance testing beyond the [Agent Skills format](https://agentskills.io/specification).

## Uninstall

Remove only this installed builder through the host's documented process. Generated application skills, profiles and separately configured schedules remain separate resources. Retire monitoring through its executor before decommissioning it.
