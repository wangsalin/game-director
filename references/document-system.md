# 文档体系、目录与模板

模板是写作结构，复制后要填入项目内容、删除写作说明和不适用节，不保留示例资产。没有数据时明确待定与影响，不能把空表交付为完整方案。

## 目录与权威入口

新建中大型开发包可用以下相对路径。已有工程沿用原结构，README 记录实际路径；同一文件只保留一个权威版本。

| 推荐产物 | 模板 | 写到什么程度 |
|---|---|---|
| README.md | [项目索引](../templates/README_TEMPLATE.md) | 文件/章节路径、就绪级别、运行入口、缺失条件 |
| 00_Project_Overview/GAME_BRIEF.md | [Brief](../templates/GAME_BRIEF_TEMPLATE.md) | 体验、平台、受众、MVP、约束、假设 |
| 01_Game_Design/GDD.md | [GDD](../templates/GDD_TEMPLATE.md) | 可实现规则、核心循环、内容范围；嵌入命中类型的专项 |
| 01_Game_Design/SYSTEMS_AND_BALANCE.md | [系统与数值](../templates/SYSTEMS_AND_BALANCE_TEMPLATE.md) | 公式、初值、上下限、样例、调参目标 |
| 01_Game_Design/Narrative/STORY_BIBLE.md | [故事/世界设定](../templates/STORY_BIBLE_TEMPLATE.md) | 实际背景、世界规则/历史、真相与信息投放；按需 |
| 01_Game_Design/Narrative/CHARACTER_BIBLE.md | [角色与势力](../templates/CHARACTER_BIBLE_TEMPLATE.md) | 动机/行动、关系/弧线、知识边界、口吻与制作引用；按需 |
| 01_Game_Design/Narrative/STORY_OUTLINE.md | [主支线大纲](../templates/STORY_OUTLINE_TEMPLATE.md) | 可玩节拍、伏笔回收、选择/合流/结局、路线与预算；按需 |
| 01_Game_Design/Narrative/QUEST_DESIGN.md | [任务设计](../templates/QUEST_DESIGN_TEMPLATE.md) | 接取/目标/失败/提交、物品奖励、去重、读档与验收；按需 |
| 01_Game_Design/Narrative/DIALOGUE_SCRIPT.md | [对白与演出](../templates/DIALOGUE_SCRIPT_TEMPLATE.md) | 实际台词、节点/选项、条件/副作用、字幕/跳过与存档；按需 |
| 02_UI_UX/UI_SPEC.md | [UI](../templates/UI_SPEC_TEMPLATE.md) | 页面流、HUD、交互状态、布局/适配和原型路径 |
| 03_Art_Assets/ART_BIBLE.md | [美术规范](../templates/ART_BIBLE_TEMPLATE.md) | 风格、可读性、输出规格、资产审核标准 |
| 03_Art_Assets/ASSET_MANIFEST.csv | [美术清单](../templates/ASSET_MANIFEST_TEMPLATE.csv) | 每项资产规格、路径、来源、阶段/审核/集成状态 |
| 04_Audio/AUDIO_MANIFEST.csv | [音频清单](../templates/AUDIO_MANIFEST_TEMPLATE.csv) | 事件、循环/叠播/限频、文件规格、状态与来源 |
| 05_Technical/TDD.md | [技术设计](../templates/TDD_TEMPLATE.md) | 引擎理由、模块边界、关键风险、构建和性能预算 |
| 05_Technical/DATA_SCHEMA.md | [数据结构](../templates/DATA_SCHEMA_TEMPLATE.md) | 类型、约束、版本、存档恢复/迁移 |
| 06_Development/MILESTONES.md | [里程碑](../templates/MILESTONES_TEMPLATE.md) | 范围、依赖、任务、退出证据、风险 |
| 07_QA_Test/QA_TEST_PLAN.md | [QA 计划](../templates/QA_TEST_PLAN_TEMPLATE.md) | 规则到用例映射、设备范围和退出标准 |
| 07_QA_Test/TEST_REPORT.md | [测试报告](../templates/TEST_REPORT_TEMPLATE.md) | 命令/步骤、构建、实际结果、未执行项 |
| CODEX_START_HERE.md | [开发入口](../templates/CODEX_START_HERE_TEMPLATE.md) | 实际文档路径、授权阶段、运行命令和验收 |
| IMPLEMENTATION_STATUS.md | [进度](../templates/IMPLEMENTATION_STATUS_TEMPLATE.md) | 当前阶段、下一步、阻塞与验证证据 |
| DECISIONS.md | [决策](../templates/DECISIONS_TEMPLATE.md) | 决策/假设/未决问题和变更影响 |
| 08_Release/ | 按渠道编写 | 只有进入发布准备才创建有内容的清单与构建说明 |

## 按规模裁剪

**LITE**：可用一份 `README.md` 合并 Brief、精简 GDD、系统数值、UI/美术方向、技术/数据、QA、里程碑、进度和决策。另保留 `ASSET_MANIFEST.csv`；有音频时增加音频清单。交给独立编码 Agent 时增加自包含 `CODEX_START_HERE.md`，或明确 README 就是唯一入口。索引要指向真实章节；省文件不省核心规则和验收。

**STANDARD**：按上表拆分需要维护的内容；关卡计划、核心循环和动画规格可先放在 GDD/Art Bible 的独立节，足够复杂时再拆文件。若不需要音频，明确本版无音频，不生成空清单凑数。

**PREMIUM**：按实际系统增加世界观/叙事、任务/对话、3D 模型/骨骼管线、摄像机/物理、网络/服务器/反作弊、性能、本地化/无障碍、发布/运营专项。不因级别高就强行添加联网、剧情或商业化。

**叙事按内容需求裁剪，不由项目级别硬性决定。** 只要背景就交付实际背景文本与必要设定，不强制整包或五份叙事文件。轻叙事可在 GDD 中合并；剧情驱动按[叙事制作](narrative-design.md)拆分真正需要维护的世界、角色、大纲、任务、对白，并把实际路径加入 README/开发入口。长篇按已授权章节/试写范围标记完成度，提纲不能冒充全剧本。

## 内容闭环

用 `RULE-`、`SCREEN-`、`ASSET-`、`TC-` 等稳定 ID 关联规则、界面、资产与测试，不要求特定命名格式。每个关键需求有规则或设计、实现位置或计划、验收方式。读[类型索引](genre-modules.md)选专项，不能用空泛通用 GDD 替代。

文件与章节合并后，同步修改开发入口和续接路径。文档包完成不代表素材已生产或游戏已运行；按[阶段门](production-workflow.md)给出真实就绪结论。
