# Security follow-up: corrections and remaining production gates

30 October 2026 · Sanitized public summary · Decision: **conditional preview; bounded enrolled pilot**.

A separate AI reviewer inspected the private reference runtime, its tests and deployed service posture, reproduced selected defects offline, and independently repeated the correction tests. This was a scoped AI-assisted review, not an external human audit, penetration test or production certification. Application identities, host names, internal addresses, deployed dependency versions and raw reports remain private.

## What the review changed

The reusable instructions now carry the following lessons into generated application skills and executor designs:

- Preserve historical exploitation evidence separately from current catalogue membership and source health. Derive urgency after that reconciliation; an outage or omission cannot silently remove the urgent action.
- Model advisory withdrawal, reinstatement and a later verified deployment retest as explicit transitions, preserving the source history.
- Independently protect enrollment/baseline requirements. Missing stores, markers or repeated recovery failures must not silently create an empty baseline for an enrolled application.
- Bind success, immutable run evidence and current finding stores to a consistent generation. A timestamp or valid JSON file alone cannot prove healthy coverage.
- Coordinate watchers with writers. Running is job state backed by the last committed evidence; it cannot renew that evidence's age. Avoid mixing generations across lock boundaries.
- Publish run history create-only. Use secure temporary creation and appropriate file/directory durability, while keeping cross-artifact transaction/recovery requirements explicit.
- Treat workload-reported versions and hashes as observations rather than independent attestation. Reconcile trusted build/artifact inventory and record disagreements.
- Separate unprivileged analysis/model execution from any narrow trusted collector. Prompts, fixed commands and a read-only socket mount do not enforce an administrative API boundary. Keep code/configuration immutable to analysis.
- Keep deterministic observations, findings and verification primary. Model explanations remain unverified advisory text; syntax checks or phrase guards cannot establish factual correctness.
- Require independently exercised notification and operator delivery before claiming that coverage. A same-host watcher and local journal are insufficient for complete host-loss notification.

## What was verified

The private reference runtime passed **29 independently repeated runtime tests**, alongside **six earlier targeted regression probes**. The corrected enrolled configuration completed a staged real review and its same-host watcher reported fresh. Tests exercised the specific state-loss, finding-transition, secure-write, create-only-history, store-consistency and concurrent-observation regressions. This evidence supports the bounded pilot, not arbitrary generated executors or universal detection accuracy.

The public engineering tools separately pass **34 tooling tests**. Both reusable packages and their selected archive contents pass structural checks. The application builder now has **26 planned scenarios and eight trigger cases**, a **60-call** controlled-text plan; the general architect also has a new planned operational-boundary case. These factory model evaluations have **not** been executed. Earlier smoke calls and private runtime tests do not substitute for them.

## What is still open

Production acceptance still requires enforced collector/analysis authority separation, independently trusted inventory, durable multi-artifact recovery, streaming/aggregate resource bounds and retention, approved network/egress controls, independent delivery and server-loss recovery, broader model-quality evaluation and distribution/update trust. Native host activation and broader first-use acceptance remain unverified.

The local model has no command tools or patch authority in the reference pilot. Nevertheless, neither that fact nor passing the tests certifies the surrounding administrative process. The scoped corrections do not resolve every architectural threat identified by the review.

The public downloads contain reusable instructions, references and engineering tooling. They do not contain the private application executor, profile, raw audit or findings, and do not start a monitoring service. krnali Ops remains the intended operator destination; its adapter has not been implemented or verified. No automatic production fixes, full infrastructure assessment, discovery of undisclosed zero-days or production-readiness score is claimed.

Public reuse licensing is still awaiting the owner's decision. New package/release versions preserve the distinction between published downloads and accepted engineering evidence.

Licensing update, 31 October 2026: the project and current skill packages are now licensed under [Apache-2.0](../LICENSE). Licensing statements above are retained as historical evidence of the original review date.
