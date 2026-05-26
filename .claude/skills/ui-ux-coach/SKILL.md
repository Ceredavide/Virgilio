---
name: ui-ux-coach
description: Use this when SPEC.md is confirmed and describes any visible UI (screens, forms, navigation, layout) for which no design has yet been approved, OR when the user explicitly mentions designing a screen, form, flow, or visible behavior. For a non-programmer.
---

# UI/UX Coach

Help the user and the coding agent design simple, understandable, user-friendly interfaces.

This skill is the UI/UX-specific architecture adviser. For a non-programmer, what the application looks like is inseparable from how it is built: screens, navigation, forms, and visual feedback are product decisions, not low-level implementation details.

Use this skill when designing screens, user flows, navigation, layout, forms, or other user-facing behaviour. If Superpowers `brainstorming` is available, use it internally to explore options, then present the UI decision through this skill's plain-language structure. Output the chosen UI/UX direction as an ADR using the template at `templates/ADR.md` so that future sessions see the decision.

## Principles

- Prefer simple layouts.
- Use clear labels.
- Avoid unnecessary complexity.
- Suggest common screens the user may not think about.
- Include loading, empty, success, and error states.
- Prefer responsive design by default.
- Prefer accessible defaults.
- Explain UX decisions in simple language.
- Prefer visual review over textual description for non-programmers (see *Visual Companion* below).
- Before `SPEC.md` exists, create visual exploration only inside `.virgilio/exploration/`.
- Before designing screens or flows, ask which device matters most and who will use the app.

## Visual Capability Declaration

At the start of a project (or when the first design conversation begins), the agent MUST declare in chat which visual tooling is available. Three possible statements, pick the truthful one:

- *"`frontend-design` is available — I can produce real browser-rendered mocks."*
- *"`frontend-design` is NOT installed — I'll fall back to standalone HTML files in `.virgilio/exploration/` that you can open in the browser."*
- *"Neither `frontend-design` nor a usable browser preview is available — I'll do textual screen-by-screen descriptions."*

Without this declaration, the user does not know what they're missing. They may think the agent's textual descriptions are the best the tool can do, when in reality a richer visual tool exists one plugin install away.

## Device And Usage Context

Before designing screens or flows, ask which device matters most:

```text
Which device should this app be designed for first?
A. Desktop web app - best for bigger screens and longer work sessions.
B. Mobile web app - best for quick use from a phone browser.
C. Native mobile app - best when it should feel like an installed phone app.
D. Both desktop and mobile - useful, but usually a little more work.
```

Also ask who will use it and in what situation. Do not design a UI before understanding the primary device and usage context.

## Mobile Design Patterns

This section fires only when the user picked **C. Native mobile app** or **D. Both desktop and mobile** in *Device And Usage Context*. For pure web apps it is not relevant.

Native mobile UIs are not "responsive desktop scaled down". They have their own anatomy and conventions, and using web vocabulary on a mobile design produces screens that feel foreign to a phone user.

### Screen anatomy

A native mobile screen is composed of:

- **Safe area** — the inset region of the screen that avoids the notch, status bar, and home indicator. Layouts must respect it.
- **Navigation bar** (top) — title of the current screen, optionally a back button on the left and an action button on the right.
- **Content area** — the scrollable region with the actual screen content.
- **Tab bar** (bottom, when used) — primary navigation between 3–5 top-level destinations.

Modal screens, sheets, and action sheets are separate patterns layered on top of this anatomy.

### Touch targets and gestures

- Minimum touch target: 44pt (iOS) / 48dp (Android). Smaller targets are perceived as broken.
- Gesture conventions to respect:
  - **swipe-from-left-edge** = go back (iOS, automatically provided by the nav stack);
  - **swipe-down** on a modal = dismiss;
  - **swipe-left** on a list row = secondary action (delete, archive);
  - **pull-down** at the top of a scrollable list = refresh.
- Prefer native pickers for date, time, and option selection. Do not implement a custom dropdown unless the native picker truly does not fit the use case.

### Navigation pattern question

When the spec calls for more than one screen, ask the user:

```text
How should the screens of the app be organized?
A. Bottom tabs + stack - 3 to 5 main sections visible at the bottom; each opens deeper screens.
B. Drawer (hamburger menu) + stack - many sections hidden behind a side menu; each opens deeper screens.
C. Single stack - one main screen, push and pop deeper screens.

Recommended: A, unless the app has fewer than 2 main sections (then C) or more than 5 (then B).
```

