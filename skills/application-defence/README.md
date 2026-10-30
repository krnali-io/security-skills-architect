# Application Defence — 0.1.0-preview.1

**Status:** local design preview / conditional review. No application has been assessed with this version. Live behavior, native discovery, collectors, scheduling and ITSM delivery remain unverified. No background service or credentials are installed.

## Value
Learn a specific application and generate or maintain its dedicated defence skill, evidence profile, recurring check plan and ITSM handoff. Use to establish application-specific ongoing security monitoring; exclude unrelated coding and standalone one-off audits.

## Install
Copy this skill folder to your agent's documented skill path, or use its supported installer. Check the host's actual version and capabilities.

## Example request
> Use $application-defence to learn the application in /path/to/repository and create its dedicated defence skill in /path/to/private-output. Review code, locked dependencies, application configuration and delivery definitions. Record host/network gaps. Prepare recurring checks and a local ITSM export; report what is verified.

The result is a `defend-<application-id>` skill plus its evidence/check profile. Begin with repository review and local output. Supply the chosen executor and ITSM destination for concrete setup. Later use the generated application skill to refresh evidence and triage changes. Skill Architect helps with engineering validation but is not required to interpret this package.

## Permissions and privacy
Repository access and local output are the initial requirements. Current advisories need source retrieval; host/network observation and integrations depend on authorized tools. Keep profiles/history private and credentials in a secret store. No telemetry or automatic uploads. The [Agent Skills format](https://agentskills.io/specification) is used; native host support needs actual acceptance testing.

Skill Markdown runs on invocation. Monitoring requires an executor, state, collectors and independent heartbeat/freshness alerts. A generated plan is designed, not verified-active. Runtime incident detection depends on suitable telemetry and tested rules. ServiceNow/Jira Service Management are candidate destinations, not implemented integrations; a neutral export needs tenant-specific mapping before delivery.

## Evidence
See SPEC.md and VALIDATION.md for scope, static checks and untested boundaries. Report version, host, expected/actual outcome and a sanitized reproduction through the existing project channel. Confirmed failures become regression cases; no public support channel is configured. Public licence and release location remain unselected.

## Uninstall
Remove only the installed builder directory through the host's documented process. Generated application skills, profiles and separately configured schedules remain separate resources. Retire schedules through their executor before decommissioning monitoring.

For newly emerging vulnerabilities, use the [emerging-risk workflow](references/emerging-vulnerabilities.md). It requires current deployed dependency evidence and advisory/exploitation sources, code-path triage and vendor-supported remediation. Container posture alone cannot satisfy this scope. The package does not ship a running feed collector or guarantee discovery of undisclosed zero-days.
