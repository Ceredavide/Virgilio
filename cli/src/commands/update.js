import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFile, rm } from 'node:fs/promises';
import { checkNodeVersion, checkGit } from '../lib/prereq.js';
import { detectState } from '../lib/detect.js';
import { copyTree } from '../lib/copy.js';
import { readMarker, writeMarker } from '../lib/version.js';
import { messages } from '../lib/messages.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const DEFAULT_TEMPLATE_ROOT = join(__dirname, '..', '..', 'template');

const VIRGILIO_OWNED_PATHS = ['.claude', '.codex', 'CLAUDE.md', 'AGENTS.md', 'templates'];

async function getCliVersion() {
  const pkgPath = join(__dirname, '..', '..', 'package.json');
  const pkg = JSON.parse(await readFile(pkgPath, 'utf8'));
  return pkg.version;
}

async function safeRm(path) {
  try {
    await rm(path, { recursive: true, force: true });
  } catch {
    // ignore: the path may not exist or may be a file
  }
}

export async function update(cwd, options = {}) {
  const { dryRun = false, _templateRoot = DEFAULT_TEMPLATE_ROOT } = options;

  const nodeCheck = checkNodeVersion();
  if (!nodeCheck.ok) {
    console.error(messages.errNodeVersion(nodeCheck.version));
    return 1;
  }

  const gitCheck = checkGit();
  if (!gitCheck.ok) {
    console.error(messages.errGitMissing());
    return 1;
  }

  const state = await detectState(cwd);
  if (state !== 'has-virgilio') {
    console.error(messages.errUpdateOnFresh());
    return 2;
  }

  const fromVersion = (await readMarker(cwd)) ?? 'unknown';
  const toVersion = await getCliVersion();

  if (dryRun) {
    console.log('--dry-run: nessun file verrà scritto.');
    console.log(`Verrebbe aggiornato da ${fromVersion} a ${toVersion}.`);
    console.log('Path che verrebbero rinnovati:');
    for (const p of VIRGILIO_OWNED_PATHS) console.log('  - ' + p);
    return 0;
  }

  try {
    for (const owned of VIRGILIO_OWNED_PATHS) {
      await safeRm(join(cwd, owned));
    }
    await copyTree(_templateRoot, cwd);
  } catch {
    console.error(messages.errCopyFailed());
    return 3;
  }

  await writeMarker(cwd, toVersion);

  console.log(messages.updateSummary(fromVersion, toVersion));
  return 0;
}
