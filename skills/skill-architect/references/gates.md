# Seven quality gates

These are the default acceptance requirements for every skill we build. Risk changes the depth and applicable tests, not the obligation to report evidence honestly. States are `pass`, `fail`, `review`, `not-tested`; explain any check that is not applicable.

| Gate | Evidence required |
|---|---|
| Contract | Purpose, intended users, triggers/exclusions, inputs/outputs, dependencies and observable acceptance criteria in SPEC.md |
| Structure | Valid metadata, resolvable resources, concise runtime instructions and selected-profile validation |
| Safety | Reviewed permission/data boundaries and dependencies; relevant scanning and adversarial tests |
| Execution | Correct task sequence and failure handling; integration/recovery tests when effects or state exist |
| Discovery | Positive, paraphrased, near-miss and negative activation cases in each claimed native host |
| Result quality | Outputs judged against frozen criteria and comparable no-skill baseline; sample size and uncertainty |
| User experience | Clear setup, useful output, honest status, actionable failure and an opt-in feedback path |

A read-only formatting skill needs no production recovery drill. A privileged operations skill needs independent authority enforcement, refusal tests, uncertain-effect handling and recovery evidence. Do not require every skill to use a backend, produce signed evidence or create a separate service.

The `engineered` validator profile requires SPEC.md, README.md and planned evaluation files as our convention. The `portable` profile does not. Neither proves all seven gates. Static pattern warnings require inspection; a generic warning alone is not proof of an exploit.

Release decision: **fail** for unresolved blocking defects or critical scenario failures; **conditional_review** for missing evidence or untested required hosts; **pass** only after applicable gates have accepted evidence. Never average a failed safety boundary into a passing numerical score. Keep the case/rubric review and named reviewer with the release record. A smoke test is not a support commitment.
