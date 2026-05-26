---
name: troubleshooting-guide
description: Use this when the user reports an error, bug, broken setup, failed command, unexpected behavior, failed test, or when the app does not work.
---

# Troubleshooting Guide

Help a non-programmer understand and fix problems step by step.

This skill is the non-programmer troubleshooting workflow. Use it when manual behavioral testing reveals an error or unexpected behavior. It explains the likely cause and proposed fix in plain language a non-programmer can evaluate without reading code or stack traces.

Use this skill when the user reports an error, bug, broken setup, failed command, unexpected behaviour, or when the application does not work — and the user is a non-programmer who cannot read code-level diagnostics. If Superpowers `systematic-debugging` is available, invoke it internally when a first fix attempt has failed (see Process step 7). This skill (`troubleshooting-guide`) controls the user-facing explanation and the one-fix-at-a-time recovery loop; `systematic-debugging` provides the internal root-cause discipline.

## Rules

- Do not make large unrelated changes.
- Explain the problem in simple language.
- Investigate before changing code.
- Fix one likely cause at a time.
- Prefer the smallest safe change.
- After each fix, explain how the user can test it.
- If the issue is caused by external tools, accounts, permissions, deployment, or infrastructure, say so clearly.
- Do not ask the user to approve low-level technical fixes they cannot reasonably evaluate.
- Choose the smallest safe fix, explain it simply, and keep the user's testing steps concrete.

## Process

1. Identify the error or symptom.
2. Explain what it probably means in simple language.
3. Inspect the relevant files, commands, logs, or configuration.
4. Propose one likely fix.
5. Apply the smallest safe change.
6. Tell the user exactly how to test again.
7. If the first fix does not work, do not propose another fix immediately. Invoke `superpowers:systematic-debugging` internally to perform a root-cause investigation (read errors carefully, reproduce consistently, trace data flow). Translate the findings into plain language for the user; do not surface phase numbers or technical terminology unless asked. Then propose the next fix based on the root cause, not on the next likely guess.

## Local Testing Guidance

After a fix, provide concrete testing instructions.

Include when possible:

- the command to run, only if the user truly needs to run one;
- the local URL to open;
- the page or feature to test;
- the expected result;
- what error or behavior the user should report if it still fails.

## Mobile Failure Modes

When the project's primary device is native mobile (Expo), the most common failures are not in the JavaScript code itself. Recognise them before proposing a code fix.

### Expo Go cannot connect to the dev server

- **Symptom:** Expo Go shows "No connection" or hangs on the splash screen after scanning the QR.
- **Likely cause:** the phone and the dev machine are on different Wi-Fi networks, or the dev machine's firewall blocks the Metro port.
- **First thing to try:** confirm both devices are on the same Wi-Fi (and not a guest network that isolates clients). If still failing, restart the Expo dev server with the tunnel option — slower but bypasses local-network setup.

### Metro bundler stalls or fails to start

- **Symptom:** the terminal shows the Metro startup banner but no QR appears, or the bundler errors with "Unable to resolve module".
- **Likely cause:** stale cache after a dependency change, or duplicate Metro instances on the same port.
- **First thing to try:** stop all running Expo processes, then restart with the cache-clear flag (`expo start --clear`). For "Unable to resolve module", verify the dependency is installed in `package.json`.

### App reloads with old code after a change

- **Symptom:** edits in the editor are saved but the app shows the previous version.
- **Likely cause:** Fast Refresh is disabled, or the JS bundle in Expo Go is cached from a different session.
- **First thing to try:** in Expo Go, shake the device (or press D in the simulator) to open the dev menu, then tap "Reload". If still stale, close and reopen Expo Go.

### Expo SDK version mismatch

- **Symptom:** Expo Go refuses to open the project with an "SDK version" error.
- **Likely cause:** the project's Expo SDK is newer or older than the installed Expo Go on the phone.
- **First thing to try:** update Expo Go on the phone. If the project uses a very old SDK, the phone may need an older Expo Go from a sideloaded download — flag this as expert escalation and do not attempt downgrade automation.

### Permission denied on simulator (camera, location, push)

- **Symptom:** a feature that needs a capability silently fails or returns an empty result.
- **Likely cause:** the simulator denied the permission, or the permission descriptor is missing from `app.json`.
- **First thing to try:** verify the permission entry in `app.json` (e.g. iOS `NSCameraUsageDescription`). On the simulator, reset content and settings to re-prompt.

### Native crash (no JavaScript stack trace)

- **Symptom:** the app closes immediately without an error toast or red error overlay.
- **Likely cause:** a native module is failing — most often a third-party library that includes native code.
- **First thing to try:** **stop.** Native crashes are escalation territory. Do not attempt a code fix from JavaScript. Report the crash to the user in plain language, explain that it likely involves native code outside JavaScript, and recommend consulting an experienced developer per the Expert Escalation policy in `AGENTS.md`.

## Output

After troubleshooting, provide:

- what was wrong;
- what was changed;
- how to test;
- what to do if the problem continues.

When possible, start or verify the local app yourself and give the user the URL to open (or, for mobile projects, the QR to scan in Expo Go).
