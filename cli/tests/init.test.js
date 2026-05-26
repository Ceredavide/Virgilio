import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, mkdir, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { init } from '../src/commands/init.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const CLI_ROOT = join(__dirname, '..');

async function makeTempDir() {
  return await mkdtemp(join(tmpdir(), 'virgilio-test-'));
}

async function seedFakeTemplate() {
  const fakeTemplate = await makeTempDir();
  await mkdir(join(fakeTemplate, '.claude', 'skills'), { recursive: true });
  await mkdir(join(fakeTemplate, '.codex'), { recursive: true });
  await writeFile(join(fakeTemplate, '.claude', 'skills', '.placeholder'), '');
  await writeFile(join(fakeTemplate, '.codex', 'config.toml'), 'fake = true');
  await writeFile(join(fakeTemplate, 'CLAUDE.md'), '# Virgilio');
  await writeFile(join(fakeTemplate, 'AGENTS.md'), '# Virgilio');
  await mkdir(join(fakeTemplate, 'templates'));
  await writeFile(join(fakeTemplate, 'templates', 'SPEC.md'), '# Template');
  return fakeTemplate;
}

test('init returns 0 and creates files on fresh directory', async () => {
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate();
  try {
    const exitCode = await init(dir, { only: null, dryRun: false, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 0);
    const claudeMd = await readFile(join(dir, 'CLAUDE.md'), 'utf8');
    assert.equal(claudeMd, '# Virgilio');
    const marker = await readFile(join(dir, '.virgilio', '.version'), 'utf8');
    assert.match(marker, /^\d+\.\d+\.\d+/);
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});

test('init returns 2 when Virgilio already installed', async () => {
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate();
  try {
    await mkdir(join(dir, '.virgilio'));
    await writeFile(join(dir, '.virgilio', '.version'), '0.1.0');
    const exitCode = await init(dir, { only: null, dryRun: false, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 2);
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});

test('init with --only=claude skips .codex/', async () => {
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate();
  try {
    const exitCode = await init(dir, { only: 'claude', dryRun: false, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 0);
    let codexExists = true;
    try {
      await readFile(join(dir, '.codex', 'config.toml'));
    } catch {
      codexExists = false;
    }
    assert.equal(codexExists, false, '.codex/ must be skipped with --only=claude');
    const claudeMd = await readFile(join(dir, 'CLAUDE.md'), 'utf8');
    assert.equal(claudeMd, '# Virgilio');
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});

test('init with --dry-run does not create files', async () => {
  const dir = await makeTempDir();
  const fakeTemplate = await seedFakeTemplate();
  try {
    const exitCode = await init(dir, { only: null, dryRun: true, _templateRoot: fakeTemplate });
    assert.equal(exitCode, 0);
    let createdAnything = true;
    try {
      await readFile(join(dir, 'CLAUDE.md'));
    } catch {
      createdAnything = false;
    }
    assert.equal(createdAnything, false, '--dry-run must not create files');
  } finally {
    await rm(dir, { recursive: true });
    await rm(fakeTemplate, { recursive: true });
  }
});
