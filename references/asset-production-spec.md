# 美术与音频生产规范

## 生产策略与工具

每个项目登记资产；内容仅是默认需求范围，不要求每款游戏都出现 Boss、骨骼或音效。先盘点已有素材、许可和可用制作工具，按实际目标生成或制作。未接通工具时记录制作规格、负责人和待制作状态，不能把制作清单说成已交付素材。

灰盒仅用明确标记的临时素材；核心循环验证后，先制作一组代表性正式资产并实际导入，再扩展批量内容。保留源文件、导出文件和版本关联；有生成工具时记录模型/工具、提示词或任务记录路径，避免重复付费请求。对外采购/付费批量生成按用户授权执行。

## 清单字段

[美术模板](../templates/ASSET_MANIFEST_TEMPLATE.csv)每行一个唯一资产/变体；动画状态可用单独 ID 或明确的 clip 清单。模板的 `EXAMPLE-` 行是格式示意，生成项目时替换，不把示例当作待制作需求。

必填标识：`asset_id,name,category,usage,format`。规格包括 `width,height,transparent,pivot,animation,fps`；3D 用 `poly_budget,texture_spec,rig_spec,scale_units,collider_spec,lod_spec`，不适用项留空并在 notes 解释必要例外。`source_path,export_path,license,provenance` 记录源/导出相对项目路径和可追溯许可/来源；planned 可暂缺文件路径，但不是生产完成。

尺寸、面数、帧率与贴图规格需在生产前确定；初期未知标注待定原因和影响，不伪造规格。license 为 `unknown` 时不得宣称可商业发布。CSV 使用 UTF-8、标准逗号分隔，含逗号的字段必须正确引用，所有行列数一致。

## 状态是独立维度

| 字段 | 允许值 | 含义 |
|---|---|---|
| production_stage | concept / production | 概念探索或可导入生产素材；用不同 ID/来源关系连接，不靠改标签把概念图变模型 |
| status | planned / in_progress / ready / deprecated | 制作进度；ready 表示规格及所需源/导出文件齐全 |
| review_status | not_reviewed / changes_requested / approved | 美术/内容审核；概念也能审核通过 |
| integration_status | not_integrated / integrated | 是否已进入实际工程并正确显示/播放 |
| verification_status | not_run / passed / failed | 是否按目标平台/设备验证；证据在 evidence_path |

`ready` 不自动意味着 reviewed、integrated 或 device-tested。`integrated` 要求生产素材及导入证据；设备验证通过要求已集成并有构建/设备/观察记录。概念图可以 approved，但不能标为生产集成或设备通过。

旧清单若出现 `review/approved/integrated` 单字段状态，核对旧证据后分拆；未知的审核、集成或设备结果保持未验证，不能从旧标签自动推断。保留旧清单备份和迁移说明，不直接覆盖用户记录。

## 2D 生产规范

- 角色/敌人/道具：统一比例、轮廓、配色和锚点；列实际需要的 idle/move/attack/hit/death 等状态，逐项验收。
- 序列帧/图集：帧尺寸、排列/命名、帧率、循环、透明边缘、pivot、切图/压缩参数；检查边缘和帧间跳动。
- 场景：背景/地面/前景/碰撞物分层；Tilemap 说明 tile 尺寸、可拼接边缘和碰撞层。
- UI：normal/pressed/disabled/selected 等实际状态、九宫格/切片规则、图标最小可读尺寸、中文字体来源。
- 特效：触发、时长、层级、混合、打断、震屏及性能预算；不得用命中特效代替伤害判定。

## 3D 生产规范

概念/三视图只作建模参考。生产资产指定源格式/引擎导出、坐标轴/单位/比例/pivot、面数/拓扑/UV、PBR 贴图通道/色彩空间/分辨率、材质、骨骼命名/层级、蒙皮、动画 clip/FPS/根运动、Collider 和 LOD。把规格写到资产类型上，不要求静态石块有骨骼。

实际导入检查比例、朝向、材质、骨骼/动作切换、穿插/碰撞、资源引用和目标设备预算；没有引擎或模型工具时停在规格/概念层，不生成假 `.fbx` 或声称已绑定骨骼。

## 音频

[音频模板](../templates/AUDIO_MANIFEST_TEMPLATE.csv)按事件登记 ID、文件名/路径、类别、时长、格式/采样率/声道、循环点、音量、优先级、叠播、并发/限频、来源和独立状态。BGM 检查循环接缝，SFX 检查多事件叠加，语音检查字幕/语言对应。没有音频需求时明确本版无音频，不生成空清单冒充完成。
