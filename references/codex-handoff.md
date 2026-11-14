# Codex / Claude Code 开发交接规范

## 开发前
1. 审计工作区，不覆盖现有工程。
2. 阅读完整项目规格和决策记录。
3. 检查引擎、版本、依赖和构建工具。
4. 列出缺失素材、App ID、广告位 ID 等外部条件。
5. 非阻断信息用可替换占位方案并记录；阻断信息才询问用户。

## 开发顺序
工程审计 → 核心规则模块及测试 → 可玩 Vertical Slice → 核心 UI/反馈 → 内容扩展 → 存档/平台 API/广告 → 性能/兼容/发布。

## 禁止
- 静态页面冒充游戏；
- 随机数或假动画冒充核心玩法；
- 擅自改变已确认规则或删需求；
- 占位图冒充正式资产；
- 核心逻辑直接调用平台 API；
- 未运行测试就声称完成；
- 未确认就覆盖/删除用户已有文件。

## 每个里程碑
更新 IMPLEMENTATION_STATUS、TEST_REPORT；有新决策时更新 DECISIONS；有资产变化时更新 ASSET_MANIFEST。

## 状态必须区分
implemented、compiled、editor-tested、simulator-tested、device-tested、released。不得混为一谈。

## 最终汇报
工程位置、引擎版本、运行平台、已完成/未完成模块、编译测试结果、真机验证、性能表现、已知问题、下一步。
