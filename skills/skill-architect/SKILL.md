---
name: skill-architect
description: Design, build, review and evaluate reusable Agent Skills. Use for requests to create or improve a SKILL.md package, define its architecture and acceptance gates, test its triggers and outcomes, or prepare an evidence-backed release decision. Do not use for ordinary application coding or executing the operational task a skill describes.
metadata:
  version: "0.3.0-preview.2"
---

# Skill Architect

Turn a recurring user task into a useful, bounded skill whose claims can be checked. Use expert judgment for design, deterministic tooling for objective checks, and actual agent runs for behavioral evidence. Keep these evidence classes separate.

## Choose the work

Use the user's requested scope: design, build, review, evaluate or prepare a release. Review does not imply rewriting or publishing. For a small change, update the affected contract and checks rather than restarting the entire process. Use supplied context before asking questions; continue independent work while a material clarification is pending.

Check whether the capability belongs in a skill. A skill guides task-specific agent decisions; MCP/tools provide authenticated access; services enforce authority and durable state; deterministic code implements repeatable transformations. Do not embed an entire application or duplicate backend policy in Markdown. For service-backed workflows, read [the boundary guide](references/service-backed.md).

## Define and build

1. Establish intended users, task family, triggers and near misses, inputs, outputs, dependencies, permissions, failure behavior and observable acceptance criteria. Multiple user roles are fine when they share the same task. Preserve the chosen product and platform scope.
2. Write or update `SPEC.md` for our generated packages. Use the seven [quality gates](references/gates.md), scaled to risk. Keep unresolved choices and untested assumptions explicit.
3. Build the smallest useful `SKILL.md`. Put conditional expertise in references and deterministic operations in scripts only when needed. The runtime entry point should stay below roughly 5,000 tokens; the engineering contract and test evidence do not all belong in the agent's default context.
4. For a new package, run `python3 scripts/scaffold.py NAME --description DESCRIPTION --output PARENT` from this skill's directory. It refuses existing destinations. Replace the draft instructions and all placeholders with the actual task. Preserve an existing package's layout when editing it.
5. Supply `README.md`, positive/negative `evals/triggers.json`, and task/failure `evals/scenarios.json`. These are our engineering conventions, not requirements of the portable format. Generate `references`, `scripts`, `assets` and host metadata only when useful. Keep fixture data synthetic or explicitly authorized.

Give generated skills a proportionate maintenance contract: what assumptions can become stale, how to recheck them, who owns failures and what evidence verifies a correction. For skills managing an application or ongoing operational risk, read [the defence lifecycle](references/defence-lifecycle.md). Carry that contract into the generated skill's runtime guidance and evaluations. A recurring promise requires a real executor, durable state and loss-of-coverage reporting. A small offline skill may only need versioned regression cases; do not add application audits or monitoring infrastructure to unrelated tasks.

## Validate and evaluate

- Run `python3 scripts/validate.py PATH --profile engineered --json` for our package contract. Use `--profile portable` when auditing someone else's conformant minimal skill. The validator performs selected format/package checks, not a complete security assessment. Use the target host's official validator when available.
- Inspect scripts and dependencies before executing them. For tool, network or privileged workflows, read [security guidance](references/security.md). Existing user authorization remains valid; do not add confirmation loops for already-authorized work. Skills cannot grant authority or override host/environment policy.
- Read [evaluation guidance](references/evaluation.md) before runtime tests. Plan calls first with `python3 scripts/evaluate.py PATH --host codex --suite all --output NEW_RESULTS_DIR`. Substitute `claude` for the Claude adapter. Add `--run` to execute the approved evaluation scope with existing login; these calls can incur provider usage.
- The first runner profile uses supplied text, disables tools and compares fresh baseline/with-skill runs. Its catalog-selection tests are not native host activation. It captures raw traces, final outputs, emitted text artifacts, assertions and comparison evidence. It cannot certify effectful integrations. Do not manufacture a passing result when a runtime, dependency or required test is unavailable.
- Keep expected answers and evaluation criteria out of the subject's prompt. Compare the same task/model/tool access, record versions and repetitions, and distinguish deterministic assertions from subjective rubric review. Do not equate keyword matches or one successful sample with demonstrated improvement.
- Review setup, discoverability, result usefulness, failures and feedback using [UX guidance](references/ux.md). Read [platform guidance](references/platforms.md) only for hosts in scope. Do not claim portability from format alone.

## Decide and deliver

Report all seven gates with evidence and unresolved work. A known blocking defect or critical behavioral failure means **fail**. Missing required evidence means **conditional review**, with the package usable only under its stated preview limits. **Pass** requires applicable gates to have accepted evidence; irrelevant checks need a recorded rationale, not a fictitious test result. A local install is not public release approval.

Return the skill location/version, usage example, actual checks and runtime results, material limitations, and next corrective action. Keep the summary proportionate. Preserve detailed evidence locally in `evals/results` or the project's established evidence location; never upload traces or collect feedback automatically. Reevaluate material changes and confirmed regressions.
