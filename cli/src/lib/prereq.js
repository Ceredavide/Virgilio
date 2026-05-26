import { spawnSync } from 'node:child_process';

export function checkNodeVersion() {
  const version = process.versions.node;
  const major = parseInt(version.split('.')[0], 10);
  return { ok: major >= 18, version };
}

export function checkGit() {
  try {
    const result = spawnSync('git', ['--version'], { encoding: 'utf8' });
    if (result.status === 0 && result.stdout) {
      return { ok: true, version: result.stdout.trim() };
    }
    return { ok: false, version: null };
  } catch {
    return { ok: false, version: null };
  }
}
