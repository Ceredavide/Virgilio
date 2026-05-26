#!/usr/bin/env node
// Cross-platform test runner. Plain `node --test tests/*.test.js` works on
// POSIX shells (the shell expands the glob) but fails on Windows cmd /
// PowerShell (the asterisk is passed literally and node cannot find the file).
// We sidestep shell expansion by listing the test files ourselves.

import { spawnSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const testsDir = join(__dirname, '..', 'tests');

const tests = readdirSync(testsDir)
  .filter((name) => name.endsWith('.test.js'))
  .map((name) => join(testsDir, name));

if (tests.length === 0) {
  console.error(`No test files found under ${testsDir}.`);
  process.exit(1);
}

const result = spawnSync(process.execPath, ['--test', ...tests], {
  stdio: 'inherit',
});

process.exit(result.status ?? 1);
