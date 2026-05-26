---
name: mobile-publishing-checklist
description: Use this when the primary device in SPEC.md is native mobile (Expo) and the user signals intent to share the app outside the development device — Expo Go preview, EAS internal build, TestFlight, Internal Testing, App Store, or Google Play. Enumerates the non-automatable barriers and routes them to expert consultation. For a non-programmer.
---

# Mobile Publishing Checklist

Enumerate the steps a non-programmer must complete (or delegate to a human expert) before a native mobile app can be installed on a real user's phone.

## When To Use

Invoke this skill when:

- the primary device in `SPEC.md` is native mobile (Expo) AND
- the user signals intent to share the app outside the development device — Expo Go preview, EAS preview build, TestFlight, Internal Testing, App Store, or Google Play.

This skill is normally invoked **through** `pre-publishing-checklist`, which dispatches to it when the primary device is mobile or both. For a web+mobile app, both checklists run.

## Why This Matters

Mobile publishing is fundamentally different from web publishing. A web app can be deployed by the agent in one push to Vercel. A mobile app requires:

- a paid developer account that only the user can create;
- platform-specific certificates the user must generate and protect;
- store-listing content the user must write;
- a human reviewer at Apple or Google;
- privacy disclosures the user must answer truthfully and personally.

This skill does not automate any of these. It lists the walls, explains the cost and time of each, and routes the user to expert consultation per the Expert Escalation policy in `AGENTS.md`. The output is informational: which walls exist, what is on the other side, and which experts close which gaps.

## Triage By Distribution Path

Before running the full checklist, identify the user's actual distribution goal:

```text
How do you want to share the app?
A. Expo Go QR (free, dev only) — the tester installs Expo Go, scans your QR, runs the JS bundle. No store, no certificates.
B. EAS preview build (free tier limits apply) — a real installable app, distributed by link to a small group.
C. TestFlight (iOS) + Internal Testing (Android) — the standard pre-release path. Real users, no public store review yet.
D. App Store and/or Google Play — full public release.

Each path adds barriers on top of the previous. A is closest to "free and immediate"; D is the full wall.
```

Then run only the sections marked with the chosen path's letter.

## The Checklist

### Apple Developer account (C · D)

- Apple Developer Program enrollment — **$99/year**, paid by the user with their own Apple ID.
- Personal vs Organization account decision. Organization needs a D-U-N-S number, additional verification, and can take ~2 weeks.
- Two-factor authentication on the Apple ID.

**Expert needed:** none for the enrolment itself. The personal vs company choice has tax implications worth discussing with an accountant if the app will receive payments.

### Google Play Developer account (C · D)

- Google Play Console — **$25 one-time**.
- Identity verification by Google.
- Closed Testing track configured if using Internal Testing for participants.

**Expert needed:** none. Faster path than Apple.

### Certificates and provisioning (B · C · D, iOS)

- iOS distribution certificate generated.
- App Store provisioning profile (for D) or Ad Hoc / Development profile (for B, C).
- Signing keys stored securely outside the repo.

**Expert needed:** a developer experienced with iOS code signing. This is the single most error-prone step for non-programmers. EAS can manage credentials automatically on its paid tier — without EAS, expert assistance is strongly recommended.

### Android signing (B · C · D)

- Android upload signing key generated (or Play App Signing enrolled).
- Key stored securely — **if lost, the app cannot be updated and must be re-published under a new identity.**

**Expert needed:** simpler than iOS; the user can do it with agent guidance, but the recovery rule for the key MUST be understood.

### App icon, splash, app name (B · C · D)

- App icon master image at 1024×1024.
- Splash screen design (background colour + foreground logo).
- Final app name as it appears in the launcher (Apple character limits apply: 30 chars).

**Expert needed:** a designer for production-quality assets. Placeholder icons are acceptable for B; not acceptable for D.

### Store listing (D)

