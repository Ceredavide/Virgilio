import { readdir, mkdir, copyFile, readFile, writeFile, stat } from 'node:fs/promises';
import { join } from 'node:path';

export async function copyTree(src, dst, options = {}) {
  const exclude = options.exclude ?? [];

  await mkdir(dst, { recursive: true });

  const entries = await readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    if (exclude.includes(entry.name)) continue;

    const srcPath = join(src, entry.name);
    const dstPath = join(dst, entry.name);

    if (entry.isSymbolicLink()) {
      const realStat = await stat(srcPath);
      if (realStat.isDirectory()) {
        await copyTree(srcPath, dstPath, options);
      } else {
        const content = await readFile(srcPath);
        await writeFile(dstPath, content);
      }
    } else if (entry.isDirectory()) {
      await copyTree(srcPath, dstPath, options);
    } else if (entry.isFile()) {
      await copyFile(srcPath, dstPath);
    }
  }
}
