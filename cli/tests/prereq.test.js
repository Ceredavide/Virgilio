import { test } from 'node:test';
import assert from 'node:assert/strict';
import { checkNodeVersion, checkGit } from '../src/lib/prereq.js';

test('checkNodeVersion returns ok=true on Node >=18', () => {
  const result = checkNodeVersion();
  assert.equal(result.ok, true, 'tests must run on Node >=18');
  assert.match(result.version, /^\d+\.\d+\.\d+/);
});

test('checkNodeVersion returns shape {ok, version}', () => {
  const result = checkNodeVersion();
  assert.equal(typeof result.ok, 'boolean');
  assert.equal(typeof result.version, 'string');
});

test('checkGit returns ok=true on dev machine with Git installed', () => {
  const result = checkGit();
  assert.equal(result.ok, true, 'dev machine must have Git installed');
  assert.match(result.version, /git version/);
});

test('checkGit returns shape {ok, version}', () => {
  const result = checkGit();
  assert.equal(typeof result.ok, 'boolean');
  assert.ok(result.version === null || typeof result.version === 'string');
});
