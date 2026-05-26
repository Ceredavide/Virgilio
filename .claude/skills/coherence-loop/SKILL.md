---
name: coherence-loop
description: Use when the agent detects a change to one of the three circles of the project (spec/idea, design, technology stack) — typically after the user accepts a new feature, picks a design option, or chooses a stack component. Runs the coherence check, declares the outcome in chat, and surfaces any conflict as a single A/B/C question. For a non-programmer.
---

# Coherence Loop

Keep the project's idea, design, and technology choices coherent with each other across iterations.

Specification, design, and technology decisions are not three sequential stages. They form a loop: a new design idea can reveal a tech constraint, a tech constraint can force a feature simplification, a feature simplification can change the design. Skipping the loop produces specifications that look fine on paper but fall apart at implementation.

## When To Invoke

After any change to one of the three circles (Idea / Design / Tech), run a short coherence check on the other two before continuing. A change happens when:

- the user accepts a new feature (Idea changed);
- the user picks a design option, mock, or screen layout (Design changed);
- the user (or the agent, with user acceptance) chooses a stack component, library, hosting platform, or backend (Tech changed).

## Procedure

1. **Detect the change.** Identify which of the three circles changed, and which two need the check.

2. **Quick-check the other two circles.** Ask internally: does this break, contradict, or significantly complicate the other two? Examples:
   - Idea changed: does the existing design still cover it? Does the chosen stack still fit?
   - Design changed: does the spec still describe what the screen does? Does the stack support the design (real-time, offline, file uploads)?
   - Tech changed: does the spec still hold given the stack's limits (free tier, capabilities)? Does the design rely on something the stack does not offer cheaply?

3. **Declare the outcome in chat, always.** Either:
   - *"Spec/design/tech remain coherent, continuing"*, or
   - *"Coherence conflict detected: A/B/C"*.

   The check is invisible to the user unless declared — skipping the declaration counts as skipping the loop.

4. **If incoherent, surface the conflict as a single A/B/C question** to the user, in plain language, with a recommended default. Do not silently adapt one of the three to fit the others.

## Mandatory Declaration

The Coherence Loop check is invisible to the user unless declared in chat. **Skipping the declaration counts as skipping the loop.** The agent MUST declare the outcome after every Idea / Design / Tech change, even when no conflict is found:

- *"Spec/design/tech remain coherent, continuing."* (no conflict)
- *"Coherence conflict detected: A/B/C."* (with the question that follows)

A single sentence is enough. Without the declaration, the loop becomes invisible and the failure mode is silent drift: a decision in one circle (e.g., new feature in Idea) goes uncrosschecked against the other two (Design, Tech), and the inconsistency surfaces only at implementation time, when it's expensive to fix.

## Example conflict surfacing

```text
The "online" live indicator on the chat screen requires one persistent
connection per visible friend. Supabase free tier limits these. Options:

A. Drop the live indicator. (simplest, free)
B. Replace it with "active in the last 5 minutes". (almost the same,
   still free, polled every few minutes)
C. Keep live indicators. (will likely require a paid plan when usage
   grows past ~20 users)

Recommended: B.
```

## Exit Criterion

The loop exits only when the user explicitly confirms that idea, design, and tech are all acceptable. Suggested wording for the exit prompt:

```text
We agreed on:
- Idea: <one line>
- Design: <one line>
- Tech: <one line>

Should I lock these and start building the first slice?
A. Yes, lock it and build the first slice.
B. Wait, I want to revise something first.
```

Until the user picks A, do not write application code.
