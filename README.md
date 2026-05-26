# Virgilio

Virgilio is a **specification-first layer for non-programmers** built on top of [`obra/superpowers`](https://github.com/obra/superpowers).

Superpowers gives the AI agent the *engineering discipline* (TDD, debugging, planning, code review). Virgilio adds the *user-facing workflow* on top: it forces the agent to start from a clear specification, to work in small visible slices, to translate technical choices into product language, and to never edit application code before the project is properly defined and Git is initialized.

If you are a developer, you probably want Superpowers directly.
If you are a non-programmer trying to build a real app with Claude Code or a compatible agent, this is for you.

## What you get

- **A specification document as the source of truth.** No code is written until it is confirmed.
- **One small slice at a time.** Each feature is built, tested in the browser, and committed before the next one starts.
- **Plain-language conversation.** No branches, no worktrees, no TDD jargon shown to the user — only product-level questions.
- **Safety hooks.** Pre-tool hooks block edits to app code if the specification is missing or Git is not initialized, on both Claude Code and Codex.
- **Five user-facing skills:** spec-coauthor, existing-project-onboarding, ui-ux-coach, troubleshooting-guide, security-review-pipeline.

## Relationship with Superpowers

Virgilio does **not** replace Superpowers. It cooperates with it:

| Layer        | Role                                                                    |
| ------------ | ----------------------------------------------------------------------- |
| Superpowers  | Internal engineering discipline (TDD, debugging, plans, code review)   |
| Virgilio     | User-facing workflow, product language, spec-first rules, safety gates |

If the two ever disagree on a user-facing behavior, the Virgilio rule wins. Superpowers terminology (branches, worktrees, TDD steps, subagents) is kept behind the scenes unless the user asks.

## Repository layout

The repository is organized so that each piece of configuration has a single canonical location. Other locations are symlinks that point to the canonical file, so a single edit propagates everywhere.

- The Claude folder holds the canonical skills and hooks.
- The Agents folder is a thin pointer to the Claude skills.
- The Codex folder holds Codex-specific configuration, plus a pointer to the shared Git-readiness hook. Only the Codex-specific spec validator is kept as a separate file because it parses a different tool-input payload format.
- The templates folder holds the starter specification and the Architectural Decision Record template.

### A note on duplication

- Skills are stored once in the Claude folder; the Agents folder is a symlink. Edit the file once and both harnesses see the change.
- The Git-readiness hook is identical for Claude Code and Codex, and is also a symlink.
- The specification validator is intentionally *not* deduplicated: Claude Code and Codex send different tool-input payloads (Write or Edit versus apply patch), so each version handles its own format. Keep both in sync when changing detection logic.
- The Claude and Agents instruction files are near-duplicates with a few harness-specific lines. Keep them aligned when editing.

## Requirements

Virgilio is a configuration layer for an AI coding agent. It is not a standalone tool. You need:

- **Claude Code or a compatible agent** (Codex with hook support also works).
- **[`obra/superpowers`](https://github.com/obra/superpowers) installed in the agent — required, not optional.** Virgilio delegates engineering disciplines to Superpowers skills: `brainstorming`, `frontend-design`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `using-git-worktrees`. Without Superpowers, the spec-first hooks still block unsafe writes, but the visual companion, structured design and review flows that Virgilio prescribes will fail. Install Superpowers first.
- **Python 3 and Git** on the machine running the agent. Both are used by the safety hooks and the checkpoint workflow.

## Install

Virgilio is meant to live inside the project you are working on, not as a global install.

In the folder where you want to use Virgilio, run:

```bash
npx @ceredavide/virgilio@1.0.0 init
```

This works in both an empty folder (new project) and a folder that already has application code (Virgilio is added alongside without touching your existing files). The CLI installs the safety hooks and the skills, leaves your `SPEC.md` to be written by the agent during the first session, and prints next-steps for installing Superpowers and the MCP servers (see `cli/README.md` for the full companion setup).

To update an existing install later: `npx @ceredavide/virgilio update` — only Virgilio's own files are replaced; your `SPEC.md`, source code, Git history, and any custom content inside `.virgilio/` are preserved.

Then open the project in Claude Code (or your Codex-compatible agent). The hooks activate automatically.

### Manual install (fallback)

If you cannot use `npx` for some reason, copy these files and folders from this repo into your project's root: `.claude/`, `.agents/`, `.codex/`, `CLAUDE.md`, `AGENTS.md`, `templates/`. **Do not copy `SPEC.md` or `README.md`** — those describe Virgilio itself, not the app you are building. If you copy `SPEC.md` along, the hooks will think your project is already specified and stop blocking unsafe code writes.

## How a session typically goes

1. You describe the app you want.
2. The agent invokes the spec-coauthor skill and writes the specification with you, asking only product-level questions.
3. The agent confirms the main device and usage context, then asks the ui-ux-coach skill to sketch screens.
4. Git is initialized. The hooks now allow app-code edits.
5. The agent builds one feature slice end-to-end, runs the app locally, gives you exact testing instructions, and commits.
6. You decide whether to keep it as the main version, keep it as a preview, or throw it away.
7. Repeat for the next slice.

If the project already contains code, step 2 is replaced by the existing-project-onboarding skill, which infers the current behavior and drafts a specification from it before any change is proposed.

## User guide

For a longer walk-through of what to expect during a session — how to answer Virgilio's questions well, what each recurring choice means, what Virgilio will refuse to do, and when to call a real programmer — read the user guide. Available in three languages:

- [English](docs/user-guide.md) (primary)
- [Italiano](docs/user-guide.it.md)
- [Deutsch](docs/user-guide.de.md)

## Status

Early-stage. Expect rough edges. Feedback and issues welcome.
