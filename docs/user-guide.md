# Using Virgilio — a guide for non-programmers

> Language: **English** · [Italiano](user-guide.it.md) · [Deutsch](user-guide.de.md)

Virgilio is a layer on top of Claude Code (or another AI coding assistant) that walks you step by step through building an app, without assuming you know how to program.

This guide does not explain how to install Virgilio (for that, see the main README). It explains what to expect from a session, how to answer Virgilio's questions well, and what Virgilio will or will not do for you. Reading time: ~10 minutes.

## What Virgilio is, in two paragraphs

Virgilio enforces a simple rule: **decide what the app does first, then write it**. No code is written until a document called `SPEC.md` exists, describing in plain language what the app does, for whom, and within what limits. You define that document, through a structured conversation with the assistant.

Once the spec exists, Virgilio implements the app **one complete slice at a time** — one small feature per slice — and after each slice tells you how to try it manually, confirms with you that it works, and saves a checkpoint. If something breaks, you return to the last good checkpoint.

## What happens in the first session

A typical first session lasts 30–90 minutes and follows this shape:

1. **Brain dump.** Virgilio will ask you to write, in your own words, everything you have in mind for the app — what it does, who uses it, why, how you imagine it, what it should NOT do. The more you write here, the fewer questions you'll hear later.
2. **Focused questions, one at a time.** One topic per turn (e.g. "what device does it primarily run on?", "will there be a login?"). Often with 3–4 A/B/C/D options and a recommendation.
3. **Spec summary.** When Virgilio has understood enough, it shows you a summary and asks for explicit confirmation before saving it as `SPEC.md`.
4. **Basic technical choices.** Right after, 2–3 alternatives for where the app will live (Vercel for web, Supabase for data, Expo for mobile, …) with the recommended default.
5. **Basic setup.** If the app saves data, Virgilio will have you create a Supabase account before writing any code (about five minutes, only once).
6. **First slice.** Virgilio implements a first small feature, tells you exactly how to try it in the browser, and asks whether it works.

## How to answer well

### To the brain dump
The more specific, the better. Include obvious things ("there clearly needs to be a login") and things you do **not** want ("I don't want push notifications"). Concrete examples and situations are worth more than abstract descriptions: "two friends splitting a pizzeria bill" is more useful than "shared expense management".

If you don't feel like writing a long brain dump, a short one is fine — Virgilio will compensate with more questions later. But if you're short on time, this is the place to invest it.

### To A/B/C/D questions
You can:

- answer with a single letter (`B`)
- combine ("A plus one thing from B")
- propose your own ("none of those work, I'd rather…")
- ask for more options or an opinion ("I don't know, what do you think?")

There are no "wrong" answers as long as they reflect your taste or your real needs. There is one wrong answer: trying to guess what Virgilio "wants to hear". Answer honestly.

### When you don't know
Saying **"I don't know, you decide"** is a legitimate answer. Virgilio has defaults designed for non-programmers who maintain the app on their own — those defaults are fine for most cases. Push back only when the question directly touches what you want out of the product.

## What the recurring choices mean

**Primary device.** You have to decide whether the app is primarily for desktop, mobile web (a browser on the phone), or a real installable phone app. This influences almost every design decision downstream.

**Login or no login?** "No login" is a real choice — it means anyone who knows the app's URL can see and modify everything. Fine for small personal utilities, not for anything else.

**Who sees what.** If there are users, you have to decide whether each one sees only their own data, whether there are shared groups, or whether there's an "admin" role.

**Use as main / preview / discard.** At the end of every slice, Virgilio will ask what to do with the new version:

- **Use as main** — this version becomes the real app; the new functionality joins the normal app.
- **Keep as preview** — the current version stays as it was, the new one is set aside as a draft. Useful when you want to compare or you're not convinced yet.
- **Discard** — throw the slice away and return to the last working version.

None of these is final: even a *discard* is recoverable until you overwrite something else.

