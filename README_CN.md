# GAME DIRECTOR — AI 游戏制作总监

版本 **1.1.0**。将游戏创意逐步转成可执行的策划、UI/美术规格、技术方案和开发交接；已授权实施时，按里程碑推进真实游戏开发。不是某个游戏工程，也不自带引擎、模型/绑定工具或付费生成服务。

## 使用

显式调用：

```text
$game-director 我想做一款微信 Roguelite 小游戏，目前只有想法，先帮我确定核心体验。
$game-director 按已有需求创建 LITE 策划包，暂时不要开发。
$game-director 读取当前项目的文档和进度，继续已授权的里程碑，保留已有修改。
```

也可直接描述游戏立项、GDD 或制作需求，由 Codex 按描述匹配。新创意只补问最重要的缺失信息；已有方案和项目先恢复上下文，不重做访谈。局部修复/单资产编辑不强制完整流程。

LITE 可合并文档；STANDARD/PREMIUM 按实际规模拆分。先验证灰盒核心循环，再做代表性 UI/正式资源切片，最后批量扩展内容。没有开发授权时仅交付策划或设计，并明确原型未验证。

## 文件入口

- [SKILL.md](SKILL.md)：任务分流、规模判断和按需加载入口。
- [文档体系](references/document-system.md)：项目目录、16 个模板与裁剪方式。
- [类型索引](references/genre-modules.md)：16 类独立专项；混合游戏按需组合。
- [生产流程](references/production-workflow.md)：10 阶段交付物与退出条件。
- [续接协议](references/project-continuity.md)：状态、决策、假设和变更同步。
- [资产规范](references/asset-production-spec.md)：2D/3D/音频字段和独立审核/集成/验证状态。
- [行为场景](references/validation-scenarios.md)：真实对话评估的输入与观察标准。

全部参考文档和模板都能从 SKILL.md 沿相对链接到达，无需一次性读取全部文件。模板包含写作指导和显式示例，生成项目时要替换为真实内容；空模板不代表开发包完成。

## 安装

个人级目标：Windows 为 `%USERPROFILE%\.agents\skills\game-director`，macOS/Linux 为 `~/.agents/skills/game-director/`。项目级目标可用项目内 `.agents/skills/game-director/`。保留 `SKILL.md`、`agents/`、`references/`、`templates/`、`scripts/`、`VERSION` 和本说明，忽略 `.git/`、Python 缓存和本地临时文件。

同名 Skill 已存在时先检查差异并保留用户配置，不能直接覆盖。不要同时在多个发现目录安装重复副本。`allow_implicit_invocation` 保持 true；这表示允许匹配，不保证每次自然语言都会触发。安装后在新会话中用 `$game-director` 检查；未出现时重启客户端。不把本地 Codex 安装说成所有 ChatGPT 会话都已安装。

位置与发现机制参考 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills)。

## 维护与验证

在 Skill 根目录运行：

```powershell
python scripts/validate_skill.py
python -B scripts/test_validate_skill.py
```

脚本只依赖 Python 标准库，检查资源存在/可达、CSV 列数/ID/枚举/数值和关键状态约束；可以从任意工作目录调用，校验脚本也可传入另一个 Skill 副本路径。回归测试覆盖 16 个有效/无效场景，仅操作临时副本。它们不验证完整 YAML，也不证明运行时对话效果。若环境提供 `skill-creator/scripts/quick_validate.py`，同时用它检查 frontmatter；`agents/openai.yaml` 另需核对 UI 元数据和 `$game-director` 默认提示。

实际多轮访谈、自动匹配、原项目续接和工具行为按[场景](references/validation-scenarios.md)在独立上下文验证，记录真实结果，不能将静态通过当成行为通过。

1.1.0 修复资产 CSV 列错位，补全专项/模板与主入口引用，前置玩法验证，并增加续接、阶段验收和资源校验。旧资产状态迁移规则见资产规范；不自动改写已有游戏项目的清单。
