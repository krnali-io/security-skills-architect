# Behavioral evaluation

## Plan and evidence

Freeze task, rubric and skill context before comparing outputs. Include realistic successes, near misses, ambiguity, dependency failures and injected instructions in supplied data. Use synthetic or authorized fixtures. Choose tests proportionate to the effects the skill can cause.

The CLI runner supports Codex and Claude through `scripts/evaluate.py`. Plan with `--host HOST --suite scenarios|triggers|all --output NEW_DIRECTORY`; add `--run` for provider calls. Select case IDs with repeated `--case`, use bounded `--repeats`, `--max-runs`, `--timeout`, and optionally pin `--model`. No credentials are accepted in cases or copied into result files by the runner.

`controlled-text-v1` intentionally disables native customizations and subject tools. It evaluates guidance over supplied text and captures text artifacts; it cannot test scripts, MCP effects, recovery or native skill discovery. Do not work around that limit by removing permission controls. Use a separately reviewed host integration profile for those tests.

For scenarios, fresh baseline and treatment processes get identical tasks/tool availability; only the treatment receives the runtime skill files. SPEC.md and eval definitions are withheld. Across repeats the order alternates. Compare observed model identity where available; unknown model identity weakens comparability and stays visible. Cold/warm caches, unpinned host defaults and small samples limit time/token comparisons.

For triggers, the host receives name/description and a user prompt, then returns `use_skill`. These results are catalog-selection experiments, not native activation precision/recall. Native discovery remains a required independent gate before claiming native support.

## Case format

`evals/triggers.json` is an array of `{id, prompt, should_trigger}`. Include requests that omit the skill name and nearby tasks that should not select it.

`evals/scenarios.json` is an array with `id`, `category`, `prompt`, nonempty `acceptance` criteria and optional `checks`. Scaffolder TODO cases cannot be executed. Supported checks are:

- `{ "type": "json_field", "path": ["decision"], "equals": "denied" }`
- `{ "type": "contains", "value": "required text" }`
- `{ "type": "not_contains", "value": "forbidden text" }`
- `{ "type": "artifact_exists", "path": "example/SKILL.md" }`

Text checks and artifact existence are limited assertions, not comprehensive correctness or security judgments. An unscored case requires rubric review. For file-generation tasks the subject returns JSON with `artifacts` mapping relative paths to text; the runner captures those files in a separate artifact directory without executing or installing them. Then inspect and validate their contents as appropriate.

## Review and release

Inspect raw output against every acceptance criterion, including semantic failures not captured by assertions. Retain trace, final answer, artifact hashes, command/profile, date, versions, usage when observed, and failure examples. Provider errors are infrastructure failures, not poor skill performance. A completed CLI process without a terminal success event is incomplete.

Compare the baseline and treatment on the same cases. Report ties and regressions as well as improvements. One successful pair cannot demonstrate general benefit. Use repeated/held-out cases and independent human or authorized model judging where subjective quality matters; disclose judging method and sample size.

The generated report returns fail for tested subject assertion failures and conditional_review otherwise. It leaves native discovery, independent safety, human UX and subjective quality gates open. The release reviewer can issue pass only when all applicable evidence is accepted in the release record. Never turn planned cases into executed evidence or report a runner unit test as agent success.

Raw traces are private and not automatically sanitized. Review/redact before sharing. Feedback and extra evaluation calls are opt-in; no telemetry or scheduled collection is included.
