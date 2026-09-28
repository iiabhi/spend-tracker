---
description: Write and run tests for a Spendly feature (spec-driven, then executed)
argument-hint: <step-number-or-feature-slug>
---

Run the test-feature agent for feature/spec `$ARGUMENTS`, then run the test-runner agent to execute what it wrote.

1. Invoke the `test-feature` subagent for `$ARGUMENTS`. It reads the spec at `.claude/specs/<step>-<slug>.md` and writes pytest test cases under `tests/` based on that spec's Routes, Rules for implementation, and Definition of Done — not the implementation code.

2. Once `test-feature` finishes, invoke the `test-runner` subagent to execute the tests it just wrote (scoped to the relevant test file if `test-feature` reports one, otherwise the full suite) and report pass/fail results.

3. Summarize for the user:
   - Which spec was tested
   - How many tests were written and where
   - Pass/fail counts from the run
   - Any spec/implementation mismatches or genuine bugs the run surfaced

If `$ARGUMENTS` is empty, ask the user which spec/feature to test rather than guessing.
