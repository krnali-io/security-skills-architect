# Skill Architect engineering contract

Version: 0.3.0-preview.4. Status: downloadable preview, conditional review.

## Objective and users

Help developers and operators create, review and improve reusable Agent Skills whose usefulness and boundaries can be demonstrated. Skill Architect supplies judgment and workflow; scripts enforce objective checks; agent runs provide observed behavior. It is not a substitute for runtime authorization.

## Input and output

Input: a capability description or existing skill package, intended users, inputs/outputs, target hosts and constraints. Infer supplied context before asking for missing material decisions.

Output: a versioned skill directory with SKILL.md, engineering SPEC.md, README.md, planned activation/task evaluations, optional useful supporting resources, actual test evidence and a seven-gate decision. Reviews may return findings without changing files. An evaluation-only request does not authorize modifying the subject.

## Required gates

Contract, structure, safety, execution, discovery, result quality and user experience are mandatory reporting dimensions. Depth is proportionate to risk. See references/gates.md. `pass` requires accepted applicable evidence; `conditional_review` means required evidence is missing; `fail` means a known blocking defect or critical tested failure. No weighted score overrides a failed boundary.

## Tooling contract

- Scaffold refuses existing destinations, invalid names and linked templates. It produces reviewable text drafts and runs no generated code.
- Validator separates the optional portable profile from the default engineered package convention. It rejects duplicate frontmatter keys, missing resources, unsafe package links and malformed evaluation plans; checks Python syntax and selected patterns without executing subject scripts. Warnings are review hints, not a complete security scan.
- Evaluator supports installed Codex and Claude Code CLIs using existing login. Default behavior prints a call plan. Explicit `--run` launches bounded model calls with fresh process/workspaces and no subject tools. It captures evidence locally, rejects unsafe artifact paths, does not execute generated artifacts and stops on runtime failure.
- The treatment receives runtime skill files; the baseline receives the same task and tool restrictions without those files. Evaluation oracles are not sent to either subject. Snapshot hashes identify the exact context and cases evaluated. Version metadata alone is not evidence that later edits were tested.
- Triggers currently measure controlled catalog selection. Native automatic activation and tool-based operational integration require separate host acceptance.
- `report.json` keeps all seven gates visible and never automatically promotes partial automated evidence to release pass. Human rubric review, security and UX acceptance remain explicit.

## Boundaries and failure behavior

No deployment, publication, secret provisioning, external messaging or user configuration changes are performed by the tools. Existing authorization is respected without repetitive approval requests. Provider CLI calls use the host's login and administrative policies, and send supplied text to that provider; they are not an offline evaluation. CLI isolation is not a sandbox for a malicious CLI or a guarantee against host-admin behavior.

Only text contexts/artifacts fit the first evaluation profile (256 KiB context and emitted artifact limits, 50 artifact files). Runtime requests have a deadline and trace limit; no automatic retries or fallback models. Failed/missing auth is not a failed skill outcome. An absent result/terminal event cannot pass. Partial evidence remains reviewable after failure.

Unit/integration tests exercise scripts with synthetic files and fake runtime processes. Real provider runs are separately identified. Tests of the runner are not tests of every skill it may generate. No native runtime, general safety, or baseline advantage claim follows from a smoke test.

## Maintenance

Generated skills carry a proportionate continuing-assurance contract. Application and operational skills define baseline evidence, freshness, recurring execution/state, coverage failure escalation, operator/ITSM routing and verified remediation. Nonoperational skills may limit this to assumption refresh and regression cases. The architect does not itself become an application monitor or provision a scheduler. See references/defence-lifecycle.md. New guidance requires behavioral evaluation; historical 0.2 evidence does not certify it.

Keep one canonical source and a matching installed copy; preserve private run evidence separately from distributable packages. Reevaluate changed behavior, runtime adapters, permissions and confirmed regressions. Record reviewer, artifact/context hashes, versions, date, sample size, limitations and remediation in each release. The project owner accepts public releases; installation alone is not publication.

Operational monitor designs must apply the proportional lifecycle/security references: enforced least privilege, collector trust, protected enrollment, committed-state consistency, immutable run history and independent coverage/delivery. Separate private-pilot regression evidence from the architect's own unexecuted behavioural cases.

## Public-tooling review corrections

Provider-context selection excludes hidden/cache paths and unsupported resources, rejects linked package/resource roots, and exposes selected path/byte metadata in the dry-run plan. Ordinary visible text can still contain sensitive material; these filters are not general redaction. Package and parser bounds fail visibly. Generated artifact writes are confined/create-only and do not follow linked parent directories. Combined stdout/stderr capture is stream bounded and process-group cleanup runs after completion as well as timeout. Execution requires POSIX; planning can run on other supported Python platforms. The executable/login/environment remain trusted dependencies, and process-group cleanup cannot contain a deliberately hostile CLI.
