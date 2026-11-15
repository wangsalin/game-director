# GAME DIRECTOR — AI 游戏制作总监

[![Validate](https://github.com/wangsalin/game-director/actions/workflows/validate.yml/badge.svg)](https://github.com/wangsalin/game-director/actions/workflows/validate.yml)
[![Version](https://img.shields.io/github/v/release/wangsalin/game-director)](https://github.com/wangsalin/game-director/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

面向 Codex 的游戏策划与制作总监 Skill。从创意访谈、游戏策划、规则数值、关卡和 UI/美术规格，到技术方案、开发交接、进度续接与验收，按项目阶段推进。

**当前版本：1.4.1。** 默认简体中文，支持 2D/3D、16 类游戏专项、独立叙事模块、可选 Web 原型工具和 LITE / STANDARD / PREMIUM 三种规模。仅要求策划时交付策划包；明确授权开发后才进入实现。

## 能做什么

- **游戏策划**：逐步澄清核心体验，编写 GDD、玩法循环、状态机、系统数值、成长、关卡与内容范围；复算重要汇总与公式样例。
- **故事与叙事**：编写故事背景、世界规则/历史、角色与势力、主支线、伏笔与结局、实际对白及任务状态；审查角色知识、分支条件和存档衔接。只需背景时不强制整套长剧情。
- **UI 与资产规划**：定义页面流程、HUD、输入反馈、适配、美术方向、2D/3D/音频规格及资产清单。
- **技术与开发交接**：沿用已确认引擎与工程，设计模块、数据、存档、平台接入、里程碑、QA 和自包含开发入口。
- **持续制作与验收**：恢复已有项目状态，区分概念、正式素材、集成和设备验证；附带真实文件、清单及 PNG/WAV 规格检查工具。
- **可玩原型与运行验收**：可选无第三方运行依赖的 Web 游戏底座，提供安全创建、独立规则测试、真实浏览器输入计划、截图/错误报告及自包含继续开发入口。已有引擎项目沿用原工程。

它不自带游戏引擎、模型/骨骼制作工具或付费生成服务。高保真原型、素材制作、构建与真机测试依赖当前环境实际可用的工具；未完成和未验证项会明确记录。

## 安装

下载 [v1.4.1 安装包](https://github.com/wangsalin/game-director/releases/tag/v1.4.1)，将其中的 **game-director 文件夹**放到以下任一位置，确保 `SKILL.md` 直接位于该文件夹下：

| 范围 | 路径 |
|---|---|
| Windows 个人级 | `%USERPROFILE%\.agents\skills\game-director\` |
| macOS / Linux 个人级 | `~/.agents/skills/game-director/` |
| 当前项目 | `<project>/.agents/skills/game-director/` |

已存在同名 Skill 时先备份和比较差异；避免在多个发现目录安装重复副本。安装后开启新会话，用 `$game-director` 调用；若未发现，重启客户端后检查路径。

也可用 Git 安装固定版本。以下命令要求 Git 可用且目标目录尚不存在：

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE/.agents/skills" | Out-Null
git clone --branch v1.4.1 --depth 1 https://github.com/wangsalin/game-director.git "$env:USERPROFILE/.agents/skills/game-director"
```

macOS / Linux：

```bash
mkdir -p ~/.agents/skills
git clone --branch v1.4.1 --depth 1 https://github.com/wangsalin/game-director.git ~/.agents/skills/game-director
```

使用 Skill 的指令与模板不要求 Python；随附 Python 创建/校验脚本需要 **Python 3.10+**，仅使用标准库。可选原型规则测试需要 **Node 20+**；自动浏览器检查另需工具锁定的 Playwright 和可启动浏览器。它们不是游戏运行依赖。

## 调用示例

从想法开始：

```text
$game-director 我想做一款单机 Roguelite，先帮我确定核心玩法，逐步讨论，暂时不要开发。
```

生成策划包：

```text
$game-director 为 PC 键鼠 2D 解谜游戏创建 LITE 策划包，包含具体规则、UI、资产清单、技术方案与验收标准，不开发。
```

继续已有项目：

```text
$game-director 读取当前工程、文档和真实进度，保留已有修改，完成当前已授权的开发里程碑并验收。
```

故事背景与剧情：

```text
$game-director 为一款海岛解谜游戏写故事背景、主角与关键NPC、主线和两个结局，说明线索如何通过玩法获得。先做叙事策划，不开发。
```

游戏立项、GDD、游戏制作等自然语言请求也允许自动匹配；实际触发由客户端决定，不保证每次都会命中。显式调用适合需要确定使用此 Skill 的场景。

制作可玩原型：

```text
$game-director 做一个可玩的轻量浏览器推箱子原型，包含键盘与屏幕按钮、胜利和重置。其他可逆细节你决定；实际运行并报告测试与未验证范围，保留继续开发入口，不发布。
```

## 可选 Web 原型工具

在目标父目录已存在、目标目录尚不存在时创建底座：

```text
python -B scripts/create_web_prototype.py /path/to/new-game --title "原型名称"
```

底座本身是可玩的回合制收集游戏；其他玩法需实际改写规则、输入/表现与用例，不能只改名。它带模块化源码、配置、规则测试和自包含 `tools/web-check/`，创建时不安装工具、不预填通过。运行方法、依赖、计划格式、失败/缺工具结果与继续开发见[原型执行说明](references/prototyping.md)。只支持静态 Web 的随附浏览器工具不能代替 Unity/Godot/Unreal 或实体设备验证。

1.4.1 补齐未压缩 WASM、部分游戏二进制/Ogg 资源与正确响应类型，生成工程附带 `.gitignore`，另加入实际浏览器 WASM/404 回归。资源可服务不等于完整引擎导出可运行；压缩、多线程、专用服务器和持续输入的限制见[工具说明](scripts/web-check/README.md)。

## 验证

在仓库根目录运行：

```bash
python -B scripts/validate_skill.py
python -B -m unittest discover -s scripts -p "test_*.py" -v
node --test assets/web-prototype/tests/rules.test.js
node --test scripts/web-check/check.test.mjs
```

Git 忽略行为回归在 Git 可用时实际运行，缺少 Git 时显示跳过；创建脚本本身不依赖 Git。安装工具依赖及浏览器后，可在 `scripts/web-check/` 运行 `npm run test:browser`，测试和失败证据保留方式见工具说明。

带资产清单的项目文件验收（替换为实际游戏项目根目录）：

```bash
python -B scripts/validate_project.py /path/to/GAME_PROJECT
```

文件检查通过只说明已检查的结构、清单、文件与规格符合约束，不代表玩法平衡、素材质量、引擎/真机或发布验收通过。测试范围和实际行为试用记录见[验收记录](references/validation-scenarios.md)；自定义清单、`--release` 资产检查与限制见[项目验收说明](references/project-validation.md)。

## 资料入口

- [原型、运行验收与继续开发](references/prototyping.md)：可玩底座、真实输入、规则测试、截图/日志与交接。
- [Skill 主入口](SKILL.md)与[完整中文说明](README_CN.md)。
- [16 类游戏专项](references/genre-modules.md)、[生产流程](references/production-workflow.md)与[文档/模板索引](references/document-system.md)。
- [故事与叙事模块](references/narrative-design.md)：背景/世界、角色/势力、大纲、任务、对白五份可裁剪模板，以及内容和状态验收要求。
- [资产生产规范](references/asset-production-spec.md)、[开发交接](references/codex-handoff.md)与[项目续接](references/project-continuity.md)。

## 许可

[MIT License](LICENSE) · Copyright (c) 2026 wangsalin。

本仓库的许可覆盖仓库中的指令、模板与代码；使用时引入的字体、图片、音频、模型或第三方工具仍需分别核对其许可。

本版原型工作流参考 [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) 的可玩反馈和运行证据思路；底座与工具为本仓库独立实现，没有移植其 Agent/钩子体系。
