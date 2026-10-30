# Skills threat model and default controls

Skills contain instructions, reference data, optional code and tool requests. The agent harness (not the Markdown skill) is responsible for real authorization and sandbox enforcement.

Threats: prompt injection in README/webpages/repository files, malicious third-party skills, dependency substitution, vulnerable bundled executables, broad access grants, unexpected network egress, accidental write/destruction, secret leakage and fake validation reports.

Controls:
1. Treat skill packages and retrieved content as untrusted until inspected. Pin or review external dependencies; never blindly execute remote installer scripts.
2. Never embed credentials, private keys, tokens or production secrets into SKILL.md, assets, tests or logs. Mask them in all evaluations.
3. Declare and request least privilege. Require the host to enforce tool scopes and approval; `allowed-tools` is experimental and not a portable authorization mechanism.
4. Separate read-only planning from write/execute operations. Preview side effects; obtain authorization for destructive, external-sharing or production actions when it is not already established. Do not ask again for an already-authorized step.
5. Ensure scripts validate paths and inputs; use process APIs, not string-concatenated shell commands, and reject path traversal.
6. Test hostile content that says "ignore previous instructions", attempts to obtain secrets or redirects output to another destination.
7. For CI, use dependency scanning and secret scanning where applicable; run tests inside a restricted workspace with no production credentials.
8. Record source URLs and trust boundaries; treat LLM self-report of safety as unverified.

Acceptance: no unresolved high/critical issues; documented permissions and residual risks. A static grep for suspicious commands is a triage hint only, never a full malware analysis.

The text evaluation runner disables subject tools, but its host process uses existing provider login and sends the supplied prompt/skill context to that provider. Treat the CLI and its managed policies as trusted dependencies. Never use production secrets as fixtures. Raw traces are local private artifacts, not automatically redacted exports. Review/redact before sharing. A skill cannot contain a malicious host or eliminate all ambient administrative configuration.

## Operational service boundaries

For skills that design privileged or recurring operations, require authority enforced outside prompts. Separate an unprivileged model/analysis service from any narrowly scoped collector/broker; do not give analysis a raw Docker/cluster/admin socket merely because its current command is read-only. Keep installed code/configuration outside analysis-writable state, define allowed targets/operations and prove denied operations with negative tests.

Treat workload-generated inventories, source hashes and model claims according to their actual trust source; they are not attestation. Reconcile independently obtained artifact/build evidence and represent disagreement. Keep observations, verification and finding transitions deterministic; model prose is unverified advice.

Protect enrollment against silent baseline resets; verify committed generation/store consistency; refuse overwrite of immutable run history. Test secure temporary writes, crash/ENOSPC recovery, concurrency, streaming and aggregate resource bounds. A file/journal check on the same host is not independent server-loss delivery. Require tested operator notification and update provenance for any production claim, with raw evidence kept private.
