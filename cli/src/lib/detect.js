import { access } from 'node:fs/promises';
import { join } from 'node:path';

const PROJECT_MARKERS = [
  'package.json',
  'app.json',
  'pyproject.toml',
  'Gemfile',
  'pubspec.yaml',
];

const VIRGILIO_MARKERS = [
  '.virgilio/.version',
  '.claude/skills/spec-coauthor',
];

async function exists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

export async function detectState(cwd) {
  for (const marker of VIRGILIO_MARKERS) {
    if (await exists(join(cwd, marker))) return 'has-virgilio';
  }
  for (const marker of PROJECT_MARKERS) {
    if (await exists(join(cwd, marker))) return 'existing-project';
  }
  return 'fresh';
}