### Splash, icon, app name

For any mobile app slice that will be tested by a real participant, the project needs:

- an **app icon** (1024×1024 master image — even a placeholder is fine for a test build, but it cannot be missing);
- a **splash screen** (the first thing the user sees while the JS bundle loads);
- a **final app name** as it will appear in the launcher.

These are not technical configuration — they are product decisions the user must make. Surface them as a small dedicated slice when the spec is confirmed and before the first participant test.

### Visual mock fallback for mobile

The `frontend-design` visual companion described in the next section targets web. For mobile, fall back to a textual screen-by-screen description using the screen anatomy above: name the safe-area handling, the nav-bar content, the main content layout, the tab-bar membership, and any modal or sheet involved. One short paragraph per screen is enough.

### Mobile anti-patterns

- Mirroring a desktop multi-column layout onto a phone screen.
- Using hover-only affordances (mobile has no hover).
- Putting more than 5 items in a bottom tab bar (Apple HIG limit; Material recommends ≤4).
- Designing forms longer than one screen without a step indicator or section split.

## Reference Fetching First

When the user names existing sites, apps, or visual examples — "I want it to look like Linear / Mettler Entwickler / the Apple Music landing page" — the agent MUST fetch those references BEFORE proposing A/B/C design directions.

Workflow:

1. `WebSearch` the named references if the URLs are not provided.
2. `WebFetch` each reference with a prompt focused on **concrete visual language**: palette, font, layout, header style, hero treatment, photography style, button shape, footer composition.
3. Synthesise the common characteristics in plain language for the user.
4. Produce the mock starting from those characteristics, not from a generic AI default.
5. Cite the references in the chat reply.

Field evidence: a mock built from a reference fetch is approved in 1-3 iterations. A mock built from generic AI defaults (elegant serif, warm palette, ecc.) takes 5+ iterations or is abandoned. The cost of fetching is 30 seconds; the cost of skipping is the whole design phase.

## Visual Companion

For any feature whose specification requires a visible UI change (a new screen, a new form, a meaningful layout change, a new navigation pattern), use the Superpowers `frontend-design` skill to produce a visual mock the user can actually see in the browser. Do not rely on textual description when a visual is feasible.

Trigger this only after `spec-coauthor` has confirmed the feature in plain language. The flow is one-shot visual, then textual refinement, then optionally one final visual re-check.

### Flow

1. **The user describes the feature.** The textual specification of the feature is already agreed (from `spec-coauthor` or a follow-up slice).
2. **Generate the visual mock.** Invoke `frontend-design`. When two reasonable approaches exist, ask the skill to produce A/B variants in the same mock. Use `.virgilio/exploration/` for files produced before `SPEC.md` is final, otherwise the project's normal frontend location.
3. **Ask the user one question in chat:**

   ```text
   Here is how the feature would look. Open the preview and tell me one thing:
   A. It is fine, save it and continue.
   B. I want to change something specific (tell me what).
   C. I want to see an alternative version (textual, then we regenerate once at the end).
   ```

4. **Refinement is text-only.** If the user picks B, refine the design through chat ("make the button bigger", "move the avatar to the top right", "drop the secondary action"). Do **not** regenerate the visual mock after every small change — refinement loops in visual generation are slow, expensive, and dispersive for the user. Keep the running list of agreed changes in chat.
5. **Final re-check (optional).** When the textual refinements are stable and the user signals "design ok", regenerate the visual mock **once** with all agreed changes applied, and ask a final confirmation. If the user confirms, the design is locked. If not, fall back to step 4.
6. **Lock the design.** Record the agreed design notes in the relevant ADR or `SPEC.md` section, then hand off to implementation.

### Fallback when frontend-design is not available

**Primary fallback: standalone HTML.** Create a self-contained HTML file in `.virgilio/exploration/` with:

- inline CSS;
- fonts from Google Fonts (CDN);
- images from Unsplash or placeholder services;
- no JS framework or build step.

The user opens it directly in the browser (double-click the file) or in the Launch preview pane of their AI tool. The file is editable in seconds, regeneratable in two minutes. Field evidence shows three design iterations (generic AI → swiss-minimal → refined) in ~15 minutes via this path.

**Secondary fallback: textual description.** Only when standalone HTML is not practical (e.g., the user has no browser available, or the design is purely conceptual). Describe screen-by-screen using the existing layout vocabulary (header, primary action, supporting content, secondary actions, empty state, error state). Tell the user that visual preview is unavailable in plain language; do not expose the missing-plugin detail unless asked.

