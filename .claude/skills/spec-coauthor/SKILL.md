---
name: spec-coauthor
description: Use this when SPEC.md is missing, incomplete, outdated, or when a non-programmer needs help turning an app idea into a clear software specification before coding.
---

# Spec Coauthor

Help a non-programmer turn an initial application idea into a clear, plain-language `SPEC.md` before implementation starts.

This skill is part of Virgilio's specification-first workflow.

## Goal

Produce or update `SPEC.md` so that it becomes the shared source of truth between the user and the AI coding tool.

The specification should be understandable by a non-programmer and useful enough to guide implementation.

## Core Rules

- Do not write application code while using this skill.
- Do not create `SPEC.md` just to bypass a missing-spec code restriction.
- Only create or update `SPEC.md` when the user is genuinely defining an app, feature, product, or project goal.
- **Always start with a free-form brain dump from the user before asking any structured question.** The user must arrive with a concrete idea. The skill's questions exist to refine that idea, not to extract it from scratch.
- **Ask one question at a time.** Never batch multiple decision dimensions in a single turn ("Which device? And who uses it? And what tone?"). One decision per turn, wait for the answer, then move on. Lettered options (A/B/C) are still a single question when they offer alternatives for the same decision.
- Do not assume the user knows software terminology.
- Use simple language.
- Actively suggest important things the user may not know to mention — but only **after** the brain dump.
- Prefer a small first version over an oversized application.
- Make hidden complexity visible.
- If the idea is too complex or risky for a non-programmer to evaluate safely, recommend consulting an experienced developer.
- Do not include external platform integrations such as deployment or managed database workflows in v1 unless the user explicitly asks.
- Exit this skill only when the user has explicitly confirmed the specification (see Exit Criterion below).

## When Not to Create SPEC.md

If the user asks for a tiny code artifact without describing an app, do not invent a minimal specification.

Examples:

- "create a basic component"
- "make a simple page"
- "add a button"
- "give me a small code example"

In this situation:

1. Do not write project files.
2. Explain briefly that Virgilio needs a real project specification before changing app files.
3. Offer to help create a proper `SPEC.md` if this is part of an app.
4. If the user only wants an example, provide a short educational snippet in chat without editing files.

## Existing Projects

If `SPEC.md` is missing but the repository already contains application files, do not start from a blank product interview. Use the `existing-project-onboarding` skill first to infer what the project already does, then use this skill to confirm, correct, and complete the resulting draft specification with the user.

## Process

The skill follows five phases in order. Do not jump ahead.

### Phase 1 — Brain Dump (always first)

Ask the user to describe, in their own words and in as much detail as possible, what they want to build. Do **not** ask structured questions yet. Do not present options. Do not propose a stack.

Use one open prompt, in plain language. Example:

```text
Before I ask anything specific, write everything you have in mind about the app you want to build. Be as detailed as possible. You can include:
- what the app does
- who will use it
- why it is useful
- how you imagine it working
- anything it should not do
Don't worry about order or completeness. We will refine together.
```

If the user is stuck or sends only one short sentence, gently prompt with the bullet list of hints above, but do not turn it into a questionnaire. The goal is to let the user pour out everything they have first.

Read the brain dump carefully. Extract every fact the user already gave you so you do not ask it again.

### Phase 2 — Mandatory Coverage Check

There is a small set of decisions that any application specification must cover, regardless of the type of app. After the brain dump, the skill must ensure each of the following is answered. If the brain dump already answers a point, mark it as covered and move on. If not, ask **one question at a time** to fill the gap.

Mandatory coverage:

- **Primary device.** Desktop web, mobile web, native mobile (Expo), app-script / extension, or a combination. This decision drives every later UI choice.
- **Authentication model.** No login at all, single-owner account, email + password, magic link, OAuth (Google / Apple / GitHub / ...), or invite-only. "No login" is a real choice and must be confirmed explicitly.
- **Privacy / who-sees-what.** Single-user data, shared groups, multiple roles (admin / member / viewer), or fully public. Confirm explicitly even when it seems obvious.
- **Data persistence.** No persistence (in-browser only), local-only, cloud-backed, or external service. If cloud-backed, surface options such as Supabase as a non-programmer-friendly default.
- **Sensitive data or payments.** Does the app store anything personal, financial, health-related, or otherwise sensitive? Does it move real money? Yes/no, and if yes, list the categories. This triggers the Pending External Review entries (see Phase 4).
- **Expected scale.** Roughly how many real users does the user expect: 10, 1 000, 100 000? This shapes hosting and architecture choices.

Each gap is asked as one question, with A/B/C/D options where it helps, plus a recommended default explained in plain language.

### Phase 3 — Contextual Coverage Check

These decisions matter only for some apps. Trigger each one only when the brain dump (or Phase 2 answers) suggests it is relevant. Do not ask all of them by default.

Contextual coverage (ask only if hinted):

