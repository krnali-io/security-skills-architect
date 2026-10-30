# Skill Architect — 0.3.0-preview.3

Build and review reusable Agent Skills against seven quality gates, with separate structural checks and actual behavioral evidence.

**Status:** downloadable preview / conditional review. The generator, validator and paired Codex/Claude CLI evaluator are implemented. Version 0.3 adds continuing-assurance guidance to generated skills and scaffolds. Earlier tooling and small Codex controlled-text results apply to version 0.2; the changed guidance has not had live behavioral acceptance. Native activation, effectful integrations and demonstrated baseline improvement remain unverified.

Application work follows [the defence lifecycle](references/defence-lifecycle.md): learn and baseline, check changes and freshness, route findings, and verify remediation. The separately packaged `application-defence` companion specializes this process into one generated skill per application. Monitoring needs an actual scheduler, collectors and persistent state; neither package silently installs these.

## Use the skill

In Codex, invoke `$skill-architect` with the recurring task, intended users, inputs, outputs and desired hosts. Example:

> Use $skill-architect to build a read-only skill that reviews an API contract and produces actionable findings. Define its acceptance criteria and evaluate it before making release claims.

Follow the [project installation guide](https://github.com/krnali-io/security-skills-architect#install-in-codex) and your host's documented discovery paths. If the current client does not discover a newly installed skill, start a new session. For other hosts, install the portable folder using that host's supported mechanism and test discovery; this package does not claim native compatibility from its layout alone.

## Local tools

Python 3.10+ and PyYAML are required. Use an existing environment or install the pinned dependency into a virtual environment; no automatic dependency downloads occur.

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/scaffold.py example-skill --description "Review API contracts and return evidenced compatibility findings. Use when reviewing an API specification." --output ./out
python3 scripts/validate.py ./out/example-skill --profile engineered --json
python3 -m unittest discover -s tests -v
```

Scaffolding creates a draft. Replace task placeholders before evaluating it. The default `engineered` policy requires SKILL.md, SPEC.md, README.md and evaluation definitions. Use `--profile portable` to assess a minimal third-party skill without imposing our documentation conventions. Both profiles run selected static checks, not full certification or malware analysis. `skills-ref validate` is an optional additional official check when available.

## Paired evaluations

First inspect the call plan; this makes no model calls and creates no results directory:

```sh
python3 scripts/evaluate.py . --host codex --suite all --case missing-host --case trigger-create --case not-trigger-code --max-runs 4 --output evals/results/my-codex-run
```

Add `--run` to execute it. Use `--host claude` for the Claude adapter. Existing host login is required. `--model` pins the same model request for both arms; without it, the report records host-default and any observed model. Where the trace omits model identity, equivalence remains unconfirmed. `--repeats`, `--timeout`, and `--max-runs` bound the work. The runner stops on runtime errors and retains partial evidence. It refuses to overwrite an existing output directory.

The first `controlled-text-v1` profile disables subject tools and native skills/plugins, supplies runtime skill text only to the treatment, and uses fresh processes for each arm. Acceptance criteria and expected values are retained outside the subject prompt. Repeated pairs alternate order. Discovery tests expose only name/description to a catalog-selection task; they do **not** measure native automatic activation.

The runner captures CLI JSONL events, stderr, prompt, final output, emitted text artifacts, SHA-256 digests, runtime version, elapsed time, usage when provided, assertion outcomes and paired comparisons. Raw traces can contain supplied data and are private local evidence; no automatic upload or redaction is claimed. Use only synthetic or authorized fixtures. Model calls send the supplied context to the selected provider and can consume paid usage.

Exit codes: 0 means the requested run completed (it may still require review); 1 means a tested subject assertion failed; 2 means invalid input, unavailable runtime or interrupted execution. Always inspect `release_decision` and the seven gates. A static pass or completed run is never automatic release approval.

See [evaluation guidance](references/evaluation.md) for case schemas and limits, [validation evidence](VALIDATION.md) for this build, and [the engineering contract](SPEC.md) for scope.

## Prepare a local preview download

```sh
python3 scripts/build_preview.py --skill . --output /path/to/new-preview-directory
```

Repeat `--skill` to include another package. The builder creates deterministic ZIPs, per-file/ZIP hashes, a manifest and SHA256SUMS. It includes only selected package resources and planned evaluation files; private run traces, profiles and unknown root files are excluded. Review included files before public sharing: allowlisting is not secret detection. Checksums are not signatures. Output is a local review preview, not publication or behavioural certification. Preview packages are published through the [project releases](https://github.com/krnali-io/security-skills-architect/releases). A public reuse licence still awaits the owner's decision. The scaffold entrypoint is stored as `SKILL.md.template` so an installer does not discover it as a second skill.

## Feedback and maintenance

Report the package version, host version, case ID, expected/actual behavior and a sanitized reproduction through [GitHub issues](https://github.com/krnali-io/security-skills-architect/issues). Do not attach credentials or raw customer traces. No telemetry or feedback transmission is installed. Confirmed failures become regression cases.

To remove the local skill, remove only its installed `skill-architect` folder after preserving any work you need. The development source and private evaluation results remain separate. No hosting, marketplace publication or operational access is configured.

Format reference: [Agent Skills specification](https://agentskills.io/specification). Host adapter sources and untested boundaries are listed in [platform guidance](references/platforms.md).
