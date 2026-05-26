import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, mkdir, readFile, rm, symlink, lstat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { copyTree } from '../src/lib/copy.js';

async function makeTempDir() {
  return await mkdtemp(join(tmpdir(), 'virgilio-test-'));
}

test('copyTree copies a plain file', async () => {
  const src = await makeTempDir();
  const dst = await makeTempDir();
  try {
    await writeFile(join(src, 'a.txt'), 'hello');
    await copyTree(src, dst);
    const content = await readFile(join(dst, 'a.txt'), 'utf8');
    assert.equal(content, 'hello');
  } finally {
    await rm(src, { recursive: true });
    await rm(dst, { recursive: true });
  }
});

test('copyTree copies nested directories', async () => {
  const src = await makeTempDir();
  const dst = await makeTempDir();
  try {
    await mkdir(join(src, 'sub', 'deep'), { recursive: true });
    await writeFile(join(src, 'sub', 'deep', 'b.txt'), 'world');
    await copyTree(src, dst);
    const content = await readFile(join(dst, 'sub', 'deep', 'b.txt'), 'utf8');
    assert.equal(content, 'world');
  } finally {
    await rm(src, { recursive: true });
    await rm(dst, { recursive: true });
  }
});

test('copyTree resolves symlinks to file content', async () => {
  const src = await makeTempDir();
  const dst = await makeTempDir();
  try {
    await writeFile(join(src, 'original.txt'), 'real content');
    await symlink('original.txt', join(src, 'link.txt'));
    await copyTree(src, dst);
    const stat = await lstat(join(dst, 'link.txt'));
    assert.equal(stat.isSymbolicLink(), false, 'destination must be a plain file, not a symlink');
    const content = await readFile(join(dst, 'link.txt'), 'utf8');
    assert.equal(content, 'real content');
  } finally {
    await rm(src, { recursive: true });
    await rm(dst, { recursive: true });
  }
});

test('copyTree skips paths matched by exclude list', async () => {
  const src = await makeTempDir();
  const dst = await makeTempDir();
  try {
    await mkdir(join(src, 'keep'));
    await mkdir(join(src, 'skip'));
    await writeFile(join(src, 'keep', 'a.txt'), 'a');
    await writeFile(join(src, 'skip', 'b.txt'), 'b');
    await copyTree(src, dst, { exclude: ['skip'] });
    const aContent = await readFile(join(dst, 'keep', 'a.txt'), 'utf8');
    assert.equal(aContent, 'a');
    let skipExists = true;
    try {
      await readFile(join(dst, 'skip', 'b.txt'));
    } catch {
      skipExists = false;
    }
    assert.equal(skipExists, false, 'excluded path must not be copied');
  } finally {
    await rm(src, { recursive: true });
    await rm(dst, { recursive: true });
  }
});

test('copyTree creates destination directory if missing', async () => {
  const src = await makeTempDir();
  const dst = join(await makeTempDir(), 'new-subdir');
  try {
    await writeFile(join(src, 'a.txt'), 'hello');
    await copyTree(src, dst);
    const content = await readFile(join(dst, 'a.txt'), 'utf8');
    assert.equal(content, 'hello');
  } finally {
    await rm(src, { recursive: true });
    await rm(dst, { recursive: true });
  }
});