- **Offline usage.** If the user mentioned travel, low connectivity, or "use it without internet".
- **Push or email notifications.** If the user mentioned reminders, alerts, or "notify me when…".
- **Installable as a real app.** PWA or native install, if the user mentioned home screen, app store, or icons.
- **External integrations.** Email, calendar, maps, social, file storage, payments — only if hinted.
- **Multilingual UI.** If the user mentioned other languages or international users.
- **Real-time / live collaboration.** If the user mentioned multiple people seeing changes simultaneously.

For each contextual decision that fires, ask one question at a time, with A/B/C options when useful.

### Phase 4 — Suggest, Surface, Simplify

Now that the mandatory and contextual decisions are settled, **actively suggest** anything the user did not think to mention but that a software project usually needs. Still one question at a time.

Cover:

- missing user flows;
- common screens the user did not name;
- likely edge cases;
- simpler first-version alternatives ("we can skip X for v1 and add it later");
- basic UX expectations (empty states, loading states, confirmations);
- data that may need to be stored that the user did not list;
- risks or hidden complexity;
- reasonable defaults.

If Superpowers `brainstorming` is available, use it internally to expand options, then translate the result through this skill's plain-language questions.

Whenever a decision touches sensitive scope (authentication, authorization, payments, personal data, production deployment, legal/compliance, security-critical behavior), record an entry in the **Pending External Review** section of `SPEC.md` (see Structure below). The agent can prototype these areas, but the entry must remain in the table until the user marks it reviewed.

If a visual mockup would help a UI decision, defer to the `ui-ux-coach` skill, which is responsible for invoking the Superpowers `frontend-design` visual companion. Do not generate UI mocks from inside this skill.

### Phase 5 — Confirm and Write

Summarize the agreed specification in plain language. Then ask the user a single explicit confirmation question:

```text
This is the specification we agreed on. Should I save it as the project's SPEC.md and move on to design and technology choices?
A. Yes, save it and continue.
B. Wait, I want to change something first.
```

**Exit criterion.** Only when the user picks A — explicit confirmation — write `SPEC.md` and hand off to the next phase. Picking B means stay in Phase 4 or jump back to whichever earlier phase the user wants to revise.

After saving, hand off to the Coherence Loop (see CLAUDE.md / AGENTS.md, *Coherence Loop*). The loop will reconcile idea, design, and tech with the user before any code is written. Do not start implementation directly from the saved spec — the loop's own exit criterion (user explicitly confirms idea, design, and tech together) is the gate for code.

Also remind the agent (not the user) to make sure Git is set up before any application code is written.

## Options and Trade-offs

When asking the user to choose between options, explain each option in simple language.

Prefer lettered options so the user can answer with one letter, combine options, or propose their own version.

Use 2-4 options plus an "Something else / a mix" option when useful.

For important choices, include:

- what the option means;
- pros;
- cons;
- recommended default.

Do not ask technical questions without explaining why they matter.

A lettered question is still **one** question. Do not stack multiple lettered questions in the same turn.

## Non-Programmer Decision Policy

Ask the user about product and experience decisions, not low-level technical implementation details.

Ask about:

- what the app should do;
- who will use it;
- what data matters;
- privacy expectations;
- user-visible behavior;
- deployment goals;
- important trade-offs.

Do not ask about routine technical choices such as file structure, internal refactors, imports, dependency wiring, or implementation patterns.

Choose safe and conventional technical defaults automatically.

## Automatic Best Practices

Include standard best practices in the specification unless they conflict with the user's goals.

Examples:

- form validation;
- password confirmation when relevant;
- clear password and account-recovery expectations when relevant;
- clear error messages;
- loading states;
- empty states;
- confirmation before destructive actions;
- basic accessibility;
- responsive layout;
- safe handling of secrets and environment variables.

## Expert Escalation

If the idea involves high complexity, risk, or decisions the user cannot reasonably evaluate alone, explain this clearly.

Examples:

- authentication;
- authorization;
- payments;
- personal or sensitive data;
- production deployment;
- legal or compliance concerns;
- complex infrastructure;
- security-critical behavior.

You may help define a prototype, but recommend consulting an experienced developer before using the result with real users, real data, money, or production systems.

Each escalation item must also appear in the **Pending External Review** section of `SPEC.md`, with the reason it is sensitive and the type of expert needed.

Suggested wording:

> This can be prototyped, but it has security, privacy, or production implications. Before using it with real users, you should consult an experienced developer.

## SPEC.md Structure

Use the canonical structure defined in `templates/SPEC.md`. Section numbers and titles must match the template — that is what a non-programmer will read, copy, and edit between sessions. Do not invent a parallel structure.

Sections you are particularly responsible for populating:

- **Section 9 — Security and access control.** Fill this directly from the answers collected during the Mandatory Coverage Check (auth model, who-sees-what, sensitive data categories, external services and credentials, destructive actions). If the user did not know, choose a safe and conventional default and document the choice.
- **Section 12 — Pending external review.** Add a row for every decision or feature that touches authentication, authorization, payments, personal data, production deployment, legal/compliance, or security-critical behavior. The agent must keep this table accurate across slices. The user changes the Status field manually after a real external review.

