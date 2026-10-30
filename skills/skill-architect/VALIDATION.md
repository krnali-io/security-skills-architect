# Build validation — 0.3.0-preview.4

Date: 30 October 2026. Decision: **conditional review / downloadable preview**.

| Check | Actual result |
|---|---|
| Tooling unit/integration tests | 54 passed, including context filtering, linked roots/templates, bounded parser/process output, descendant cleanup, artifact confinement and archive/checksum regressions |
| Engineered package validator | Passed, no reported warnings |
| Changed lifecycle guidance and scaffold | Source inspection and structural checks only; live behavior not tested |
| Codex/Claude behavioral evaluations | No current-version calls made; earlier 0.2 results are historical only |
| Baseline benefit | Not established |
| Native host activation, effectful integration, human UX and general model safety | Not tested |
| Official skills-ref tool | Not installed; not run |

The 0.2 preview had four successful Codex controlled-text smoke calls and a Claude attempt blocked by missing login. This does not establish acceptance of the changed 0.3 instructions. Original release metadata/evidence notes are preserved privately under evals/history/0.2.0-preview.1 and are excluded from preview archives, alongside raw results.

Current source adds proportionate continuing-assurance guidance, an application/operational lifecycle reference, a scaffold maintenance contract and an ongoing-defence design scenario. The template entrypoint uses a .template suffix to avoid accidental discovery as a separate installed skill. The preview builder emits local ZIPs and checksums without publishing or installing anything; allowlisted files still need content review before public release.

| Gate | State | Evidence / remaining work |
|---|---|---|
| Contract | pass for preview | Updated SPEC and generated continuing-assurance contract |
| Structure | pass for preview | Selected engineered checks, zero warnings; tooling tests |
| Safety | review | Scoped separate-agent source review and offline regressions completed; live model/host boundaries and general safety remain unaccepted |
| Execution | review | 54 tooling tests; changed agent workflow and effectful integration not tested |
| Discovery | not-tested | Native activation pending; historic catalog tests do not establish it |
| Result quality | not-tested | Current baseline/treatment and artifact rubric review pending |
| User experience | review | Example/setup/failure guidance; human first-use review pending |

Next acceptance: run current paired cases, inspect outputs against all criteria, test native discovery/resources on each claimed host and complete broader application/operator acceptance. A separate private companion pilot has exercised local-model advisory interpretation; that does not establish acceptance of this general architect workflow. Missing evidence remains conditional review; no stable public support or performance claim is made. GitHub preview releases are available. The engineering tools themselves do not deploy or publish. Public reuse licensing remains unresolved. This revision carries scoped operational security lessons into the lifecycle/safety guidance and adds a planned boundary-design case. A separate AI reviewer independently repeated 29 private-runtime tests and the enrolled pilot completed a staged run; this does not certify factory output quality or production authority, inventory trust, transactions, resources or delivery. Current workflow behaviour still lacks broad acceptance.

The general architect's new operational-boundary case is planned, not executed. The reference runtime is private and not included in this package. See the [sanitized security follow-up](https://github.com/krnali-io/security-skills-architect/blob/main/docs/security-review-2026-10-30.md).

The public-tooling audit reproduced an unintended hidden-file provider-context path, package/template-root symlink bypasses, fast-exit trace-budget and descendant cleanup failures, and recursive-input failures. This revision corrects those paths with offline regression cases. The evaluator lists selected context paths/bytes before execution, filters selected text consistently with packaging, confines artifact writes using directory descriptors, bounds capture while streaming and requires POSIX process groups for execution. This is not general secret redaction, containment of a hostile CLI, or broad runtime-host acceptance. The hash-locked development dependency has a matching advisory audit with no known-vulnerability matches at review time. See the [public security review](https://github.com/krnali-io/security-skills-architect/blob/main/docs/public-security-review-2026-10-30.md).