- App name and subtitle.
- Short description (80 chars) and long description (4000 chars).
- Screenshots for each required device size: iPhone 6.7", iPad 12.9" (if iPad supported), Android phone, Android tablet (if tablet supported).
- Promotional video (optional, recommended).
- Keywords (100 chars total, iOS).
- Privacy policy URL.
- Support URL.
- Category and content rating.

**Expert needed:** a copywriter familiar with App Store Optimization (ASO) for keywords and descriptions. Translations for each target market are a separate Expert Escalation item per `AGENTS.md`.

### Privacy disclosures (D)

- Apple Privacy Nutrition Labels — the user must answer truthfully for every data type the app collects.
- Google Play Data Safety form — same principle, separate form.
- iOS App Tracking Transparency (ATT) prompt — required if any SDK in the app performs cross-app tracking (analytics, ads).

**Expert needed:** a privacy / GDPR consultant for any app that handles personal data, payments, or user-generated content. These answers have legal weight and cannot be "the agent's best guess".

### Push notifications (B · C · D, if applicable)

- Apple Push Notification service (APNs) auth key.
- Firebase Cloud Messaging server key for Android.
- Backend service configured to send to APNs / FCM (e.g. a Supabase Edge Function or external provider).

**Expert needed:** a backend developer experienced with mobile push delivery. Failure modes are subtle (silent delivery failures, throttling, message size limits) and visible only at scale.

### Deep links and universal links (D, if applicable)

- App-site association file hosted on the marketing domain.
- Custom URL scheme configured.
- End-to-end test: links open the installed app, not Safari / Chrome.

**Expert needed:** not strictly required, but error-prone for first-time setups.

### Review process expectations (C · D)

- **Apple App Review:** 24h–72h typical, can be longer. Common first-submission rejections: missing account-deletion flow (mandatory since 2022), unclear in-app purchase flow, AI-generated content without moderation, missing privacy policy.
- **Google Play review:** usually faster, automated checks first. Common rejections: missing data safety form, intrusive ads, broken core flow.
- **Plan for at least one round of rejection on first Apple submission.** Allow a week of buffer in the participant test schedule.

**Expert needed:** a developer experienced with App Review policy. Rejections are technical and require a specific response within the App Review portal.

## Output

After running the relevant sections of the checklist:

```text
Mobile publishing readiness:
- X items the user can complete with my guidance
- Y items require expert consultation (listed below by expert type)
- Z items already done

Experts to engage:
- iOS code-signing developer: <yes / no>
- Designer: <yes / no>
- Privacy / GDPR consultant: <yes / no>
- Mobile push backend: <yes / no>
- App-Store-policy developer: <yes / no>

Estimated time to first installable build: <hours / days>
Estimated time to App Store / Play Store live: <weeks>

Do you want me to start a slice for any of the items I can guide?
Or do you prefer to schedule expert consultations first?
```

Add a row to `SPEC.md` Section 12 (Pending external review) for every item flagged as "expert needed". The user changes the Status field manually after the real consultation. Until the table for the going-live scope is clean (or every row marked reviewed), the agent must remind the user before any "we go live to real users" discussion.

## Anti-Patterns

- Pretending to "fix" certificate issues by guessing flags. If certs are wrong, ask the user to consult an iOS-experienced developer.
- Writing store-listing copy without the user's input. The voice of the app is theirs, not the agent's.
- Filling in privacy disclosures with defaults. These have legal weight and require the user's truthful answer.
- Treating EAS paid features as required. The checklist works without EAS — the manual signing path is longer but free.
- Letting the user think Expo Go is a "publishing path" for real users. Expo Go is a dev tool. Real users on real devices begin at path B (EAS preview) at the earliest.

## When To Skip

- The primary device in `SPEC.md` is web only. Use `pre-publishing-checklist` exclusively.
- The user is testing on their own development device with Expo Go. No checklist required.

## Limitations

This checklist is informational. Even when every item is checked, an app's review outcome at Apple or Google cannot be predicted with certainty. Per the Expert Escalation policy, an experienced mobile developer should review the build before public submission.
