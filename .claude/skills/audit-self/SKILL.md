---
name: audit-self
description: Use when the user asks for a status check on SPEC and ADR discipline — "where are we", "audit", "check the SPEC", "is everything tracked", "what's missing", "did you forget to update anything". Always manually invoked; never auto-runs.
---

# Self-Audit

Verify that the session's work has left the durable artefacts the Virgilio rules require: SPEC progress markers updated, Open Questions closed when resolved, ADRs written when triggered, deferred items materialised somewhere persistent.

This skill is a **check, not a fix**. It produces a report; the user (or a follow-up turn) decides what to act on.

## When To Use

Invoke when the user asks any of:

- "where are we?"
- "audit" / "check"
- "check the SPEC"
- "is everything tracked?"
- "what did we leave undone?"
- "did you forget to update anything?"
- "what's missing?" / "give me the audit"

The agent recognises the trigger regardless of the user's natural language (Italian, German, Spanish, etc.) — the phrases above are English samples, not an exhaustive list.

Do NOT invoke automatically without one of the above triggers. The audit is an information request, not a workflow gate.

### Project Type Independence

This audit applies regardless of project type: web apps, native mobile (Expo), CLI tools, API-only services, libraries, scripts. The four checks operate on SPEC.md, ADRs, commit history, and code comments — none of which are UI-specific. On a project without a visible UI (e.g., a CLI tool), the "UI Design Gate skips" limit listed below is simply not applicable (there are no UI gates to skip).

## The Four Checks

Run each check against the current project state. Classify each finding as:

- **✅ in order** — the discipline is respected
- **🟡 suspect / verify** — might be a false positive; user judges
- **⬜ chiaramente missing** — clear gap, action recommended

### Check 1 — SPEC section 4 (Core features) markers vs reality

Open `SPEC.md` section 4. For each bullet:

1. Does it have a leading marker (✅ / 🟡 / ⬜)? If not, that bullet violates the `spec-coauthor` Core Features Progress Markers rule → ⬜.
2. Cross-reference the marker with recent commits (`git log --oneline -30`):
   - Marker ✅ but no commit message in the last 30 mentions the feature → 🟡 (might be old work the user knows about; might be a forgotten marker).
   - Marker ⬜ but a recent commit appears to have shipped the feature → 🟡 (probably a forgotten update; recommend ✅).
   - Marker 🟡 → list the partial parts mentioned so the user sees what's still pending.

Be specific: cite the bullet's text and the commit hash you cross-referenced.

### Check 2 — SPEC section 13 (Open questions) closure

Open `SPEC.md` section 13. For each entry:

1. Is the question literally still open in the user's mind, or has a decision in this session (or recent commits) actually answered it?
2. If the conversation has clearly decided something that answers an open question: 🟡 (recommend moving the entry per the Open Questions Lifecycle rule — into the appropriate downstream section + logged in section 12).

Entries that genuinely remain unanswered → ✅. Entries clearly resolved but still in section 13 → 🟡. Entries no longer relevant due to a project pivot → ⬜ (recommend marking `obsolete (reason)`).

### Check 3 — ADR triggers without ADRs

Run `git log --oneline -30`. For each commit, check whether the work matches one of the ADR triggers listed in `AGENTS.md` § Architecture Selection:

- Data schema affecting 2+ tables
- State machine / lifecycle
- Security pattern across 2+ tables or 2+ endpoints
- URL or routing structure
- Deferred decision with visible debt
- Choice conflicting with documented default
- Workflow state model beyond a single screen
- Third-party SDK or service category

For each commit that looks like one of the triggers, check whether a corresponding ADR exists in `docs/adr/`. If not:

- Clear match → ⬜ (recommend writing the ADR now).
- Ambiguous match → 🟡 (ask the user whether to write the ADR).

Cite the commit hash and the trigger category it matches.

### Check 4 — Deferred items persistence

Scan recent commits AND the current conversation context for deferral phrases:

- "we'll do this later" / "lo facciamo dopo" / "rimando a"
- "deferred to slice X" / "to be done in <name>"
- "later" / "after launch" / "post-MVP"
- "stub for now" / "placeholder"

For each deferral, check whether it is materialised in at least one of:

- An entry in SPEC section 4 with 🟡 marker referencing the deferred work
- An entry in a SPEC "Deferred items" subsection (if it exists)
- A `// TODO(slice-X): <description>` or equivalent comment in the code

Materialised → ✅. Announced but not materialised → ⬜ (recommend adding the trace in one of the three locations).

## Output Format

Produce a single structured report in plain language. Template:

```
Virgilio audit — <today's date>

**SPEC section 4 (Core features)**
- ✅ X bullets with marker aligned to recent commits
- 🟡 Y bullets with marker to verify: [list with citations]
- ⬜ Z bullets missing a marker: [list]

**SPEC section 13 (Open questions)**
- ✅ X questions legitimately still open
- 🟡 Y questions probably resolved but not moved out: [list]

**ADR triggers (last 30 commits)**
- ✅ X commits that didn't require an ADR
- 🟡 Y commits ambiguous (verify): [list with commit hashes + trigger category]
- ⬜ Z commits that clearly required an ADR per trigger list: [list]

**Deferred items**
- ✅ X "later" announcements materialised somewhere (SPEC / TODO / Deferred items)
- ⬜ Y "later" announcements that only exist in chat: [list]

**Recommended actions:**
1. [concrete next step the user can take, with file:line or commit hash]
2. [...]
```

Each ⬜ finding MUST cite the file:line, the bullet text, or the commit hash so the user can verify. Avoid generic prose like "consider improving SPEC discipline".

For 🟡 findings, phrase as a question to the user rather than a verdict ("Open question 3 says 'logo to be decided'; in this session we agreed on the Mettler-inspired direction. Should I move that entry to ADR-0002?").

## Honest Limits

What this audit does NOT check (deferred to a future, comprehensive version):

- **UI Design Gate skips.** Detecting "first detail page" or "first admin shell" patterns in commits requires code-structure analysis. Not in this lite version.
- **Coherence Loop declarations.** Verifying the agent declared "spec/design/tech remain coherent" after each change requires parsing the entire conversation. Fragile and out of scope here.
- **End-Of-Step Report quality.** Whether each report had its three fixed sections, gate sub-section listed honestly. Manual review only for now.

A clean ✅ across the four checks DOES NOT mean Virgilio's discipline was perfect in this session — it means *these four checks* didn't catch a visible gap. Treat the report as a sanity tool, not as a final quality gate.

## Anti-patterns

- Running the audit silently and not reporting because everything is ✅. The user asked for a check; they get one even if it's clean.
- Auto-running the audit at "end of session" without a user trigger. The skill is invoked only on explicit request.
- Producing a wall of complaints. The output should fit on one screen and lead with concrete next steps, not with criticism.
- Cycling: an audit that flags a deferral, the user materialises it, the next audit re-flags it as still missing because the agent didn't re-read the file. After fixing, re-run the audit only if the user asks.
