# Web 浏览器检查工具

[check.mjs](check.mjs) 用 Playwright 驱动真实浏览器输入；项目自行提供场景计划。它启动仅绑定 `127.0.0.1` 的临时静态服务器，检查后关闭，不执行项目后端、不发布游戏。适用于受支持资源组成的静态 Web 项目；已有 Vite 或引擎 Web 导出先按项目方式构建到独立静态目录，再核对下方资源与服务器条件，不能将源目录或原生工程当成可运行产物。

## 环境与调用

Node 20+。在本工具目录执行 `npm ci`，按[锁文件](package-lock.json)安装唯一直接依赖 Playwright；它只用于开发验收，不是游戏运行依赖。需要可用浏览器：可选择已安装 Chrome/Edge，或在授权范围内执行 `npx playwright install chromium` 下载专用浏览器。没有浏览器就报告 not_run，不自动安装全局工具。

在游戏项目根目录（工具随创建脚本复制到 `tools/web-check/` 后）：

```text
npm --prefix tools/web-check ci
node tools/web-check/check.mjs --project . --plan browser-plan.json --out evidence-run-01
```

使用系统 Chrome 可加 `--channel chrome`，Edge 为 `--channel msedge`；或用 `--executable` 指定实际浏览器文件，不能与 channel 同用。默认使用 Playwright 的 Chromium。`--out` 必须是不存在的新目录，其父目录已存在；不覆盖上次证据。路径相对执行时工作目录，支持空格与中文。

## 静态资源与导出边界

服务白名单包括 HTML/CSS/JS/MJS/JSON、PNG/JPG/JPEG/SVG/WebP、WAV/MP3/Ogg、WOFF2/ICO，以及未压缩 `.wasm`、`.pck`、`.data`、`.bin`。WASM 使用精确的 `application/wasm`；游戏数据按二进制传输，二进制响应不添加文本字符集。隐藏文件、越界路径和白名单外类型仍拒绝提供。

这只说明对应文件可被服务，不保证某个引擎完整导出包可运行。当前不处理预压缩 `.gz/.br/.unityweb`、自定义响应头、跨源隔离/多线程、后端或专用加载器要求。导出依赖这些条件或其他资源格式时，使用项目实际服务器与自身浏览器测试，并记录环境与结果；不能把换成普通网页解释为原引擎通过。

## 计划

计划是 JSON：`schema: 1`、可选 `viewport: {width,height}`、`touch: true`、`scenarios` 数组。每个场景有唯一 ASCII `id` 和 `steps`，新建隔离浏览器上下文并从首页开始，同一场景内 reload 保留本地存储。不会在不同场景共享存档。生成的底座在项目根目录提供 browser-plan.json；其他游戏按实际规则编写。

支持的 action：

| action | 字段 | 行为 |
|---|---|---|
| click | selector | 点击唯一可操作元素 |
| tap | selector | 触摸点击，需要计划设置 touch: true；这是浏览器模拟，不是实体手机实测 |
| press | key | Playwright 键名，例如 ArrowRight、Escape、r；一次按下并松开 |
| wait | ms | 等待 0–5000ms，用于有实际时间需求的机制 |
| reload | 无 | 刷新同一页面，不清空当前场景存储 |
| expectText | selector、equals | 检查可见元素文本（去首尾空白），精确相等 |
| expectState | path、equals | 通过只读 `window.game.getState()` 获取快照，按点分路径深比较，最多等待 3 秒 |
| screenshot | name | ASCII 名称，保存当前整页截图 |

输入范围是单次 `press`、元素 `click/tap`；当前没有持续按住/松开、组合键持续状态、鼠标移动/拖拽、指针锁定或手柄动作。动作/射击/平台跳跃等项目需要这些输入时，沿用项目自身测试工具或先实现并验证相应驱动，不能用单次按键覆盖结果推断持续操作已通过。

`expectState` 的观测口只同步返回当前真实状态的拷贝，不返回 Promise；观测读取另有 3 秒超时保护，避免异常观测口挂起验收。不能用强制通关、修改坐标或设置奖励来替代输入。没有观测口的既有游戏可仅使用 DOM 断言和截图；不为测试重写整个游戏。没有断言的场景、空计划和非法步骤拒绝通过。计划按需求写，不能把底座的通关路线直接套到其他玩法。

## 结果与边界

新目录写入 `report.json` 与每个场景的截图：逐步状态、预期/实际、浏览器版本/视口、计划及已服务文件的 SHA-256、JS/控制台/请求错误、截图哈希。失败保留证据，修复后用新目录复测。每个动作通常最多等 3 秒，页面导航 15 秒；动作阶段预算 120 秒，计划明确等待总和不超过 60 秒。

- 退出 0 / passed：本计划中的断言完成且未记录浏览器错误。
- 退出 1 / failed：输入计划、项目或实际场景失败；输出目录非法时命令直接报错。
- 退出 2 / not_run：缺 Playwright 或可启动浏览器，未执行场景。

无效计划仍是失败，不会因截图成功变成通过。错误运行不能覆盖旧证据。截图需要人工检查布局、中文、反馈与可读性。这里只覆盖指定计划/视口，未测玩法、兼容性、帧率、触控设备、平衡、趣味、素材质量、原生引擎或发布条件不能标为通过。

维护工具运行 `node --test scripts/web-check/check.test.mjs`（仓库根目录）；无需安装 Playwright 即可检查计划与静态服务逻辑。实际浏览器检查另行运行。

安装依赖及浏览器后，在工具目录运行 `npm run test:browser`。随附 [browser.test.mjs](browser.test.mjs) 实际验证浏览器 WASM 流式实例化/游戏数据字节，以及 DOM 断言成功仍因资源 404 判失败。默认在系统临时目录保留项目、计划、报告和截图；可用 `WEB_CHECK_TEST_ROOT` 指定不存在的新目录，`WEB_CHECK_EXECUTABLE` 指定已安装 Chromium 文件。缺浏览器时不会把这两项测试标为通过。此测试不代表完整引擎导出或 Ogg 播放验收。
