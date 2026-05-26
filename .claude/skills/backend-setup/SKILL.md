---
name: backend-setup
description: Use this when SPEC.md requires data persistence or login, the backend (Supabase by default) is not yet set up, AND either (a) the SPEC describes no visible UI (CLI tool, API-only, agent backend, script), or (b) the UI Design Gate has been completed for the visible features. Guides a non-programmer through creating a Supabase project and connecting it to the app.
---

# Backend Setup

Set up the real backend for a Virgilio project before the first slice that needs stored data or login.

This skill is the non-programmer-friendly provisioning workflow. The default backend is Supabase, already chosen in Architecture Selection.

## When To Use

Use this skill when:

- `SPEC.md` describes data that must persist or be shared (section 6, *Data the app remembers*);
- `SPEC.md` describes any login or access control (section 9, *Security and access control*);
- the project has no working backend credentials yet.

If the project already has working Supabase credentials, do not re-run provisioning. Move on to the slice.

## Core Rules

- A slice that needs stored data is not real until it runs against the real backend.
- Do not work around a missing backend with local files, in-memory state, or browser storage. A local store passes the manual testing gate while hiding that the real backend does not exist: it looks like progress, but it cannot be deployed, cannot be shared between users, and has to be rebuilt later. This is the most important failure to avoid here.
- Default to the hosted (online) free project. Do not ask a non-programmer to install Docker or run a local Supabase stack — it is heavier and fails in ways they cannot fix.
- Never commit credentials. Confirm the project's local environment file is ignored by Git before storing anything in it.
- Some Supabase features (e.g., HaveIBeenPwned password check, custom SMTP, point-in-time recovery) require the Pro plan. Verify availability before proposing a feature that requires upgrade; if it's Pro-only, say so up-front and let the user decide.
- When a slice introduces file uploads, verify that deletion of the related record also removes the orphan files in storage. Otherwise the storage bucket fills with unreachable files over time.

## What "Connected" Means

The backend is connected when the app has working Supabase credentials available — normally a project URL and key in a local environment file such as `.env.local`. That is the real gate. How the agent got there does not matter; the credentials being present and working does.

## Check Connector / MCP First

Before asking the user to create a Supabase project manually and copy keys, check whether a Supabase connector, plugin, or MCP is already configured for the project or the host tool:

