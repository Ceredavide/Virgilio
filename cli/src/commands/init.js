import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFile } from 'node:fs/promises';
import { checkNodeVersion, checkGit } from '../lib/prereq.js';
import { detectState } from '../lib/detect.js';
import { copyTree } from '../lib/copy.js';
import { writeMarker } from '../lib/version.js';
import { messages } from '../lib/messages.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const DEFAULT_TEMPLATE_ROOT = join(__dirname, '..', '..', 'template');

async function getCliVersion() {
  const pkgPath = join(__dirname, '..', '..', 'package.json');
  const pkg = JSON.parse(await readFile(pkgPath, 'utf8'));
  return pkg.version;
}

function excludeListForOnly(only) {
  if (only === 'claude') return ['.codex'];
  if (only === 'codex') return ['.claude'];
  return [];
}

export async function init(cwd, options = {}) {
  const { only = null, dryRun = false, _templateRoot = DEFAULT_TEMPLATE_ROOT } = options;

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
  if (state === 'has-virgilio') {
    console.error(messages.errInitOnExisting());
    return 2;
  }

  if (dryRun) {
    console.log('--dry-run: nessun file verrà scritto.');
    console.log(messages.initSummary(['(verrebbe creato il contenuto di template/)']));
    return 0;
  }

  try {
    await copyTree(_templateRoot, cwd, { exclude: excludeListForOnly(only) });
  } catch (err) {
    console.error(messages.errCopyFailed());
    return 3;
  }

  const version = await getCliVersion();
  await writeMarker(cwd, version);

  const installedPaths = [];
  if (only !== 'codex') installedPaths.push('.claude/');
  if (only !== 'claude') installedPaths.push('.codex/');
  installedPaths.push('CLAUDE.md', 'AGENTS.md', 'templates/', '.virgilio/.version');

  console.log(messages.initSummary(installedPaths));
  console.log();
  console.log(messages.superpowersReminder());
  console.log();
  console.log(state === 'existing-project' ? messages.initNextStepsExisting() : messages.initNextStepsFresh());

  return 0;
}