### Anti-patterns

- Do not generate a new visual mock after every typed comment. One up-front mock, text refinement, optional one final mock.
- Do not show ten variants at once. Two is usually enough; three is the upper limit.
- Do not silently regenerate when the user is mid-conversation about something else.

### Pre-spec visual offer

When offering visual exploration before `SPEC.md` exists, avoid technical opt-in language. Do not mention token cost, implementation details, or experimental tooling unless the user asks. Prefer a simple choice:

```text
I can show a quick visual sketch while we define the app.
A. Use the visual preview (recommended)
B. Continue in text only
```

## When Designing a Feature

### Classification of slices

Before applying the full Visual Companion flow, classify the slice:

- **New pattern** → full visual mock A/B/C as documented below.
- **Visually significant extension** — same visual language as approved, but adds ≥2 new sections to a page, more than doubles a page's height, or introduces a new interaction primitive (carousel, accordion, tab strip). → mini-gate with visual mock (or detailed textual mock) before building.
- **Medium extension (new screen reusing approved language)** → text-only A/B with recommended option in chat; visual mock only if the user asks.
- **Small extension (new field on an existing form, new action on an existing card, variant)** → textual declaration only, then ask the user whether to mock or trust.

Recommend the lighter option for small extensions; recommend the visual mock for new patterns and visually significant extensions.

For "visually significant extension" and "medium extension", declare the expected visual impact in plain language **before building** ("the home page will go from 3 sections to 6, roughly doubling its height; the carousel will appear between Intro and Contact"). One line. This catches "it's not what I imagined" early.

#### Concrete Examples By Category

To resolve the recurring ambiguity in the field — agents tend to under-classify "new patterns" as "extensions" and skip the gate — here are concrete examples:

**New pattern (full A/B/C gate required):**

- First admin shell with sidebar (the layout itself is a new pattern, regardless of how few pages it has).
- First detail page (hero + content layout) when only list pages existed.
- First page hero on the public site.
- First multi-tab interface inside a single page.
- First wizard / step-by-step flow.
- First data table with bulk actions or row-level actions.

**Visually significant extension (mini-gate required):**

- Adding a carousel/accordion/tab strip to an existing page that has none of those.
- Doubling a page's vertical content (3 sections → 6).
- Changing the navigation pattern shape (sidebar → top tabs).

**Medium extension (text-only A/B):**

- A second admin page that reuses the approved admin shell.
- A second public landing variant with different hero copy but same layout.

**Small extension (declaration only, no gate):**

- A new field on an existing form.
- A new action button on an existing card or row.
- A colour or copy tweak.

When in doubt, the agent must choose the heavier classification. False positives cost a question; false negatives cost a rebuild.

The Affirmative-response rule still applies: short "ok" / "go" answers confirm the option choice, not bypass the declaration.

### Design checklist

Consider:

- What screen is needed?
- What should the user see first?
- What action should be most obvious?
- What can go wrong?
- What feedback should the app show?
- What should happen after success?
- What should happen if there is no data?
- What should happen while the app is loading?

For page-level decisions, ask in plain language:

- what pages exist;
- what each page is for;
- what the user can do there;
- what information is visible;
- what happens after the main action.

If authentication, payments, sensitive data, production deployment, or complex permissions affect the experience, warn that the prototype should be reviewed by an experienced developer before real use.

## Best Practices

Apply these by default when relevant:

- clear page titles;
- visible primary actions;
- helpful empty states;
- understandable error messages;
- success feedback;
- confirmation before destructive actions;
- simple navigation;
- responsive layout;
- basic accessibility labels and semantic structure.
- password confirmation for registration forms when relevant;
- safe, clear wording around privacy and destructive actions.

## Output

Before implementation, provide a short UI/UX plan.

Include:

- screens;
- main user actions;
- important states;
- recommended default behavior;
- simple testing notes for the user.

If a local preview can be started, include the local URL and the exact screen or action the user should test.

Pre-spec visual exploration is temporary. Do not treat it as production app code, and use it to improve the written specification.

When asking the user to choose between layouts or flows, prefer lettered options and a recommendation:

```text
Which layout feels best?
A. Compact dashboard - fastest to scan
B. Guided step-by-step flow - easier for beginners
C. Split view - useful when comparing details
D. Something else / a mix

Recommended: A, because ...
```
