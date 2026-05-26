---
name: slice-execution
description: Use this when starting, building, or completing a single user-visible feature slice after SPEC.md is confirmed. Covers slice decomposition examples, commit-message style, end-of-slice product question, manual testing instructions, scope splitting, and recovery when a fix fails.
---

# Slice Execution

Guide the agent through one user-visible feature slice — from picking what counts as a slice, through building and testing it, to closing it with the right product-language question.

## When To Use

Use this skill when:

- `SPEC.md` is confirmed and the agent is about to start work on a single slice;
- the user describes a multi-feature request that needs to be split;
- a slice has just been built and the agent is preparing the manual testing instructions or the end-of-slice question;
- a fix during slice work has failed and recovery is needed.

## Rapid Sequence Mode

When the user signals they want to move fast — "let's do a bunch of slices today", "implement everything, you decide", "go go go" — the agent does not silently obey by skipping gates. Instead, the agent proposes Rapid Sequence Mode explicitly:

> *"Rapid Sequence Mode: one slice per turn, no parallel work, brief check-ins (1-2 sentences on what to test), safe defaults applied without asking on UX choices that re-use approved patterns. Pattern-new design gates and manual testing gates remain mandatory. Git commit between every slice. Mode ends on explicit request or when a test fails."*

If the user agrees, the agent applies the rules above. If the user declines, the standard one-slice-with-full-gates flow continues.

The mode is a way to honour "let's go fast" without honouring "let's skip safety". Slices stay independently revertable; gates stay where they protect the user from invisible regressions.

## What Counts As A Slice

A slice is a thin vertical piece — data, logic, and user-visible behavior for one feature.

A slice should deliver a recognizable mini-feature the user would describe as "a thing the app can now do", not just an internal step toward one. Prefer one coherent flow over isolated tiny changes. The user should be able to understand a slice's purpose without being told which future slice will complete it.

### Good slice

- A user can create a shared group, add members, and record the first expense in it.

### Too small

- A button label changes.
- A saved item appears only in activity history.
- A state exists but cannot yet be acted on.
- A user can add an expense but cannot yet see the result.

### Upper bound

When a feature naturally requires 3-6 tightly connected steps to feel useful, implement them in the same slice, as long as the result can still be tested clearly and safely. As a practical upper bound, a slice should remain small enough that a non-programmer can manually test it in roughly 2-3 minutes following the instructions you provide. If the test would take longer, split the slice.

### Can-break-independently rule

If two pieces of behavior inside the same slice can break independently of one another — one works while the other does not — they are two slices, even when they feel conceptually close. Login and logout, signup and password reset, "add a member" and "remove a member" fall on opposite sides of this rule.

### File-count heuristic

When a slice you are planning would touch more than three component files plus one server action plus one server-side query, treat that as a signal to consider splitting. Not a rule, a reflection trigger: it usually means the slice covers several distinct user-visible behaviors that could be tested and committed independently.

### Reporting

When reporting progress, describe each slice in terms of user-visible functionality, such as "a user can now add an expense and assign it to a group", rather than technical units like "implemented the expenses controller and migration".

## Scope Splitting

If the user's request contains multiple independent features, split it into small user-visible slices:

```text
This request contains several parts. To keep the project stable, we should build and verify one part at a time.
```

Then recommend the first slice in plain language. Do not implement multiple large features in one session.

## Pre-Slice Scope Question

When a slice's "complete" state can reasonably mean either of two things — for example:

- v1 minimal: only the core flow, no placeholders for sibling features yet;
- v1 with visual placeholders: core flow plus stub sections for upcoming features;

the agent MUST ask the user at the START of the slice, before writing any code:

> *"This slice can land in two shapes:*
> *(a) the minimal version of `<feature>` only;*
> *(b) the minimal version of `<feature>` plus visual placeholders for `<sibling features>`.*
> *Which one do you want for this slice?"*

Asking after the user has seen a partial result is the most common cause of slice rework (the agent builds (b), the user wanted (a), 20+ minutes lost to rollback). The question costs one turn at the start; the alternative is a rebuild.

## Manual Testing Instructions

