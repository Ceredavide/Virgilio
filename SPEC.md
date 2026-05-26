# Virgilio

**Last updated:** 2026-05-14
**Status:** draft

> This SPEC describes Virgilio itself — the specification-first layer for non-programmers that runs on top of `obra/superpowers`. Virgilio is the tool, not an app built with it. This file dogfoods Virgilio's own rule: even a developer tool should be readable and approvable by the people who will actually use it.

## 1. What it is

Virgilio is a configuration package for AI coding agents (Claude Code, Codex, and compatible tools) that forces a specification-first, slice-by-slice workflow when a non-programmer asks the agent to build an app. It adds product-level skills, plain-language conversation rules, and safety hooks on top of `obra/superpowers`.

## 2. Who uses it

- **Primary user:** a non-programmer using an AI coding agent to build a real application. They can read product decisions but should not be asked to evaluate technical details.
- **Secondary user:** a developer who maintains a Virgilio-based project, or who installs Virgilio into a non-programmer's workspace.

## 3. Main device and usage context

- **Device:** desktop terminal running an AI coding agent.
- **When it is used:** during agent sessions, whenever the user is creating, extending, or fixing an application.
- **Connection:** always online (the agent is online).

## 4. Core features (current scope)

- A user can describe an app idea in plain language and the agent will refuse to write app code until the specification exists and is confirmed.
- A user can open an existing codebase and the agent will infer a draft specification before proposing changes.
- A user can ask for a feature and the agent will deliver one small visible slice at a time, run it locally, give explicit testing steps, and commit.
- A user is never asked technical Git questions; the agent translates branches, worktrees, and commits into product-level choices.
- A user can request a security review and the agent runs a three-role pipeline appropriate for non-programmers.
- A user can ask "why is this broken?" and the agent investigates one cause at a time before changing code.

Out of scope right now:

- Auto-deployment to production.
- Multi-developer collaboration features.
- A graphical installer or UI.
- Support for agents that do not expose a PreToolUse hook mechanism.

## 5. Key user flows

### Flow: build a new app from scratch

1. The user describes the app idea to the agent.
2. The agent invokes the spec-coauthor skill and writes the specification together with the user, asking product questions only.
3. The agent confirms the primary device and usage context.
4. The agent invokes the ui-ux-coach skill for screen and flow design.
5. The agent initializes Git and commits the spec.
6. The agent implements one slice, runs the app locally, hands the user a clear test script, and commits.
7. The user decides what to do with the slice (main version, preview, throw away).
8. Repeat from step 6 for the next slice.

### Flow: continue an existing project

1. The user opens a project that already has app files but no specification.
2. The agent invokes the existing-project-onboarding skill, inspects the repo, writes a draft specification from the observed behavior.
3. The user reviews and confirms the spec.
4. From here, the new-app flow continues from step 5.

### Flow: something is broken

1. The user reports an error or unexpected behavior.
2. The agent invokes the troubleshooting-guide skill, investigates, explains the likely cause in plain language, and proposes one targeted fix.
3. The agent applies the fix, tells the user exactly how to retest, and commits if the test passes.

## 6. Data the app remembers

Virgilio itself does not store user data. The artifacts it produces live inside the user's own project:

- The specification document at the project root — the source of truth.
- Architectural Decision Records under the docs folder, for material decisions.
- A virgilio support folder, for temporary visual or product sketches that are not application code.
- A virgilio onboarding folder, populated when onboarding an existing project.
- Git history — every working slice is a commit with a plain-language message.

## 7. What it does not do

- It does not run the agent. The user still needs an AI coding agent.
- It does not deploy applications.
- It does not write code that bypasses Superpowers' engineering disciplines.
- It does not expose Git, branch, or worktree mechanics to the user.
- It does not enforce a particular framework, language, or stack — it enforces workflow, not technology.

## 8. Look and feel

Virgilio has no user interface of its own. The "look and feel" is the conversation style of the agent:

- **Tone:** patient, plain-language, product-focused.
- **Style:** no jargon, no Git terminology, no test-framework terminology shown to the user unless asked.
- **Decisions:** lettered choices (A/B/C) framed as product trade-offs, with a recommended default.

## 9. Quality bar

- Every user-visible change must be committed and runnable locally before the next slice begins.
- Hooks must block app-code edits when the specification is missing or Git is not initialized, on every supported harness.
- Canonical files (skills, identical hooks) must live in a single place; other locations are symlinks. Edits should not require synchronizing copies.
- Skill definitions must use plain-language descriptions a non-programmer can understand.
- The Claude and Agents instruction files should stay aligned; meaningful drift is a bug.
- Templates must be usable as starting points without further editing.

