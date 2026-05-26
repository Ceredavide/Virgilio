---
name: pre-publishing-checklist
description: Use this when the user signals intent to go live (first deployment to production, custom domain, real users), to verify that domain, email, legal pages, secrets, backend health, and pending external reviews are ready before public exposure. For a non-programmer.
---

# Pre-Publishing Checklist

Guide a non-programmer through the verification steps required before exposing the application to real users for the first time.

## When To Use

Use this skill when:

- the user says "go live", "let's publish", "let's show it to someone", "real users", "production", "first deployment to a custom domain";
- the slice just completed enables the app to receive non-author traffic (custom domain configured, first paid plan, real SMTP configured, switching from preview to production);
- before any "share the URL" moment with someone external to the development.

## Why This Matters

Without a structured pre-publishing pass, the first contact between the application and real users typically fails on small but visible items: legal pages missing behind consent checkboxes, AI-generated translations never reviewed, default platform subdomain instead of a custom domain, signup emails sent from a generic Supabase sender, secrets ending up in the wrong place. These cost reputation, not just minutes. The checklist surfaces them before the user sees them.

This skill is verification, not implementation. For each failed item, the appropriate next action is a small slice that closes the gap — handed off to `slice-execution` or `backend-setup` as appropriate.

## Primary Device Dispatch

Before running the checklist sections below, read the primary device from `SPEC.md` section 3:

- **Web only** → run all sections below as-is. Mobile publishing items do not apply.
- **Native mobile (Expo) only** → skip the *Domain and email* section and the cookie banner item in *Legal and trust* (they are web-specific). Run *Backend and data*, *Identity and access*, *Content and translations*, *Specification*. Then invoke `mobile-publishing-checklist` for store submission, certificates, privacy disclosures, and App / Play review expectations.
- **Both web and mobile** → run the full checklist below for the web side, then invoke `mobile-publishing-checklist` for the mobile side. Produce a single combined readiness report at the end (not two separate ones — the user is going live once, not twice).

If `SPEC.md` does not record the primary device clearly, stop and ask the user before continuing the checklist.

## The Checklist

Run through the sections in order. For each item, ask the user, observe the state of the project, and surface gaps explicitly. Translate failures into the smallest next slice that closes them.

### Domain and email

- Custom domain configured and pointing to the deployment (not just the platform's default subdomain).
- Email sender configured with custom SMTP if the app sends real email (signup confirmation, password reset, magic links, notifications). The default Supabase sender is heavily throttled and looks unprofessional.
- Email templates (signup, password reset, magic link, notifications) reviewed for the project's tone and language.

### Legal and trust

- Privacy policy page exists and is reachable from any consent checkbox that links to it (see `slice-execution` § Pending References).
- Impressum / legal owner information present (mandatory in CH, DE, AT; recommended elsewhere).
- Cookie banner present if cookies are used beyond strictly necessary, with locale-appropriate wording. *(Web only — native mobile apps do not have cookies; their equivalent privacy surfaces are handled by `mobile-publishing-checklist`.)*

### Backend and data

- Supabase advisors (security + performance) re-run on the final schema (see `backend-setup` § Post-Migration Health Check).
- Storage cleanup verified for any uploaded files: deletion of the parent record removes orphan files.
- Backups configured, or explicitly acknowledged as missing and accepted as known debt.
- Row-Level Security policies reviewed against the going-live scope: more user types may now access the app than during development.

### Identity and access

- Redirect URL allow-list configured for the custom domain (Supabase Auth, OAuth providers, magic links).
- Email confirmation policy set (on for real users; off only for explicit reasons).
- Pro-only features previously deferred (HaveIBeenPwned password check, point-in-time recovery, custom SMTP) verified against the chosen plan.

### Content and translations

- AI-generated public content (translations, marketing copy, descriptions) flagged for human review per the Expert Escalation rules in `AGENTS.md` and tracked in SPEC section 12.
- Placeholder content (lorem ipsum, "Coming soon", default images, provisional logo) replaced with real assets.

### Specification

- SPEC section 12 (Pending external review) reviewed in full: every item either marked as reviewed, or explicitly accepted by the user as known debt with the going-live scope.

## Output

After running the checklist:

- list which items pass, which fail, and which require the user to act (e.g., contact a translator, register a domain, install custom SMTP credentials);
- for each failure, propose the smallest slice that closes the gap and offer to start it;
- do not proceed with the going-live action while critical items (legal pages, email confirmation policy, Pending external review) are open.

End with an explicit summary in plain language:

```text
Pre-publishing check:
- X items pass
- Y items need a quick fix (I can propose slices)
- Z items need you to act outside the app (translator, domain, ...)
- W items in Pending external review are still open

Are we ready to go live, or do we close some of these first?
```

## When To Skip

- Pre-deployment iterations on the author's machine: not yet exposed to non-author users.
- Deployments to staging or preview environments that explicitly stay private.

## Anti-Patterns

- Running the checklist as a one-shot pass/fail report without offering remediation slices.
- Skipping items because "they sound minor" — none of these items are minor for the user's first reputation contact.
- Treating the checklist as the going-live gate itself. The checklist verifies readiness; the user's explicit "we go live" remains the gate.
- Letting the checklist expand into general security or quality review — those belong to `security-review-pipeline` and to `requesting-code-review`. Pre-publishing is specifically about the first-exposure surface.