**Pending external review.** If the app touches login, payments, personal data, production deployment, or legal matters, Virgilio adds a row to a table inside `SPEC.md`. That table is a reminder: before letting real users in, someone experienced should look at those items. Virgilio will still build, but it will remind you to call an expert before "launch".

## What Virgilio will always do

- Ask for a spec before writing code.
- Save a checkpoint after every working slice.
- Tell you exactly how to try the new functionality in the browser — URL, what to click, what to expect.
- Stop if Git is not initialised, or if the app saves data but the database is not configured.
- Break a large request ("do login, signup, password reset and logout") into several slices, building them one at a time.

## What Virgilio will refuse to do

- Write code before `SPEC.md` exists.
- Use "temporary solutions" that look like they work but have to be redone later (for instance, saving data in the browser when the app really needs a database).
- Ask you to approve technical choices you can't reasonably evaluate (internal refactors, dependency wiring, file layout). Those Virgilio handles itself with a safe default.
- Skip the manual test at the end of a slice.
- Implement multiple large features in the same session without confirming each step.
- Push sensitive things to production (authentication, payments, personal data) without reminding you that an expert review is needed.

## If you feel the agent is going too fast

Virgilio has specific moments when it *must* stop and ask for your confirmation:

- before writing code → `SPEC.md` must exist;
- before designing screens → it must show you 2–3 design options and wait for your OK;
- before saving real data → the backend (Supabase) must be configured;
- at the end of every slice → it must give you manual test instructions;
- right after → it must ask what to do with the slice (use as main / preview / discard).

If the agent skips one of these, you can stop it:

```text
Wait, you skipped the design / the backend setup / the manual test.
Let's go back to that step.
```

Virgilio will NOT roll files back automatically (risk of losing work). It will tell you what is already written and ask whether you want to pass through the skipped step now (possibly with code changes) or accept the skip as known "debt" to handle later. You decide.

Short affirmatives like "go", "proceed", "ok", "you decide" are normal. They mean "continue to the next required step", not "skip the gates". If the agent interprets them as permission to skip design or test, stop it.

## When to call a real programmer

Virgilio is excellent for **building a working prototype** and testing it with friends and family. It does NOT replace a programmer when any of these come into play:

- **Real, unknown users** (people you don't know personally who trust your software).
- **Real money** (payments, subscriptions, invoices).
- **Sensitive data** (health, financial, personal identifiers).
- **Compliance decisions** (GDPR, legal archiving, mandatory accessibility).
- **Complex infrastructure** (multiple servers, scaling, high availability).

For all of these, Virgilio helps you reach a prototype, but reminds you to call an expert before launch. The *Pending external review* table inside `SPEC.md` is your reminder.

## Honest limits

- **Virgilio is not deterministic.** The same prompt can produce slightly different answers in two sessions. It's not a bug, it's the nature of language models. For important things, always confirm.
- **It is not a no-code tool.** You have to answer questions, read summaries, run manual tests, confirm checkpoints. It is not "press a button and an app appears".
- **It works best for small-to-medium apps.** A shared to-do list, a small utility for a group, a personal management app — yes. A social network or a marketplace with thousands of users — no, beyond the prototype you'll need a real team.
- **The AI assistant can be wrong.** If you see it proposing something that looks strange, stop it and ask for an explanation. Saying "wait, I don't understand why you're doing it this way" is always fine.

## If you feel stuck

- "I don't understand the question" → ask for an example or a rephrasing.
- "I don't know which option to choose" → say "I don't know, you decide".
- "The app doesn't do what I expect" → describe what you did, what you expected, and what you saw. Virgilio will switch to troubleshooting mode.
- "This is too big, I want to do less" → say "let's just do X for now, the rest later".
- "I'm losing the thread" → say "give me a summary of where we are and what's left".

---

*This guide is meant for the first hour with Virgilio. For technical details about the internal workings (skills, hooks, repo structure) see the other project documents.*
