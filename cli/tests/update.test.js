import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, mkdir, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { update } from '../src/commands/update.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function makeTempDir() {
  return await mkdtemp(join(tmpdir(), 'virgilio-test-'));
}

async function seedFakeTemplate(contents) {
  const fakeTemplate = await makeTempDir();
  await mkdir(join(fakeTemplate, '.claude', 'skills'), { recursive: true });
  await mkdir(join(fakeTemplate, '.codex'), { recursive: true });
  await writeFile(join(fakeTemplate, 'CLAUDE.md'), contents.claudeMd ?? '# Virgilio (canonical)');
  await writeFile(join(fakeTemplate, 'AGENTS.md'), contents.agentsMd ?? '# Virgilio (canonical)');
  await writeFile(join(fakeTemplate, '.claude', 'skills', '.placeholder'), 'canonical');
  await writeFile(join(fakeTemplate, '.codex', 'config.toml'), 'canonical = true');
  await mkdir(join(fakeTemplate, 'templates'));
  await writeFile(join(fakeTemplate, 'templates', 'SPEC.md'), '# Template (canonical)');
  return fakeTemplate;
}

async function seedExistingInstall(dir, version) {
  await mkdir(join(dir, '.virgilio'));
  await writeFile(join(dir, '.virgilio', '.version'), version);
  await mkdir(join(dir, '.claude', 'skills'), { recursive: true });
  await mkdir(join(dir, '.codex'), { recursive: true });
  await writeFile(join(dir, 'CLAUDE.md'), '# Modified by user');
  await writeFile(join(dir, 'AGENTS.md'), '# Modified by user');
  await mkdir(join(dir, 'templates'));
  await writeFile(join(dir, 'templates', 'SPEC.md'), '# Template (stale)');
}

test('update returns 2 when no Virgilio install present', async () => {
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate({});
  try {
    const exitCode = await update(dir, { dryRun: false, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 2);
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});

test('update overwrites Virgilio files but preserves user SPEC.md and .git', async () => {
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate({ claudeMd: '# Virgilio (new)' });
  try {
    await seedExistingInstall(dir, '1.0.0');
    await writeFile(join(dir, 'SPEC.md'), '# User project spec — do not touch');
    await mkdir(join(dir, '.git'));
    await writeFile(join(dir, '.git', 'HEAD'), 'ref: refs/heads/main');

    const exitCode = await update(dir, { dryRun: false, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 0);

    const claudeMd = await readFile(join(dir, 'CLAUDE.md'), 'utf8');
    assert.equal(claudeMd, '# Virgilio (new)', 'CLAUDE.md must be overwritten with canonical content');

    const userSpec = await readFile(join(dir, 'SPEC.md'), 'utf8');
    assert.equal(userSpec, '# User project spec — do not touch', 'user SPEC.md must be untouched');

    const gitHead = await readFile(join(dir, '.git', 'HEAD'), 'utf8');
    assert.equal(gitHead, 'ref: refs/heads/main', '.git must be untouched');
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});

test('update rewrites .virgilio/.version to the new version', async () => {
  // Seed with a sentinel version that the CLI will never publish, so the test
  // can verify the rewrite happened regardless of the CLI's current version.
  const SEED_VERSION = '0.0.0-pretest';
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate({});
  try {
    await seedExistingInstall(dir, SEED_VERSION);
    const exitCode = await update(dir, { dryRun: false, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 0);
    const newVersion = (await readFile(join(dir, '.virgilio', '.version'), 'utf8')).trim();
    assert.notEqual(newVersion, SEED_VERSION, 'version marker must be rewritten');
    assert.match(newVersion, /^\d+\.\d+\.\d+/);
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});

test('update preserves user-added files inside .virgilio/ (e.g., .virgilio/exploration/)', async () => {
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate({});
  try {
    await seedExistingInstall(dir, '1.0.0');
    await mkdir(join(dir, '.virgilio', 'exploration'));
    await writeFile(join(dir, '.virgilio', 'exploration', 'notes.md'), '# Findings');
    const exitCode = await update(dir, { dryRun: false, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 0);
    const notes = await readFile(join(dir, '.virgilio', 'exploration', 'notes.md'), 'utf8');
    assert.equal(notes, '# Findings', 'user files inside .virgilio/ must survive update');
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});
