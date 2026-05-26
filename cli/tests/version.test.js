import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { writeMarker, readMarker } from '../src/lib/version.js';

async function makeTempDir() {
  return await mkdtemp(join(tmpdir(), 'virgilio-test-'));
}

test('writeMarker creates .virgilio/.version with given version', async () => {
  const dir = await makeTempDir();
  try {
    await writeMarker(dir, '1.2.3');
    const content = await readFile(join(dir, '.virgilio', '.version'), 'utf8');
    assert.equal(content.trim(), '1.2.3');
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('readMarker returns null when marker file does not exist', async () => {
  const dir = await makeTempDir();
  try {
    const version = await readMarker(dir);
    assert.equal(version, null);
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('readMarker returns trimmed version string when marker exists', async () => {
  const dir = await makeTempDir();
  try {
    await writeMarker(dir, '1.2.3');
    const version = await readMarker(dir);
    assert.equal(version, '1.2.3');
  } finally {
    await rm(dir, { recursive: true });
  }
});

test('writeMarker overwrites an existing marker', async () => {
  const dir = await makeTempDir();
  try {
    await writeMarker(dir, '1.0.0');
    await writeMarker(dir, '2.0.0');
    const version = await readMarker(dir);
    assert.equal(version, '2.0.0');
  } finally {
    await rm(dir, { recursive: true });
  }
});
