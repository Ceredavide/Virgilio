import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { join } from 'node:path';

const MARKER_DIR = '.virgilio';
const MARKER_FILE = '.version';

export async function writeMarker(cwd, version) {
  const dir = join(cwd, MARKER_DIR);
  await mkdir(dir, { recursive: true });
  await writeFile(join(dir, MARKER_FILE), version + '\n');
}

export async function readMarker(cwd) {
  try {
    const content = await readFile(join(cwd, MARKER_DIR, MARKER_FILE), 'utf8');
    return content.trim();
  } catch {
    return null;
  }
}
