import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, mkdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { detectState } from '../src/lib/detect.js';

async function makeTempDir() {
  return await mkdtemp(join(tmpdir(), 'virgilio-test-'));
}

test('detectState returns "fresh" on empty directory', async () => {
  const dir = await makeTempDir();
  try {
    const state = await detectState(dir);
    assert.equal(state, 'fresh');
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('detectState returns "existing-project" when package.json present', async () => {
  const dir = await makeTempDir();
  try {
    await writeFile(join(dir, 'package.json'), '{}');
    const state = await detectState(dir);
    assert.equal(state, 'existing-project');
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('detectState returns "existing-project" when app.json present', async () => {
  const dir = await makeTempDir();
  try {
    await writeFile(join(dir, 'app.json'), '{}');
    const state = await detectState(dir);
    assert.equal(state, 'existing-project');
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('detectState returns "has-virgilio" when .virgilio/.version present', async () => {
  const dir = await makeTempDir();
  try {
    await mkdir(join(dir, '.virgilio'));
    await writeFile(join(dir, '.virgilio', '.version'), '0.1.0');
    const state = await detectState(dir);
    assert.equal(state, 'has-virgilio');
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('detectState returns "has-virgilio" when .claude/skills/spec-coauthor exists (legacy install without .version)', async () => {
  const dir = await makeTempDir();
  try {
    await mkdir(join(dir, '.claude', 'skills', 'spec-coauthor'), { recursive: true });
    const state = await detectState(dir);
    assert.equal(state, 'has-virgilio');
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('detectState prefers has-virgilio over existing-project when both signals present', async () => {
  const dir = await makeTempDir();
  try {
    await writeFile(join(dir, 'package.json'), '{}');
    await mkdir(join(dir, '.virgilio'));
    await writeFile(join(dir, '.virgilio', '.version'), '0.1.0');
    const state = await detectState(dir);
    assert.equal(state, 'has-virgilio', 'has-virgilio must take precedence');
  } finally {
    await rm(dir, { recursive: true });
  }
});
