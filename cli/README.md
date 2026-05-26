# @ceredavide/virgilio

Installer for [Virgilio](https://github.com/Ceredavide/Virgilio), the specification-first AI coding workflow for non-programmers.

## Quick install

In the folder where you want to use Virgilio:

```bash
npx @ceredavide/virgilio init
```

This works in two cases:

- **Empty folder** — Virgilio is installed and ready. The agent will write the project specification with you.
- **Existing project** — Virgilio is added alongside your existing code. The agent will read your project to understand it before proposing changes.

## Setup beyond the CLI

`npx @ceredavide/virgilio init` installs Virgilio's files into your project. To actually USE Virgilio you also need: a few free accounts, the Superpowers plugin in your AI tool, and a handful of MCP servers. Plan ~15 minutes the first time.

### 1. Accounts (do this first)

All free, all reachable with a single GitHub login:

- **[GitHub](https://github.com)** — master account. Create here first.
- **GitHub repository** for your project — create at [github.com/new](https://github.com/new), then `git clone` locally. Run the install inside the cloned folder.
- **[Vercel](https://vercel.com)** (web deployment) — "Continue with GitHub".
- **[Supabase](https://supabase.com)** (database + auth) — "Continue with GitHub".
- **[Expo](https://expo.dev)** (mobile apps, optional) — "Continue with GitHub".

For each service you'll later need an **access token**:

| Service | Token URL |
|---|---|
| Vercel | [vercel.com/account/tokens](https://vercel.com/account/tokens) |
| Supabase | [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens) |
| GitHub | [github.com/settings/tokens](https://github.com/settings/tokens) (Personal Access Token) |
| Expo | [expo.dev/accounts/[your-name]/settings/access-tokens](https://expo.dev) |

### 2. Superpowers in your AI tool

Virgilio depends on [obra/superpowers](https://github.com/obra/superpowers). Follow the install instructions in the Superpowers README for your tool (Claude Code or Codex).

### 3. MCP servers (per service)

MCP (Model Context Protocol) servers let your AI tool talk directly to Vercel, Supabase, Expo, GitHub. The same `npx add-mcp <URL>` command works on Claude Code and Codex.

| Service | Command / Documentation |
|---|---|
| Vercel | `npx add-mcp https://mcp.vercel.com` |
| Supabase | [supabase.com/docs/guides/ai-tools/mcp](https://supabase.com/docs/guides/ai-tools/mcp) |
| Expo | [docs.expo.dev/eas/ai/mcp/](https://docs.expo.dev/eas/ai/mcp/) |
| GitHub | follow the GitHub MCP install instructions in your AI tool's plugin gallery |

For each MCP you'll be asked for the corresponding access token from step 1.

### 4. Then run init

Once the accounts, Superpowers, and MCP servers are in place, run `npx @ceredavide/virgilio init` in your project folder. The agent will guide you from the empty `SPEC.md` to the first working slice.

## Update an existing install

```bash
npx @ceredavide/virgilio update
```

Only Virgilio's own files (skills, hooks, instruction files, templates) are replaced. Your `SPEC.md`, source code, Git history, and any custom content inside `.virgilio/` are preserved.

## Options for init

| Option | Effect |
|---|---|
| `--only=claude` | Install only the Claude Code configuration (skip `.codex/`). |
| `--only=codex` | Install only the Codex configuration (skip `.claude/`). |
| `--dry-run` | Show what would be installed without writing files. |

## Requirements

- **Node.js 18 or newer.**
- **Git** installed on your machine.
- **Superpowers** plugin installed in your AI tool — Virgilio depends on it. See [obra/superpowers](https://github.com/obra/superpowers).

## What gets installed

- `.claude/` — skills, hooks, settings for Claude Code.
- `.codex/` — hooks for Codex.
- `CLAUDE.md` and `AGENTS.md` — the instruction files the agent reads at session start.
- `templates/` — the starter `SPEC.md` and `ADR.md` templates.
- `.virgilio/.version` — the install marker.

Your `SPEC.md` (the project's specification) is NOT created by the installer. The agent writes it with you during the first session, via the `spec-coauthor` skill.

## Pin a version

For reproducible installs (useful in user studies, classes, or team setups):

```bash
npx @ceredavide/virgilio@1.2.3 init
```

## License

MIT.
