import { CONFIG } from '../config.js';
import { createState, transition } from './rules.js';

const $ = selector => document.querySelector(selector);
const canvas = $('#board');
const context = canvas.getContext('2d');
const saveKey = 'game-director.beacon-path.v1';
let state = createState();
let wins = 0;
let storageWarning = '';
try {
  const saved = Number(localStorage.getItem(saveKey) ?? '0');
  if (Number.isSafeInteger(saved) && saved >= 0) wins = saved;
  else storageWarning = '存档无效，已从零记录。';
} catch { storageWarning = '浏览器未允许保存，本次仍可游玩。'; }

function act(action) {
  const previous = state.scene;
  state = transition(state, action);
  if (previous !== 'won' && state.scene === 'won') {
    wins += 1;
    try { localStorage.setItem(saveKey, String(wins)); }
    catch { storageWarning = '本次胜利未能保存。'; }
  }
  render();
}

function render() {
  document.title = `${CONFIG.title} · 可玩原型`;
  $('#title').textContent = CONFIG.title;
  $('#scene').textContent = ({ title: '待开始', playing: '进行中', paused: '已暂停', won: '已通关', lost: '未通关' })[state.scene];
  $('#stats').textContent = `能量 ${state.energy} / 信号 ${state.collected.length}/${CONFIG.signals.length} / 步数 ${state.moves}`;
  $('#message').textContent = state.message;
  $('#record').textContent = `本机累计通关 ${wins} 次。${storageWarning}`;
  $('#start').hidden = state.scene !== 'title';
  $('#restart').hidden = state.scene === 'title';
  $('#pause').hidden = !['playing', 'paused'].includes(state.scene);
  $('#pause').textContent = state.scene === 'paused' ? '继续' : '暂停';
  document.querySelectorAll('[data-move]').forEach(button => { button.disabled = state.scene !== 'playing'; });
  const tile = Math.min(canvas.width / CONFIG.width, canvas.height / CONFIG.height);
  context.clearRect(0, 0, canvas.width, canvas.height);
  for (let y = 0; y < CONFIG.height; y++) for (let x = 0; x < CONFIG.width; x++) {
    context.fillStyle = (x + y) % 2 ? '#e4edf5' : '#f2f6fa';
    context.fillRect(x * tile + 3, y * tile + 3, tile - 6, tile - 6);
  }
  function mark(point, color, text) {
    const [x, y] = point;
    context.fillStyle = color;
    context.fillRect(x * tile + 14, y * tile + 14, tile - 28, tile - 28);
    context.fillStyle = '#fff'; context.textAlign = 'center'; context.textBaseline = 'middle';
    context.font = `bold ${Math.round(tile * .3)}px system-ui`;
    context.fillText(text, (x + .5) * tile, (y + .5) * tile);
  }
  CONFIG.walls.forEach(point => mark(point, '#53677c', '岩'));
  CONFIG.hazards.forEach(point => mark(point, '#af3f4b', '风'));
  mark(CONFIG.goal, '#277658', '灯');
  CONFIG.signals.forEach((point, index) => { if (!state.collected.includes(index)) mark(point, '#90651c', '片'); });
  mark(state.position, '#216ab0', '你');
  if (state.scene !== 'playing') {
    context.fillStyle = 'rgba(245,248,252,.83)'; context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = '#20374f'; context.font = 'bold 40px system-ui';
    context.fillText(({ title: '准备出发', paused: '已暂停', won: '信标点亮', lost: '再试一次' })[state.scene], canvas.width / 2, canvas.height / 2);
  }
}

$('#start').addEventListener('click', () => { act('start'); canvas.focus(); });
$('#restart').addEventListener('click', () => { act('restart'); canvas.focus(); });
$('#pause').addEventListener('click', () => act('pause'));
document.querySelectorAll('[data-move]').forEach(button => button.addEventListener('click', () => act(button.dataset.move)));
const keys = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', w: 'up', s: 'down', a: 'left', d: 'right', p: 'pause', r: 'restart' };
window.addEventListener('keydown', event => {
  if (event.ctrlKey || event.altKey || event.metaKey || event.repeat) return;
  const action = keys[event.key] ?? keys[event.key.toLowerCase()];
  if (action) { event.preventDefault(); act(action); }
});
window.addEventListener('blur', () => { if (state.scene === 'playing') act('pause'); });
// 只读观测口；测试通过真实输入推进，不提供设置位置/强制胜利的方法。
Object.defineProperty(window, 'game', { value: Object.freeze({
  getState: () => ({ ...structuredClone(state), wins, storageWarning })
}), writable: false });
render();
