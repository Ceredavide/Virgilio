#!/usr/bin/env node
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { copyTree } from '../src/lib/copy.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..', '..');
const TEMPLATE_DIR = resolve(__dirname, '..', 'template');

const VIRGILIO_FILES = ['.claude', '.codex', 'CLAUDE.md', 'AGENTS.md', 'templates'];

// Local development artefacts that must NEVER end up in the published tarball.
// All of these are gitignored at the repo root, but the snapshot walks the
// filesystem (not the git index), so we have to filter explicitly here.
//
// - __pycache__ / .DS_Store / node_modules: local cache / OS / dependency dirs.
// - worktrees: git worktree state lives at .claude/worktrees/ in this repo. If
//   the snapshot walked into it, the tarball would include the entire dev
//   workspace (hundreds of files, ~200 kB+). Disastrous for an installer.
const SNAPSHOT_EXCLUDE = [
  '__pycache__',
  '.DS_Store',
  'node_modules',
  'worktrees',
];

async function safeRm(path) {
  try {
    await rm(path, { recursive: true, force: true });
  } catch {
    // ignore
  }
}

// stat() follows symlinks, so symlinked files are resolved to plain files.
// Mirrors the symlink-resolution behaviour inside copyTree for single-file
// top-level entries like CLAUDE.md -> AGENTS.md.
async function copyEntry(src, dst) {
  const info = await stat(src);
  if (info.isDirectory()) {
    await copyTree(src, dst, { exclude: SNAPSHOT_EXCLUDE });
  } else {
    await mkdir(dirname(dst), { recursive: true });
    const content = await readFile(src);
    await writeFile(dst, content);
  }
}

async function main() {
  console.log(`Snapshot source: ${REPO_ROOT}`);
  console.log(`Snapshot destination: ${TEMPLATE_DIR}`);

  await safeRm(TEMPLATE_DIR);

  for (const name of VIRGILIO_FILES) {
    const src = join(REPO_ROOT, name);
    const dst = join(TEMPLATE_DIR, name);
    try {
      await copyEntry(src, dst);
      console.log(`  + ${name}`);
    } catch (err) {
      if (err.code === 'ENOENT') {
        console.log(`  ! ${name} (source not found, skipped)`);
      } else {
        throw err;
      }
    }
  }

  // Re-create the .gitkeep that safeRm(TEMPLATE_DIR) removed at the start.
  // Without this, every snapshot run shows .gitkeep as deleted in `git status`,
  // because cli/template/* is gitignored except this single tracked file.
  await writeFile(join(TEMPLATE_DIR, '.gitkeep'), '');

  console.log('Snapshot complete.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