After implementing a user-visible change, run the app locally when possible and provide concrete testing instructions.

Include when possible:

- the local URL;
- what page to open;
- what action to perform;
- what result to expect;
- what error or behavior to report if it fails.

Do not only say "test it". Tell the user exactly what to test. Do not ask the user to run CLI commands unless there is no reasonable alternative.

Example (web):

```text
To test this:
1. Open http://localhost:3000
2. Click "Create account"
3. Enter an email and password
4. Confirm that you see the dashboard
Expected result: the account is created and you are redirected to the dashboard.
```

### Mobile testing variant

When the project's primary device is native mobile (Expo), the Manual Testing Gate cannot rely on a local browser URL. Adapt the format:

- **How to open the app.** Default path is Expo Go (free, no native build required). Tell the user to scan the QR code printed by the dev server with the Expo Go app on their phone. Alternatives: open the iOS simulator (macOS host only) or the Android emulator.
- **Actions.** Use **tap** / **swipe** / **long-press** instead of "click". Reference UI elements by their visible label or icon, not by mouse position.
- **Expected result.** Frame for a phone screen: "the dashboard opens" rather than "you are redirected to the dashboard".
- **If Expo Go disconnects** from the dev server during the test, ask the user to kill Expo Go and re-scan the QR. This is the single most common mobile testing hiccup and is not a code bug.

Example (mobile):

```text
To test this:
1. Open Expo Go on your phone
2. Scan the QR code shown in the terminal
3. When the app loads, tap "Create account"
4. Enter an email and password, then tap "Continue"
5. Confirm that the dashboard appears
Expected result: the account is created and the dashboard opens.
If Expo Go shows "no connection", close it and scan the QR again.
```

Keep both example formats (web and mobile) available — pick the one that matches the project's primary device (decided during `spec-coauthor` and recorded in `SPEC.md`).

### Declared Fallbacks Must Be Exercised

If the slice ANNOUNCES a fallback behaviour to the user — for example "cards automatically fall back to Italian if the requested locale is missing", "deleted records are soft-archived not erased", "the form sends an email but also stores it in the inbox if email fails" — the manual testing instructions for that slice MUST include a concrete step that exercises the fallback path, not only the happy path.

Announcing a fallback without testing it is a false promise: the fallback may not actually work, and the user only discovers this in production when the happy path fails.

## Pending References

If a slice introduces a reference (link, route, form field, consent checkbox) to something that does not exist yet, record it in `SPEC.md` under a section called `### Pending References` with the future slice that will resolve it, and mention it explicitly in the End-Of-Step Report.

Example: a checkbox "I have read the privacy policy" linking to `/privacy` is fine to ship, as long as the missing destination is tracked and reaches a real page before the app goes public.

The user must know what the app is currently promising to a visitor before that promise is honored.

## User Consent Gate

If a slice introduces a user consent affordance (a checkbox like "I have read the privacy policy", "I accept the terms", a cookie banner with a consent action, a marketing opt-in), apply a stricter sub-gate before committing:

1. **Destination exists.** The page or document linked from the consent (privacy, terms, cookie info) must already exist in the project. If it does not, either ship a placeholder destination first as a separate slice, or record both the consent and the missing page in `SPEC.md` § *Pending References* and explicitly call out the gap in the End-Of-Step Report as known legal debt.

2. **Consent text approved.** The wording the user is asked to agree to must have been explicitly approved by the user, not generated by the agent and silently shipped. AI-default phrasing on a binding consent is a reputational and legal risk; see also *Expert Escalation* in `AGENTS.md`.

If either check fails, do not present the slice as "done". Either ship a smaller version without the consent affordance, or propose the slice that closes the gap first.

## Financial and Algorithmic Math

If the slice implements financial or algorithmic logic (sums, divisions, percentages, rounding, comparative balances, settlement algorithms, scoring), invoke `superpowers:test-driven-development` for that logic. Write failing tests for the math before implementing it. This is non-optional regardless of slice size.

