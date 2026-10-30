# Security

This project contains preview skill instructions and local engineering tools. It is not a production security monitor. Generated operational systems require their own access controls, security review and acceptance evidence.

## Supported version

Use the most recent preview linked from the root README. Earlier previews may lack later privacy, input-validation and process-handling corrections. A skill version or successful structural check is not a security certification.

## Report a vulnerability privately

Use **Security → Report a vulnerability** on this GitHub repository. Private vulnerability reporting is enabled. Include the affected version, a minimal synthetic reproduction, expected and observed behaviour, and the relevant file/line. Do not post credentials, private repositories, application profiles or raw provider traces in public issues.

If a real credential has been published, revoke or rotate it through its owner/provider. Removing a file or rewriting history alone does not revoke the credential, and existing clones or caches can retain earlier bytes.

## Trust and data boundaries

Scaffolding, validation and packaging run locally. Evaluation planning does not call a model. Explicit evaluator execution uses the selected provider CLI and sends the selected runtime context to that provider; it is not an offline or local-model workflow. Review the selected context before execution. File filters are not a general secret scrubber, and arbitrary ordinary text can still contain sensitive information.

The evaluator does not execute emitted artifacts. Its process-group cleanup and host flags are safeguards for a trusted local CLI, not containment for a hostile executable or host configuration. Raw outputs remain private and require review before publication.

## Repository controls

The default branch requires a pull request and passing checks. Force pushes and branch deletion are blocked. CI uses read-only repository permissions, does not persist checkout credentials, uses SHA-pinned first-party actions and installs hash-locked binary development dependencies. Secret scanning, push protection and dependency alerts are enabled. Checksums identify release bytes; signed release provenance remains separate work.
