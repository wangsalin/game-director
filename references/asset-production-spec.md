# 美术与音频资产规范

## 通用资产字段
每项资产登记：Asset ID、名称、类别、用途、格式、尺寸/面数预算、透明背景、Pivot/Anchor/Scale、动画状态/帧率、源文件、导出文件、授权来源、状态和验收备注。
状态：planned / in_progress / review / approved / integrated / deprecated。

## 2D
- 角色：独立角色图；需要的 idle/move/attack/hit/death/interact 状态；统一比例、轮廓、材质。
- Sprite Sheet：标明帧尺寸、排列、帧率、循环方式和 pivot。
- 场景：背景、地面、前景、碰撞物、装饰分层；Tilemap 标明 tile 尺寸和碰撞层。
- UI：按钮 normal/pressed/disabled/selected/loading；面板切片规则；图标最小可读尺寸。
- VFX：触发条件、持续时间、混合模式、层级、屏幕震动和性能预算。

## 3D
概念图/三视图、源模型、格式、比例/坐标轴/pivot、面数预算、拓扑/UV、PBR 贴图、材质/shader、骨骼命名、动画 clip、Collider、LOD、场景模块、灯光、相机、VFX 和性能预算。

## 音频
清单字段：Audio ID、触发事件、文件名、BGM/SFX/Voice/Ambience、时长、循环方式、音量基准、优先级、是否允许叠播、限频规则、授权来源。

## 完成定义
- Concept：概念设计完成，不代表可导入。
- Production-ready：规格、源文件和导出文件齐全。
- Integrated：已进入工程并正确显示/播放。
- Approved：在目标设备通过质量验收。
不得把 Concept 标记为 Integrated 或 Approved。