Manual testing alone is fragile for this kind of code: a wrong-but-fluent result (off-by-one, wrong rounding direction, asymmetric balance, swapped operands) can pass visual inspection while being silently broken. Tests for the math layer are an internal safeguard; the user still receives only the user-facing testing instructions.

## Commit Messages

Commit messages must describe what the user can now do, not which files changed.

Good:

```text
A user can add an expense to a group
```

Bad:

```text
Update components and routes
```

## Recovery Rule

If a change breaks an existing feature, attempt at most one targeted fix. If the first fix fails:

- stop;
- return only the current slice changes to the last known working version;
- explain the issue simply;
- choose a smaller next step.

Never revert unrelated user changes.

### Recovery After Routing Restructure

Restructuring the routing layer — adding a dynamic segment (`[locale]/`, `[id]/`), moving a route's directory, renaming a layout file — breaks the dev server's hot reload in ways that look like application bugs. The user will see stale cache, missing routes, or 404s that survive a page reload.

Recovery after a routing restructure:

1. Stop the dev server (`Ctrl-C` on the terminal running `npm run dev`).
2. Delete the framework's build cache (`rm -rf .next` for Next.js, `rm -rf .expo` for Expo, equivalent for other frameworks).
3. Restart the dev server.

The agent MUST document this sequence in the manual testing instructions whenever the slice modified the routing layer. The user does not know that "kill dev + clear cache" is a thing; if not told, they will report the symptom as a bug and the slice will lose half an hour to false diagnosis.

## End-of-Slice Build Verification

Before declaring a slice "complete", run the project's production build:

- web (Next.js, Astro, Vite, …): `npm run build`
- mobile (Expo): `npx expo export` or the equivalent prebuild
- other frameworks: the equivalent production build command

`npm run dev` (or its mobile equivalent) does not exercise the same code paths as the production build. Strict-mode type errors, server-component constraints, import cycles, optimisation edge cases — these surface only at build time. Skipping this step ships a slice that may break the moment the user tries to deploy.

Report the build outcome in the End-Of-Step Report: "production build passed" or "build failed (reason)". Do not mark the slice "complete" on a failed build — either fix the issue or roll back via the Recovery Rule.

## Deferred Items Persistence

Every time the agent says to the user "we'll do this later" — for example "email notifications will arrive with Resend later", "the admin messages section will arrive in slice 14", "file uploads later, URLs for now" — the agent MUST materialise that deferral in at least ONE persistent location:

- an entry in `SPEC.md` Core Features (section 4) with the 🟡 partial marker;
- an entry in a `SPEC.md` "Deferred items" subsection (create the subsection if absent);
- a `// TODO(slice-X): <description>` comment in the code that depends on the deferred work.

A "we'll do this later" announced only in chat disappears with the session. Promises must materialise somewhere the user can re-discover them next week without re-reading the transcript.

## End-Of-Slice Question

End-of-slice choices come only after:

- automated checks have passed where relevant;
- the app has been opened locally where possible;
- the user has received manual testing instructions;
- the user has confirmed the visible behavior works, or explicitly chooses to continue anyway.

At the end of a completed isolated implementation, do not ask technical Git questions. Ask product-level questions instead, choosing the closing style based on the slice:

**Soft close** — when the next step is obvious and low-risk (same pattern continuing, no new decision). One line, e.g. "Works? I'll continue with slice X (one-line description)."

**Standard close** — when the next step has more than one reasonable continuation. Use the A/B/C product-level template:

- A. Use it as the main version - this makes the new feature part of the normal app.
- B. Keep it as a separate preview - this keeps the current app unchanged for now.
- C. Throw away this experimental version - this removes the work from this slice.

**Hard close** — when the slice closes an entire phase (end of UI Design Gate, end of backend setup, end of security review). Include a deeper explanation of what was accomplished and what the next phase opens up. A/B/C/D with longer per-option context.

Pick the lightest close that fits. If the right next step is obvious and low risk, apply the safe default and explain it briefly.

## When Testing Reveals A Problem

If manual testing reveals an error or unexpected behavior, hand off to the `troubleshooting-guide` skill to diagnose and propose a fix in plain language. Stay within one slice; do not let troubleshooting expand into unrelated changes.
