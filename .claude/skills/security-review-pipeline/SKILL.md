---
name: security-review-pipeline
description: Use this when the user asks for a security review, after completing a feature slice, or before sharing the application with real users. Coordinates a three-role review pipeline (Reviewer → Orchestrator → Developer) for non-programmers.
---

# Security Review Pipeline

Coordinate a structured security review of the current codebase using separate review, triage, and fix phases. Keep analysis separate from remediation so the user can understand the risks before code changes are made.

## When to Use

Trigger this skill in any of the following situations:

- the user asks for a security review, asks "is this safe?", or asks "should I share this with real users?";
- a feature slice has been completed and the slice touches authentication, authorisation, sensitive data, external services, or destructive actions;
- before a release or before the application is used with real data, real users, or real money.

If `SPEC.md` does not yet exist, do not run the pipeline. Instead, ask the user to invoke `spec-coauthor` first, because the security elicitation in `spec-coauthor` produces the input this pipeline consumes.

## Pipeline

### Phase 1 - Security Reviewer

Goal: produce a structured list of security findings without proposing fixes.

Prefer Superpowers `requesting-code-review` when the host tool supports it. Use it to dispatch a security-focused reviewer while keeping the rest of this pipeline in Virgilio's non-programmer-facing format. If Superpowers review tools are unavailable, perform the review inline. Provide the following inputs:

- the SPEC.md "Security and Access Control" section (so the reviewer knows what was promised);
- the diff or current state of the codebase to review;
- a security-focused review prompt that requires the reviewer to look for, at minimum, these categories:
  - injection (SQL, command, prompt);
  - authentication bypass;
  - broken authorisation / IDOR;
  - insecure data storage (plaintext secrets, unencrypted PII);
  - hardcoded secrets;
  - missing input validation;
  - missing CSRF/XSS protections;
  - logging of sensitive data;
  - missing rate limiting on auth and destructive endpoints.

Required output format from the Security Reviewer (JSON, validated by the Orchestrator):

```json
{
  "findings": [
    {
      "id": "F1",
      "file": "exact/path/to/file.ext",
      "line_range": [12, 18],
      "category": "broken-authorisation",
      "severity": "critical | high | medium | low",
      "title": "short technical title",
      "plain_language_description": "one or two sentences explaining the risk in non-technical terms",
      "evidence": "the exact lines or pattern that exhibit the risk",
      "suggested_fix_approach": "one sentence describing the kind of fix needed (not the code)"
    }
  ],
  "scope_notes": "what was reviewed and what was not"
}
```

If the Security Reviewer cannot produce valid JSON, retry once with a stricter prompt; if it fails again, abort the pipeline and surface the failure to the user. Do not proceed with malformed input.

### Phase 2 - Orchestrator

Goal: filter, prioritise, translate, and present findings to the user, then collect approval to fix.

Operate inline (not via subagent) on the JSON output from Phase 1.

1. Validate the JSON against the schema above. If invalid, return to Phase 1 retry.
2. Drop findings of severity `low` unless the cumulative count of `low` findings exceeds 5 or any `low` finding affects an authentication or authorisation pathway. In the latter case, escalate to `medium`.
3. Group findings by file.
4. Sort within each group by severity (critical → high → medium → low).
5. Present to the user as a numbered list, one finding per line, formatted exactly as:

```
[severity-emoji] N. [plain_language_description]
   File: <file>:<start_line>-<end_line>
   Suggested approach: <suggested_fix_approach>
```

Severity emoji: critical = 🔴, high = 🟠, medium = 🟡, low = ⚪.

6. After the list, ask the user a single question: "Which of these would you like me to fix? (default: all critical and high)". Wait for the user's response. Acceptable answers: "all", "all critical and high" (or empty answer = same), a comma-separated list of finding IDs (e.g., "F1, F3"), or "none".
7. Hand off the approved finding IDs to Phase 3.

### Phase 3 - Developer

Goal: apply the smallest safe fix per approved finding, verify behaviour, and commit following the rules in the `slice-execution` skill.

For each approved finding, in severity order:

1. Read the exact lines referenced by the finding.
2. Apply the smallest fix that addresses the finding, following the simplest-solution-that-works constraint from *Architecture Selection* in `AGENTS.md` (no rewrites, no opportunistic refactors).
3. Run the application manually per the manual testing instructions in `slice-execution` to verify no behavioural regression. If a regression is detected, revert the fix per `slice-execution`'s recovery rule and mark the finding as `unfixed-due-to-regression` for the final summary; do not attempt a second fix.
4. Commit per `slice-execution`'s commit-message rules with the message `fix(security): <plain_language_description>`.

After all approved fixes are applied, produce a final summary to the user:

- N critical findings → fixed
- N high findings → fixed (or unfixed-due-to-regression, with reasons)
- N medium findings → deferred (with reasons)
- N low findings → deferred (with reasons)
- Recommendation: re-run `security-review-pipeline` after the next feature slice if any auth, authz, sensitive-data, or destructive-action slice is added.

## Limitations (state explicitly to the user at the start)

This pipeline is itself an LLM-based tool. It will not catch all vulnerabilities and may produce false positives. It is best understood as a risk-reduction measure, not a security guarantee. Per the Expert Escalation policy, an experienced developer should review the application before it is used with real users, real data, or real money, even if this pipeline reports zero findings.

## Fallback for environments without subagent support

If the host tool does not support Superpowers `requesting-code-review` or subagent dispatch, execute Phases 1-3 inline as a single pass, using internal role-prompting to maintain the analysis/remediation separation. Document this as a degraded mode.
