# [App name]

**Last updated:** YYYY-MM-DD
**Status:** [draft | confirmed | in revision]

> SPEC.md is the central source of truth for this project. It is written in plain language so a non-programmer can read, change, and approve it. Every implementation slice should trace back to a line in this file. Keep it short. Add detail only when a real decision has been made.

## 1. What the app is

One or two sentences that describe the app to someone who has never seen it. Avoid jargon.

Example: "A mobile web app where a small group of friends can share trip expenses and see who owes what at the end of the trip."

## 2. Who uses it

- **Primary user:** who they are, why they care, in what situation they open the app.
- **Other users (optional):** any secondary role that touches the app, with one line each.

If there is only one type of user, say so explicitly.

## 3. Main device and usage context

State the primary device and how it is used. This drives every UI decision.

- **Device:** [desktop web | mobile web | native mobile | desktop + mobile]
- **When it is used:** short situation description (at home, on the go, on shared screens, offline, etc.).
- **Connection:** [always online | sometimes offline | unknown]

## 4. Core features (current scope)

List only the features that belong in the version being built now. One bullet per feature, in user-visible language.

- A user can ...
- A user can ...
- A user can ...

Out of scope right now (so we do not forget but do not build):

- ...
- ...

## 5. Key user flows

For each important flow, describe the steps in plain language. One short list per flow.

### Flow: [name]

1. The user opens ...
2. The user sees ...
3. The user does ...
4. The result is ...

Repeat for each flow that matters for the current scope.

## 6. Data the app remembers

List the kinds of information the app stores, in plain language. No tables, no field types unless a real decision has been made.

- **[Thing]:** what it represents, who can see it, who can change it.
- **[Thing]:** ...

If anything is sensitive (personal data, payments, passwords), say so here.

## 7. What the app does **not** do

Useful boundaries. Things that look reasonable but are explicitly out of scope.

- ...
- ...

## 8. Look and feel

A few short statements about the desired tone and style.

- **Tone:** [friendly | neutral | professional | playful | ...]
- **Visual style:** [simple and clean | dense and information-rich | ...]
- **Accessibility expectations:** [readable on small screens | works with screen readers | high contrast | ...]

Specific design references (optional): links, screenshots, or sketches.

## 9. Security and access control

Plain-language answers to the safety questions any application needs. The agent fills these in during the Mandatory Coverage Check; the user confirms them.

- **Authentication:** [no login | single owner | email + password | magic link | OAuth | invite-only]. Account recovery expected? Two-factor expected?
- **Who sees what:** [single-user | shared groups | roles (admin / member / viewer) | fully public]. Confirm explicitly even when it seems obvious.
- **Sensitive data categories:** [none | personal | financial | health | location | messages | ...]. Anything that would be embarrassing or harmful if leaked goes here.
- **External services and credentials:** for each external service (email, payments, third-party API), state whether the user provides their own key or the app uses a shared one.
- **Destructive actions:** which actions cannot be undone. These need confirmation prompts in the UI.

## 10. Quality bar

Plain-language expectations the app should meet before real users use it.

- Forms validate input and explain errors clearly.
- Destructive actions ask for confirmation.
- The app shows a sensible empty state when there is nothing to display.
- The app shows a sensible loading state on slow connections.
- Add other expectations specific to this app.

## 11. Risks and expert review

List anything where a non-programmer should consult an experienced developer before exposing real users.

- Authentication and account recovery
- Payments and billing
- Personal or sensitive data
- Production deployment
- Anything else that touches money, identity, or legal compliance

## 12. Pending external review

A persistent, growing list. The agent adds a row every time a slice touches sensitive scope (authentication, authorization, payments, personal data, production deployment, legal or compliance, security-critical behavior). Rows stay here until the user manually changes the Status field after a real external review has happened. Before talking about "going live" or "real users", the agent reminds you of any row still marked `pending`.

| Feature / decision | Why it is sensitive | Type of expert needed | Status |
|---|---|---|---|
| (filled in as the project grows) | | | pending |

## 13. Open questions

Things still to decide. Each line should be a real question, not a vague topic.

- ...
- ...

## 14. Change log

Track significant changes to this specification. Newest entry on top.

- YYYY-MM-DD — first draft.