1. If a Supabase MCP is configured with credentials, use it directly — create or select the project, provision tables, run setup actions through the MCP. No manual key entry is required.
2. If a Supabase plugin or connector exists in the host tool but credentials are missing, prompt for the smallest setup needed (often just connecting the user's existing Supabase account).
3. Only if no connector and no MCP are available, fall back to the manual *Provisioning Walkthrough* below.

The connector path is faster and reduces the surface where a non-programmer can paste keys in the wrong place. Prefer it when available.

After any setup performed via a connector, complete the *Supabase Dashboard Tour* so the user understands what was created.

## Provisioning Walkthrough

**This walkthrough is the fallback path** when no Supabase MCP connection is available (see § *Check Connector / MCP First* above). When the MCP IS available, prefer the MCP path — it is faster, less error-prone, and the user does not have to copy-paste keys. Use this walkthrough only when the MCP path is unavailable or has failed.

A Supabase project is created by a person, on the Supabase website — the agent cannot create the account. Guide the user in plain product language, not technical opt-in language:

```text
Before I build features that save data, we need a safe place to store it.
I will guide you, step by step:
1. Create a free account on supabase.com
2. Create a new project
3. Copy two keys from the project settings and paste them here
It takes about five minutes, and only has to be done once.
```

When the user provides the keys, store them in the project's local environment file, confirm that file is ignored by Git, and never commit credentials.

Local Supabase via Docker is an option only if the user is technical and explicitly asks for it.

## Using an MCP Connection When Available

If a Supabase MCP connection is available, use it to do the backend work directly — create tables, apply schema changes, inspect data. If no MCP is available, guide the user through the Supabase dashboard and write the schema as migration files instead.

The MCP is an accelerator for the agent, never the gate. The gate is always "the app is connected to a real backend", reachable with or without an MCP. Do not require a non-programmer to configure an MCP.

A Supabase MCP connection with a broad access token can create and delete database tables. Treat that token as a sensitive credential: never commit or expose it, and be deliberate with destructive schema actions.

## Post-Migration Health Check

After any schema migration via MCP, run both `get_advisors(type="security")` and `get_advisors(type="performance")`. Security alone misses index and query issues that only hurt as data grows.

## Persist Schema Changes to Repo

Every schema change applied via `apply_migration` (or any equivalent MCP call that mutates database structure) MUST also be written to a versioned migration file in the project repository.

### Rule

After every successful `apply_migration` call:

1. Write the same SQL to `supabase/migrations/YYYYMMDDHHmmss_<descriptive_slug>.sql` in the project repo. Create the `supabase/migrations/` directory if it does not exist.
2. Use the Supabase CLI timestamp format for the prefix: 14 digits, UTC, no separators (`20260526143012`). This matches what `supabase migration new <name>` produces locally, so future Supabase tooling reads the files in the right order.
3. The slug is a short snake_case description of the migration (`create_core_tables`, `enable_rls_and_policies`, `add_team_table`, …).
4. Commit the migration file as part of the slice that produced the schema change. The migration file is not a separate slice; it is part of the same commit as the code that depends on the new schema.

### Why

The MCP applies the migration to the live Supabase project, but the migration text lives only in Supabase's cloud database after that. Three realistic failure modes lose the schema if the file is not persisted:

- The Supabase project is deleted by accident.
- The Supabase project is paused permanently (free-tier inactivity cleanup).
- The user wants to migrate the project to a different Supabase organisation or to self-host.

A non-programmer cannot run `pg_dump` and reconstruct the schema by reading raw SQL. The repo file is the durable, human-readable record.

### When MCP is not available

The pre-existing fallback path (manual schema via Supabase dashboard with migration file) already produces a `supabase/migrations/*.sql` file by construction — it is the same convention. Both paths converge on the same artefact in the repo.

### Anti-patterns

- Applying a migration via MCP and skipping the file because "the schema is already in Supabase". This is the most common omission. Do not skip it.
- Writing the file but committing only at the end of the session. Commit it with the slice that needed the schema; otherwise a session that fails mid-way leaves a divergence between repo and Supabase project.
- Using a non-UTC timestamp. UTC is the convention; mixing local time across machines creates file-ordering bugs when collaborators are in different timezones.

## Database Types: Single Source of Truth

When using the Supabase MCP, the agent generates TypeScript types via `generate_typescript_types`. Two strategies for using these types in the project — pick ONE and commit to it:

**Option A — MCP output as canonical types (recommended).** Save the full output of `generate_typescript_types` directly to `lib/supabase/database.types.ts` (or the project's equivalent path). Verbose, but authoritative. Re-generate every time the schema changes.

**Option B — Manual summary with regeneration script.** Maintain a hand-written types file PLUS an npm script `db:types` that regenerates from the MCP and FAILS if the generated output diverges from the manual summary. The script forces the manual file to stay in sync. More effort, smaller types file.

Pick the strategy at the first MCP-driven schema migration and document the choice in `SPEC.md` section 6 (Data) or in an ADR. Do not silently switch between strategies across sessions: the second session won't know which one the first one used, and the types will drift.

Field evidence: silently maintaining a "simplified manual summary" in parallel with MCP output (without the regeneration script) produces type drift within 2-3 schema changes. The drift is invisible until a query fails at runtime.

## Supabase Dashboard Tour

After creating or modifying Supabase resources for the project (whether via MCP or via the user's manual setup), invite the user to inspect what was created in the Supabase dashboard. The point is product-understanding, not technical verification — the agent still verifies setup with tools.

Walk through each relevant area with one sentence on what it means for the app:

- **Project Overview**: project name, status, region.
- **Authentication**: where the app's users will appear once registration is built.
- **Table Editor**: where the app's tables live. List the tables created by name and what each holds.
- **Storage**: where uploaded files live. List any buckets created.
- **Policies / RLS**: where access rules are managed.

For each area, suggest what to look at and what NOT to change yet.

Example wording:

```text
Apri Supabase e seleziona il progetto.

1. Vai in Table Editor.
   Dovresti vedere le tabelle che abbiamo creato — qui vivranno i dati dell'app.

2. Vai in Storage.
   Dovresti vedere i bucket che abbiamo creato — qui verranno salvati i file caricati.

3. Vai in Authentication.
   Qui compariranno gli utenti quando creeremo account reali.

Non modificare nulla per ora: questa visita serve solo a capire dove sono finite le cose.
```

## Deployment Is Separate

Hosting on Vercel is not needed to build and test slices — the app runs locally with its dev server. Vercel matters only when the app goes live for real users. Do not block early slices on deployment; handle Vercel at the "going live" step, alongside the pending external review reminders.

## Mobile / Expo Notes

When the project's primary device is native mobile (Expo), the Supabase setup is the same as for web (hosted project, anon key, RLS, dashboard tour). Three caveats matter for the client side:

- **Public environment variables must be prefixed `EXPO_PUBLIC_`.** Expo only exposes env vars to the client bundle when the variable name starts with `EXPO_PUBLIC_`. Use `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_ANON_KEY` in the local environment file, not the unprefixed names used by Next.js. The Supabase JS SDK works identically once the variables are exposed.
- **File uploads use `expo-file-system` URIs, not `Blob`.** React Native does not expose `Blob` in the same way the browser does. When the first upload slice arrives, verify the upload helper consumes the URI returned by `expo-file-system` (or `expo-image-picker`) and not a synthetic `Blob`.
- **Auth redirect URLs include a deep-link scheme.** Magic links and OAuth redirects on Expo target a custom URL scheme (`exp://...` during development, the project's own scheme in production builds). Add the relevant entries to the Supabase Auth redirect allow-list when login is built, otherwise the redirect after authentication silently fails on the device.

These notes apply only when the first mobile slice is implemented. They do not block backend provisioning itself — credentials in `.env.local` work identically.

## Output

After successful setup:

- the local environment file contains working credentials;
- the file is gitignored;
- the agent confirms briefly, in plain language, that the backend is ready;
- the agent moves on to the first slice that needed the backend.

If setup fails or stalls, explain the blocker in plain language and propose the next step — do not silently proceed to slice work without a connected backend.