Before the user talks about "going live" or "real users", remind them of any row in section 12 still marked `pending`.

## Output Requirements

At the end of the skill:

- create or update `SPEC.md` using the structure from `templates/SPEC.md`;
- keep it readable for a non-programmer;
- avoid unnecessary technical jargon;
- ensure section 9 (Security and access control) is filled with real answers, not placeholders;
- ensure section 12 (Pending external review) exists, even if its table is empty at first;
- clearly mark risks and out-of-scope features;
- remind the agent to set up Git after the specification is confirmed and before implementation starts.

## Open Questions Lifecycle

`SPEC.md` section 13 lists Open Questions — product or technical decisions deferred at spec-writing time. Every Open Question has one of three fates over the project's lifetime:

- **Resolved.** A later conversation answers the question. The agent MUST then:
  1. Move the entry out of section 13.
  2. Update the appropriate downstream section (typically section 4 Core features, section 6 Data, or section 9 Security & access control) with the resolved decision.
  3. Add a one-line entry to the section 12 change log: *"Open question resolved: <question> → <decision>."*

- **Deferred again.** Still open after a session that touched related scope. Leave the entry in section 13 with an updated *Last touched* date so the user can see the question hasn't gone stale.

- **No longer relevant.** A project pivot makes the question moot. Mark the entry `obsolete (reason)` in section 13 with a date, and log the obsoletion in the section 12 change log. Do not silently delete.

When the user makes a decision in conversation that closes an Open Question, the agent surfaces the move explicitly:

> *"This closes Open Question N from SPEC section 13. I'll move it to section <Y> and log the resolution."*

Silent closure is worse than no closure: the user loses the trail of how the decision was reached.

## Core Features Progress Markers

`SPEC.md` section 4 lists Core Features as bullet points. As slices land, the agent MUST keep markers next to each feature:

- **✅ shipped** — slice committed, manual testing passed, end-to-end.
- **🟡 partial** — one or more sub-deliverables of the feature still pending (e.g., form built but email notification deferred).
- **⬜ not yet started** — included in scope but no slice has touched it yet.

The marker goes inline at the start of each bullet, replacing any previous marker. Example:

```
- ✅ A user can create a shared group and add members.
- 🟡 A user can record an expense (form works; balance calculation pending).
- ⬜ A user can settle up via an external payment provider.
```

Update the markers at the **end of every slice** that closes or advances a Core feature, as part of the End-Of-Step Report. This makes SPEC section 4 the user's visible-from-the-file progress dashboard — readable without opening Git or the changelog.

If a slice introduces a Core feature that didn't exist in section 4, add the bullet with the appropriate marker, not just in the commit.

## SPEC Cross-Section Reconciliation

When the agent edits SPEC section 4 (Core features) or section 5 (User flows) during a session — because the user introduces a new lifecycle, role, workflow, or visible behaviour — the agent MUST also re-check the following sections for required updates:

- **Section 6 (Data the app remembers)** — new fields, tables, relationships, or status enums?
- **Section 9 (Security and access control)** — new role, new access rule, new sensitive-data category?
- **Section 11 (Out of scope)** — does the new scope contradict an existing "out of scope" line?
- **Section 12 (Pending external review)** — any new escalation item triggered by the change?

After the cross-check, the agent declares one of two outcomes in chat:

- *"SPEC reconciled across sections 4–12."* (no further changes needed)
- *"SPEC reconciled with the following pending updates: [list]."* (changes still to apply)

Silent drift between sections is the most common SPEC quality failure observed in real sessions. The declaration in chat makes the reconciliation auditable.

## Triadic Decomposition Pattern

When the user is uncertain between two concepts that seem to overlap — "should we have Projects or Opportunities?", "do I need Leads or Customers?", "is it a Draft or a Reference?" — the agent applies the Triadic Decomposition pattern:

1. **Recognise it's a product question, not a technical detail.** The fact that two concepts overlap suggests a hidden state model.

2. **Distinguish from the end user's perspective.** Are the concepts genuinely different for the user (or for a specific sub-audience)? Sometimes yes (investors care about "Projects", buyers care about "Opportunities"), sometimes no (a "Lead" is just a Customer in an earlier state).

3. **If genuinely different, propose keeping BOTH as distinct states of a single entity with an explicit lifecycle.**

   Examples:
   - Lead → Customer → Returning customer
   - Draft → Published → Archived
   - Opportunity → Project → Case study (real estate / consultancy lifecycle)
   - Order placed → Paid → Fulfilled → Cancelled

4. **Translate immediately into the data model** so the user sees the implication: a single table with a `status` column, transitions logged.

5. **Update SPEC, the admin panel, and the public surface coherently** — the lifecycle is one decision but it ripples across multiple sections.

Field evidence: users who initially ask "A or B?" frequently respond "ah, both!" once shown the lifecycle interpretation. The decomposition turns a binary scope question into an integrated data model, and the project gains a state machine instead of two parallel concepts.
