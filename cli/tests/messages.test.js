import { test } from 'node:test';
import assert from 'node:assert/strict';
import { messages } from '../src/lib/messages.js';

test('messages exposes all required keys', () => {
  const required = [
    'help',
    'unknownCommand',
    'unexpectedError',
    'errNodeVersion',
    'errGitMissing',
    'errInitOnExisting',
    'errUpdateOnFresh',
    'errCopyFailed',
    'initSummary',
    'initNextStepsFresh',
    'initNextStepsExisting',
    'superpowersReminder',
    'updateSummary',
  ];
  for (const key of required) {
    assert.equal(typeof messages[key], 'function', `messages.${key} must be a function`);
  }
});

test('messages.errNodeVersion includes the version received and the required minimum', () => {
  const out = messages.errNodeVersion('16.20.0');
  assert.match(out, /16\.20\.0/);
  assert.match(out, /18/);
});

test('messages.errInitOnExisting routes to update', () => {
  const out = messages.errInitOnExisting();
  assert.match(out, /npx @ceredavide\/virgilio update/);
});

test('messages.errUpdateOnFresh routes to init', () => {
  const out = messages.errUpdateOnFresh();
  assert.match(out, /npx @ceredavide\/virgilio init/);
});

test('messages.superpowersReminder mentions Superpowers and a URL', () => {
  const out = messages.superpowersReminder();
  assert.match(out, /Superpowers/);
  assert.match(out, /https:\/\/github\.com\/obra\/superpowers/);
});

test('messages.updateSummary includes from-to version transition', () => {
  const out = messages.updateSummary('1.0.0', '1.2.3');
  assert.match(out, /1\.0\.0/);
  assert.match(out, /1\.2\.3/);
});
