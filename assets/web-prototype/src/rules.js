import { CONFIG } from '../config.js';

const same = (a, b) => a[0] === b[0] && a[1] === b[1];
const directions = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

export function createState() {
  return { scene: 'title', position: [...CONFIG.start], energy: CONFIG.energy,
    collected: [], moves: 0, message: '收集两枚信号片，到达右侧灯塔。', reason: null };
}

// 每次返回新状态；无渲染、存储、计时器或平台 API。
export function transition(state, action) {
  const next = structuredClone(state);
  if (action === 'start' || action === 'restart') return { ...createState(), scene: 'playing' };
  if (action === 'pause' && ['playing', 'paused'].includes(state.scene)) {
    next.scene = state.scene === 'playing' ? 'paused' : 'playing';
    return next;
  }
  if (state.scene !== 'playing' || !directions[action]) return next;
  const [dx, dy] = directions[action];
  const target = [state.position[0] + dx, state.position[1] + dy];
  if (target[0] < 0 || target[0] >= CONFIG.width || target[1] < 0 || target[1] >= CONFIG.height ||
      CONFIG.walls.some(point => same(point, target))) {
    next.message = '前方不能通行，不消耗能量。';
    return next;
  }
  next.position = target;
  next.energy -= 1;
  next.moves += 1;
  const signal = CONFIG.signals.findIndex(point => same(point, target));
  if (signal >= 0 && !next.collected.includes(signal)) next.collected.push(signal);
  next.message = `已收集 ${next.collected.length}/${CONFIG.signals.length} 枚信号片。`;
  // 结算顺序：危险区 -> 能量耗尽 -> 抵达出口。最后一格能量不构成胜利。
  if (CONFIG.hazards.some(point => same(point, target))) {
    next.scene = 'lost'; next.reason = 'hazard'; next.message = '进入风暴区。换条路线，再试一次。';
  } else if (next.energy <= 0) {
    next.scene = 'lost'; next.reason = 'energy'; next.message = '能量耗尽。缩短路线，再试一次。';
  } else if (same(target, CONFIG.goal) && next.collected.length === CONFIG.signals.length) {
    next.scene = 'won'; next.message = '信标已点亮，小船找到归途！';
  } else if (same(target, CONFIG.goal)) next.message = '灯塔还缺信号片，请回去收集。';
  return next;
}
