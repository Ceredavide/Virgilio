#!/usr/bin/env node
import { init } from '../src/commands/init.js';
import { update } from '../src/commands/update.js';
import { messages } from '../src/lib/messages.js';

const args = process.argv.slice(2);
const command = args[0];
const flags = parseFlags(args.slice(1));

function parseFlags(rest) {
  const flags = { only: null, dryRun: false };
  for (const arg of rest) {
    if (arg === '--dry-run') flags.dryRun = true;
    else if (arg.startsWith('--only=')) flags.only = arg.split('=')[1];
  }
  return flags;
}

async function main() {
  try {
    switch (command) {
      case 'init':
        process.exit(await init(process.cwd(), flags));
      case 'update':
        process.exit(await update(process.cwd(), flags));
      case undefined:
      case '--help':
      case '-h':
        console.log(messages.help());
        process.exit(0);
      default:
        console.error(messages.unknownCommand(command));
        process.exit(1);
    }
  } catch (err) {
    console.error(messages.unexpectedError(err));
    process.exit(99);
  }
}

main();
