# Host adapters and support ledger

The portable runtime entry is SKILL.md. Host discovery, invocation, metadata and permission behavior need separate acceptance.

| Host | Current package support | Evidence required before native compatibility claims |
|---|---|---|
| Codex | Optional agents/openai.yaml; CLI controlled-text evaluator | Native automatic/explicit activation, resources, tools and installed version |
| Claude Code | Portable instructions; CLI controlled-text evaluator | Native skill loading, resources, permission behavior and installed version |
| Cursor | Portable instruction source only | Actual installation, activation, authentication and task runs |
| Other runtimes | No tested adapter in this version | Customer-required host integration and recorded acceptance |

The evaluator uses CLI flags checked against local Codex 0.164.0 and Claude Code 2.1.292. It fails on unavailable/unsupported runtimes; it never removes permission controls to make an old version run. Controlled-text runs do not use native skill discovery. Do not promote their results to native support.

Configuration references consulted 24 October 2026: [OpenAI skills](https://learn.chatgpt.com/docs/build-skills), [OpenAI configuration](https://developers.openai.com/codex/config-reference/), [Claude CLI](https://code.claude.com/docs/en/cli-reference), and local CLI help. Recheck changed flags before changing supported versions. User login and admin-managed policies remain host concerns. No cloud deployment is performed by this package.
