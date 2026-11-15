# GAME DIRECTOR — AI 游戏制作总监

版本 **1.4.1**。将游戏创意逐步转成可执行的策划、故事/世界观与角色剧情、UI/美术规格、技术方案和开发交接；已授权实施时，按里程碑推进真实游戏开发。含可选 Web 原型底座与运行验收工具，不自带原生引擎、模型/绑定工具或付费生成服务。

## 使用

显式调用：

```text
$game-director 我想做一款微信 Roguelite 小游戏，目前只有想法，先帮我确定核心体验。
$game-director 按已有需求创建 LITE 策划包，暂时不要开发。
$game-director 为解谜游戏写故事背景、角色动机、主支线、对白和结局，明确线索与玩家行动，先不开发。
$game-director 读取当前项目的文档和进度，继续已授权的里程碑，保留已有修改。
```

也可直接描述游戏立项、GDD 或制作需求，由 Codex 按描述匹配。新创意只补问最重要的缺失信息；已有方案和项目先恢复上下文，不重做访谈。局部修复/单资产编辑不强制完整流程。

LITE 可合并文档；STANDARD/PREMIUM 按实际规模拆分。先验证灰盒核心循环，再做代表性 UI/正式资源切片，最后批量扩展内容。没有开发授权时仅交付策划或设计，并明确原型未验证。

## 文件入口

- [SKILL.md](SKILL.md)：任务分流、规模判断和按需加载入口。
- [文档体系](references/document-system.md)：项目目录、21 个模板与裁剪方式。
- [类型索引](references/genre-modules.md)：16 类独立专项；混合游戏按需组合。
- [生产流程](references/production-workflow.md)：10 阶段交付物与退出条件。
- [续接协议](references/project-continuity.md)：状态、决策、假设和变更同步。
- [资产规范](references/asset-production-spec.md)：2D/3D/音频字段和独立审核/集成/验证状态。
- [行为场景](references/validation-scenarios.md)：真实对话评估的输入与观察标准。
- [项目文件验收](references/project-validation.md)：交付时核实清单、实际素材和证据文件；可直接运行。
- [故事与叙事](references/narrative-design.md)：背景、世界观、角色/势力、主支线/结局、任务与对白；包括时间线、知识/线索和存档检查。

全部参考文档和模板都能从 SKILL.md 沿相对链接到达，无需一次性读取全部文件。模板包含写作指导和显式示例，生成项目时要替换为真实内容；空模板不代表开发包完成。

- [原型与运行验收](references/prototyping.md)：可选 Web 底座、安全创建、规则测试、真实输入、截图/错误报告与自包含继续开发交接。

## 安装

从[GitHub 仓库](https://github.com/wangsalin/game-director)或[版本发布](https://github.com/wangsalin/game-director/releases)取得文件，完整命令见[安装说明](README.md#安装)。个人级目标：Windows 为 `%USERPROFILE%\.agents\skills\game-director`，macOS/Linux 为 `~/.agents/skills/game-director/`。项目级目标可用项目内 `.agents/skills/game-director/`。保留 `SKILL.md`、`agents/`、`references/`、`templates/`、`assets/`、`scripts/`、`VERSION`、README 与 `LICENSE`，忽略 `.git/`、node_modules、Python 缓存和本地临时文件。

同名 Skill 已存在时先检查差异并保留用户配置，不能直接覆盖。不要同时在多个发现目录安装重复副本。`allow_implicit_invocation` 保持 true；这表示允许匹配，不保证每次自然语言都会触发。安装后在新会话中用 `$game-director` 检查；未出现时重启客户端。不把本地 Codex 安装说成所有 ChatGPT 会话都已安装。

位置与发现机制参考 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills)。

## 维护与验证

在 Skill 根目录运行：

```powershell
python scripts/validate_skill.py
python -B -m unittest discover -s scripts -p "test_*.py" -v
```

Python 脚本需要 Python 3.10+，只依赖标准库。Skill 校验检查资源存在/可达、CSV 列数/ID/枚举/数值和关键状态约束；可以从任意工作目录调用，校验脚本也可传入另一个 Skill 副本路径。回归测试仅操作临时副本和生成的 PNG/WAV 文件。它们不验证完整 YAML，也不证明运行时对话效果。若环境提供 `skill-creator/scripts/quick_validate.py`，同时用它检查 frontmatter；`agents/openai.yaml` 另需核对 UI 元数据和 `$game-director` 默认提示。

验收带资产清单的游戏项目（将路径换成你的项目）：

```powershell
python -B scripts/validate_project.py "C:/Games/MyGame"
```

默认查找美术/音频清单，检查文档引用、真实文件、证据、PNG/WAV 规格。`--release` 加强资产完成状态与来源检查；通过不等于游戏或发布验收通过。参数、格式限制、自定义清单和退出码见[项目文件验收](references/project-validation.md)。

实际多轮访谈、自动匹配、原项目续接和工具行为按[场景](references/validation-scenarios.md)在独立上下文验证，记录真实结果，不能将静态通过当成行为通过。

1.4.1 修复静态服务对未压缩 WASM/游戏数据/Ogg 等资源的支持与响应类型，生成工程增加 `.gitignore`，补充真实浏览器 WASM 和 404 反例回归。原型资源、专用服务器与持续输入边界见[工具说明](scripts/web-check/README.md)。新增 Git 忽略行为回归在 Git 可用时执行，否则显示跳过；创建脚本本身不依赖 Git。

1.4.0 增加可选 Web 可玩底座、创建脚本、真实浏览器验收和继续开发交接；Node 20+ 用于规则/工具检查，Playwright 仅在自动浏览器验收时安装，游戏运行不需要第三方包。完整命令与限制见[原型说明](references/prototyping.md)。

1.3.0 增加独立叙事制作模块与五份模板，接通访谈、类型专项、GDD、数据/任务状态、续接与 QA。按仅背景/轻叙事/剧情驱动裁剪，不要求简单游戏编写长剧情。1.2.0 的真实项目文件验收继续保留；脚本不会审查剧情因果、分支条件或叙事质量，这些需做纸面/状态走查与实际试读/试玩。

本仓库采用 [MIT License](LICENSE)；第三方素材与工具按各自许可使用。
