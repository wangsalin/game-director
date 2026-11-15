import test from 'node:test';
import assert from 'node:assert/strict';
import { createState, transition } from '../src/rules.js';

const start = () => transition(createState(), 'start');
const walk = (state, route) => route.reduce((s, a) => transition(s, a), state);
const winRoute = ['up', 'right', 'right', 'right', 'right', 'right', 'down'];

test('winning route requires actual collection and movement', () => {
  const won = walk(start(), winRoute);
  assert.equal(won.scene, 'won'); assert.equal(won.moves, 7);
  assert.equal(won.energy, 5); assert.deepEqual(won.collected, [0, 1]);
});
test('hazard loses; post-end movement cannot change the result', () => {
  const lost = walk(start(), ['down', 'right']);
  assert.equal(lost.scene, 'lost'); assert.equal(lost.reason, 'hazard');
  assert.deepEqual(transition(lost, 'up'), lost);
});
test('wall and edge do not spend energy or increment moves', () => {
  const initial = start();
  assert.equal(transition(initial, 'left').energy, 12);
  const blocked = walk(initial, ['right', 'right']);
  assert.deepEqual(blocked.position, [1, 2]); assert.equal(blocked.moves, 1);
});
test('pause freezes movement; resume and restart work', () => {
  const paused = transition(transition(start(), 'right'), 'pause');
  assert.deepEqual(transition(paused, 'up'), paused);
  assert.equal(transition(paused, 'pause').scene, 'playing');
  assert.deepEqual(transition(paused, 'restart'), start());
});
test('energy exhaustion ends the run', () => {
  const route = Array.from({ length: 12 }, (_, i) => i % 2 ? 'down' : 'up');
  const lost = walk(start(), route);
  assert.equal(lost.scene, 'lost'); assert.equal(lost.reason, 'energy'); assert.equal(lost.energy, 0);
});
test('exit without both signals is not a win; collection is not duplicated', () => {
  const atExit = walk(start(), ['up', 'up', 'right', 'right', 'right', 'right', 'right', 'down', 'down']);
  assert.equal(atExit.scene, 'playing'); assert.equal(atExit.collected.length, 0);
  const revisit = walk(start(), ['up', 'right', 'left', 'right']);
  assert.deepEqual(revisit.collected, [0]);
});
test('transitions never mutate the input or configuration-derived start', () => {
  const initial = start(); transition(initial, 'right');
  assert.deepEqual(initial, start());
});
