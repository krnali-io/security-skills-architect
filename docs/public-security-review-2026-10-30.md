# Public project security and privacy review

30 October 2026 · Scope: public repository source, retained Git history, release attachments, development dependencies, CI and repository settings. This is a scoped AI-assisted review with offline reproductions. It is not an external human audit or a guarantee that no vulnerability exists.

## Disclosure checks

Two local scanners reviewed all retained Git history without finding credential patterns. Credential verification against external services was disabled. Release attachments were downloaded, archive paths checked and contents scanned; no tested private application/host/address/home-path identifiers or credential patterns were found in those attachments. Complete checksum sets matched. One older release intentionally has a withdrawn/incomplete attachment set and is labelled accordingly.

The current source tree and README artwork were anonymised. Some older source snapshots and automatically generated source archives retain identifying labels. Removing those identifiers requires the separately approval-gated history/tag migration; it is not described as complete. No actual labels or private operational details are reproduced here. A clean scanner result does not establish that unknown secret formats or all identifying information are absent.

## Confirmed tooling issues corrected in this preview

- Hidden runtime files could enter provider-bound evaluation context even when release packaging excluded them. Context selection now excludes hidden/private paths and exposes the selected file list before execution. This is filtering, not content redaction.
- Resolving a linked package root before validation hid the link from the package policy. Root and template links are now rejected before content is read.
- Recursive or oversized supplied text could fail outside the intended validation result. Inputs are bounded and parser failures are reported without echoing frontmatter values.
- Fast-exiting processes could exceed the trace budget before the poller noticed, and ordinary child processes could outlive the evaluator. Stream/process handling now enforces bounded capture and cleans up its process group. These controls do not sandbox a malicious CLI.
- Artifact writes and selected package members have strengthened path/resource checks, with synthetic regression cases.

The private code review records conditions and reproductions. No real provider calls, credential-validation calls or production application probes were made for this tooling review. Public evaluation suites remain planned until explicitly executed and reviewed.

## Repository and supply-chain changes

Secret scanning, push protection, private vulnerability reporting and dependency alerts are enabled. Main requires PR/check gates and blocks force pushes/deletion. CI action references are pinned to reviewed full commit IDs and allowed actions are restricted to first-party sources. Checkout credentials are not persisted. The development dependency is hash-locked and binary-only; its current advisory audit found no matches. Automated dependency/action update proposals are configured.

Only the latest linked preview should be used for new evaluations. Historical source and older previews can retain earlier implementation weaknesses. The release checksums authenticate neither the publisher nor all future updates; signed provenance, native host acceptance and broader behavioural/security testing remain open.

## Remaining acceptance

The private operational pilot is a separate system with separate findings. Public tooling fixes do not resolve its collector-authority, inventory-trust, transaction/recovery or independent-delivery gates. Keep model-generated explanations advisory, validate proposed effects outside the model and retain explicit coverage limits.
