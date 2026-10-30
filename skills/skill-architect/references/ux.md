# User experience contract

## Install/first run
Show a one-sentence value proposition, input examples, host support, dependencies, permissions and removal procedure. A skill should work for a first useful read-only example without registration where feasible.

## At invocation
Determine whether the task fits. Avoid unexpected skill activation. Ask only for blocking missing details. Disclose permissions and intended side effects before any privileged action. Explain when the skill cannot run in the user's current host.

## During work
Give useful progress for longer tasks, not repetitive narration. Distinguish facts, assumptions and tool failures. Prevent infinite loops. Save intermediate outputs only when user environment and permissions allow it.

## At completion
Return (1) concrete deliverable, (2) short status and what was checked, (3) meaningful findings with evidence, (4) what did not run / could not be proved, and (5) next action. Do not claim "all tests passed" when no real checks were run.

## Feedback loop
Document a simple correction path with expected versus actual behavior and reproduction details; do not append a feedback question to every routine response. Collect diagnostics only by opt-in; minimise and anonymise data where practicable. Store issue category, expected vs actual, skill+host version and reproduction instructions. Feed confirmed failures into regression scenarios; re-release after evaluation. Skill Markdown alone does not imply telemetry or a persistent feedback service.
