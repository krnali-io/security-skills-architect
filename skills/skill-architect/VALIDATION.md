# Build validation — 0.3.0-preview.2

Date: 30 October 2026. Decision: **conditional review / downloadable preview**.

| Check | Actual result |
|---|---|
| Tooling unit/integration tests | 34 passed, including fake-runtime process capture/timeouts and deterministic preview archive/checksum/privacy-boundary tests |
| Engineered package validator | Passed, no reported warnings |
| Changed lifecycle guidance and scaffold | Source inspection and structural checks only; live behavior not tested |
| Codex/Claude behavioral evaluations | No current-version calls made; earlier 0.2 results are historical only |
| Baseline benefit | Not established |
| Native host activation, effectful integration, independent security/UX review | Not tested |
| Official skills-ref tool | Not installed; not run |

The 0.2 preview had four successful Codex controlled-text smoke calls and a Claude attempt blocked by missing login. This does not establish acceptance of the changed 0.3 instructions. Original release metadata/evidence notes are preserved privately under evals/history/0.2.0-preview.1 and are excluded from preview archives, alongside raw results.

Current source adds proportionate continuing-assurance guidance, an application/operational lifecycle reference, a scaffold maintenance contract and an ongoing-defence design scenario. The template entrypoint uses a .template suffix to avoid accidental discovery as a separate installed skill. The preview builder emits local ZIPs and checksums without publishing or installing anything; allowlisted files still need content review before public release.

| Gate | State | Evidence / remaining work |
|---|---|---|
| Contract | pass for preview | Updated SPEC and generated continuing-assurance contract |
| Structure | pass for preview | Selected engineered checks, zero warnings; tooling tests |
| Safety | review | Author inspection, bounded tooling and adversarial plans; independent review/live behavior pending |
| Execution | review | 34 tooling tests; changed agent workflow and effectful integration not tested |
| Discovery | not-tested | Native activation pending; historic catalog tests do not establish it |
| Result quality | not-tested | Current baseline/treatment and artifact rubric review pending |
| User experience | review | Example/setup/failure guidance; human first-use review pending |

Next acceptance: run current paired cases, inspect outputs against all criteria, test native discovery/resources on each claimed host and complete broader application/operator acceptance. A separate private companion pilot has exercised local-model advisory interpretation; that does not establish acceptance of this general architect workflow. Missing evidence remains conditional review; no stable public support or performance claim is made. GitHub preview releases are available. The engineering tools themselves do not deploy or publish. Public reuse licensing remains unresolved. This revision updates version, publication and feedback documentation; current workflow behaviour still lacks broad acceptance.
