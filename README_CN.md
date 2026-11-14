# GAME DIRECTOR Skill（AI 游戏制作总监）

## 用途
把一个初步游戏创意，通过渐进式对话，变成可验证、可设计、可交付给 Codex / Claude Code 的完整游戏项目包。

## 目录
- `SKILL.md`：主工作流
- `references/interview-playbook.md`：访谈问题库
- `references/document-system.md`：Lite / Standard / Premium 文档体系
- `references/genre-modules.md`：游戏类型专项模块
- `references/asset-production-spec.md`：2D / 3D 美术与音频规范
- `references/codex-handoff.md`：编码 Agent 交接标准
- `templates/`：项目文档模板
- `agents/openai.yaml`：UI 元数据

## 安装到 Codex（个人级，推荐）
将整个 `game-director` 文件夹复制到：
- Windows：`%USERPROFILE%\\.agents\\skills\\game-director\\`
- macOS / Linux：`~/.agents/skills/game-director/`

最终确保存在 `.../game-director/SKILL.md`。Codex 会从用户级 `.agents/skills` 目录发现 Skill；若未出现，重启 Codex。

也可以放到某个项目的 `.agents/skills/game-director/`，只在该项目使用。

## Codex 中调用
- 显式调用：`$game-director`
- 查看 Skill：`/skills`
- 也可直接描述“我想做一款……”触发自动匹配。

## ChatGPT 中使用
支持 Skills 的 ChatGPT 桌面环境可以从 Skills 入口使用。当前对话也可以明确说“按 GAME DIRECTOR 工作流来”，并附上本 Skill。仅把文件复制到 Codex 本地目录，不会自动安装到所有 ChatGPT 网页会话。

## 推荐开场
`$game-director 我想做一款微信小游戏，类型是 Roguelite 射击。我只有一个大概想法，请像游戏制作人一样逐步问我问题。每次问最重要的一两个问题，不要一次发问卷。先确定产品方向和核心玩法，确认后再做完整开发包。`