## 10. Risks and expert review

Virgilio is a thin layer. The serious risks come from the apps users build with it. The agent must surface those risks proactively when a slice touches:

- Authentication, account recovery, or session management.
- Payments and billing.
- Personal or sensitive data.
- Production deployment.
- External integrations that handle money, identity, or compliance.

When in doubt, the agent must recommend an experienced developer review the work before real users are exposed to it.

## 11. Open questions

- Should Virgilio ship a real installer (one command) instead of a manual copy-paste setup?
- Should the spec-validator hook be refactored into a shared library used by both the Claude and Codex variants?
- Should there be a starter-pack template for common app types (CRUD web app, mobile-first PWA)?
- How should Virgilio evolve when Superpowers changes its public skill names or contracts?

## 12. Change log

- 2026-05-14 — first draft.
- 2026-05-21 — relaxed UI Design Gate: declared-intent + one-question check is enough for extensions that re-use the approved visual language; full 2-3 directions reserved for new visual patterns.
- 2026-05-26 — started mobile track extension. Mapped which skills assume web behavior so the upcoming changes stay small and focused.
- 2026-05-26 — mobile-ready skill set: testing instructions, design patterns, troubleshooting, backend notes, and the Manual Testing Gate now cover native mobile (Expo) alongside web.
- 2026-05-26 — added a mobile publishing checklist that maps the walls between an Expo app and a real user's phone (developer accounts, certificates, store listings, privacy disclosures, review process), and routes each wall to the type of expert that closes it. The existing pre-publishing checklist now dispatches to this new one automatically when the app is mobile.
- 2026-05-26 — extended the experimental baseline with two mobile scenarios and four mobile probes, and added a participant debrief script (later moved into the thesis document) to capture the cost-decision data point for RQ3.
- 2026-05-26 — added an install CLI (`cli/`): users can now install Virgilio with `npx @ceredavide/virgilio init` instead of copying files by hand from the repo. Two commands (`init`, `update`), both auto-detect fresh vs existing projects and install for Claude Code and Codex by default. README explains the companion setup (GitHub-login accounts, Superpowers, MCP servers).
- 2026-05-26 — repo cleanup: development documents (design proposals, baseline scenarios, debrief script, exploration findings) moved out of the repo into the thesis document, so the repo focuses on the tool + CLI + user-facing documentation. The development history remains in Git commit history for anyone who wants it.
- 2026-05-26 — hardened SPEC and ADR discipline based on field-session feedback: explicit ADR trigger list added to Architecture Selection (data schemas spanning multiple tables, state machines, RLS patterns, routing structure, deferred decisions, third-party SDK choices); spec-coauthor gained an Open Questions Lifecycle rule (resolved questions get moved out of section 13 and logged), a Core Features Progress Markers rule (✅/🟡/⬜ updated after every slice that touches a Core feature), and a SPEC Cross-Section Reconciliation rule (after edits to section 4 or 5, re-check 6/9/11/12 and declare the outcome); backend-setup now requires writing `supabase/migrations/*.sql` files to the repo after every `apply_migration` MCP call, so the schema survives even if the Supabase project is lost.
- 2026-05-26 — second discipline round (13 more rules from the same feedback): slice-execution gained Rapid Sequence Mode, a Pre-Slice Scope Question, a "declared fallbacks must be exercised" rule for manual tests, recovery instructions after routing restructure, mandatory `npm run build` before slice completion, and persistence of "we'll do this later" promises into SPEC or code TODOs; ui-ux-coach now declares its visual tooling capability at project start, fetches user-named references before proposing design directions, treats standalone HTML as the primary fallback when frontend-design is unavailable, and has concrete examples per pattern-classification category; AGENTS.md expanded the End-Of-Step Report to three fixed sections (what changed / what was verified / gates declared, skipped, deferred), tightened the Affirmative-Response rule with a corollary on unseen decisions, and added concrete TaskCreate triggers; backend-setup tagged Provisioning Walkthrough as fallback-only and documented the database-types single-source-of-truth choice; spec-coauthor gained a Triadic Decomposition pattern for overlapping concepts; coherence-loop now requires an explicit declaration in chat after every Idea/Design/Tech change; the backend-ready-check hook recognizes both modern Supabase publishable key names and the `sb_publishable_*` value pattern.
