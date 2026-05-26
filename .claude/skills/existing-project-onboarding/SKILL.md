---
name: existing-project-onboarding
description: Use this when SPEC.md is missing but the repository already contains application files, or when a non-programmer asks to understand, extend, clean up, or continue an existing project.
---

# Existing Project Onboarding

Help a non-programmer understand an existing codebase before any implementation begins.

This skill turns an inherited or generated repository into a plain-language project map and a draft `SPEC.md`. The goal is to make the current project understandable and safe to extend.

## Core Rules

- Do not write or edit application code while using this skill.
- Do not refactor, clean up, upgrade, or fix the project during onboarding.
- Do not assume the project is broken just because the structure is unfamiliar.
- Do not expose low-level file-by-file technical detail unless it explains user-visible behavior.
- Do not read or print secret values from `.env` files. You may note which environment variable names appear necessary.
- Treat the current code as the source of evidence, but mark uncertain conclusions clearly.
- Prefer a small, understandable summary over exhaustive code documentation.

## When To Use

Use this skill when:

- `SPEC.md` is missing and the repository already contains application files;
- the user asks "what does this project do?";
- the user wants to extend, continue, clean up, or take over an existing project;
- the user received a repo from someone else and does not know how it works.

If the repository is empty or clearly not an application, do not use this skill. Use `spec-coauthor` if the user is defining a new app.

## What To Inspect

Inspect only what is needed to understand the project:

- README and existing documentation;
- package or framework files, such as `package.json`, `pyproject.toml`, `Gemfile`, `pubspec.yaml`, or Expo config;
- app entry points, routes, pages, screens, and major UI components;
- data models, database schema files, migrations, or API routes;
- environment variable examples, without reading secret values;
- test files or scripts, if present;
- deployment config, only to understand how the app is expected to run.

Use fast searches and summaries. Do not bulk-read generated folders such as `node_modules`, build outputs, caches, or lockfile internals unless there is a specific reason.

## Process

1. Check whether `SPEC.md` exists.
2. Check Git status and note whether there are uncommitted changes. Do not modify or revert them.
3. Identify the framework, runtime, and likely app type in simple language.
4. Map the visible user-facing features.
5. Map the main screens, flows, and actions.
6. Identify the data the app appears to store or send.
7. Identify external services, login, payments, sensitive data, or deployment assumptions.
8. Infer how to run or preview the app, but do not install or upgrade dependencies unless the user explicitly asks.
9. Create `.virgilio/onboarding/project-summary.md`.
10. Create or update a draft `SPEC.md` when there is enough evidence. Mark uncertain sections as "Needs confirmation".
11. Present the summary to the user in plain language and ask them to confirm or correct the product understanding.
12. After confirmation, hand off to `spec-coauthor` if the specification still needs product decisions, security elicitation, or first-slice selection.

## Project Summary Structure

Create `.virgilio/onboarding/project-summary.md` with this structure:

```md
# Existing Project Summary

## What This Project Appears To Be

Plain-language description of the app.

## What Users Can Currently Do

List visible features inferred from the code.

## Main Screens Or Interfaces

List pages, screens, routes, or command interfaces in user terms.

## Data And External Services

Describe stored data, APIs, authentication, payments, files, or third-party services. Do not include secret values.

## How It Appears To Run

List likely local commands or preview steps, only if they are visible from project files.

## Risks Or Unknowns

List anything uncertain, risky, sensitive, or needing user confirmation.

## Suggested Next Small Steps

Suggest 2-4 small, user-visible next slices or cleanup options.
```

## Draft SPEC.md Guidance

If enough evidence exists, create a draft `SPEC.md` using the standard Virgilio structure.

The draft must:

- describe current behavior, not imagined future behavior;
- clearly mark assumptions and uncertain areas;
- include current visible features;
- include likely out-of-scope items;
- include a "Needs User Confirmation" note where product intent is unclear;
- avoid adding new features unless they are listed as possible next steps.

If there is not enough evidence to create a useful `SPEC.md`, do not invent one. Create only the onboarding summary and ask the user for missing context.

## User-Facing Summary

After onboarding, explain:

- what the project appears to be;
- what it already seems able to do;
- what is unclear;
- what the safest next step is.

Use lettered choices:

```text
Does this description match the project?
A. Yes, continue from this understanding
B. Partly, I want to correct something
C. No, the project is for something else
```

Do not ask the user to evaluate internal architecture unless it affects cost, privacy, deployment, or maintainability.
