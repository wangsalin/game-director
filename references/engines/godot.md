# Godot 专项

先读[共同流程](README.md)。以下命令以 Godot 4 标准版为形状示例，执行前用目标二进制的 `--version` / `--help` 和对应版本官方文档核实；不自动将 Godot 3 或 .NET 工程转换为此路径。

## 工程与环境

- 入口是 `project.godot`；记录实际补丁版本、标准/.NET、渲染器和目标平台。`config/features` 提供兼容性线索，`config_version` 是配置格式号，都不能独立证明精确编辑器版本。C# 工程还需匹配 .NET SDK、解决方案/工程和目标平台支持。
- 核实实际引擎可执行文件、插件、导出模板及目标 SDK。Windows 优先使用 console 版本采集 CLI 输出；无显示环境可用 `--headless` 做导入/规则检查，但不证明图形、音频或硬件输入正确。
- 新工程用匹配版本项目管理器/原生场景创建；已有工程先保留差异，从原目录导入。保留源码、`project.godot`、场景/资源、适用的 `.uid`/导入设置和 `export_presets.cfg`；`.godot/` 是生成数据，不提交导出凭证。按实际版本判断需要跟踪的元数据，不全局删除 UID 或改写引用。

## 实现最小切片

设置真实主场景和输入映射；按需求选择 Node2D/Control/Node3D 等结构，检查相机、UI 锚点/容器、坐标空间、碰撞层/掩码。输入→规则→状态反馈形成闭环，再补目标/结算、重开、暂停和适用存档。

在匹配版本编写脚本并连接信号；Godot 3/4 的节点名、信号、物理移动等 API 有差异，不用字符串替换迁移整工程。场景切换/重开时检查计时器、信号重复、释放节点后引用、全局状态是否复位；物理更新与 UI/渲染更新按实际需要分开。

导入一组真实图片/音频/模型：检查纹理过滤、图集/动画、像素或世界单位、骨骼/材质、碰撞与音频总线。移动/重命名优先用 FileSystem 面板并复核依赖；存在文件不等于成功导入。缺字体时实际检查中文显示，不能只看英文标签。

## 命令行和测试

变量须先设为实际绝对路径，以下都是待执行形状：

```powershell
& $Godot --version
& $Godot --headless --path $Project --import
if ($LASTEXITCODE -ne 0) { throw 'Godot import failed' }
& $Godot --path $Project
```

`--import` 等导入完成后退出；检查退出码和日志里的脚本/资源错误，不能用固定睡眠后杀进程冒充导入完成。已有自动测试使用项目选定的工具；简单规则可用 `SceneTree` 测试脚本，从真实规则模块执行断言，失败显式 `quit(1)`、成功 `quit(0)`：

```powershell
& $Godot --headless --path $Project --script res://tests/rules_test.gd
```

上面的脚本必须实际存在；示例命令不自带测试。测试可观察游戏状态，不通过直接写最终状态或强制胜利来伪造输入成功。实际运行主场景检查输入、相机/HUD、核心循环、重开、暂停、保存、控制台；无头输入模拟与图形真实操作分别报告。

## 导出和启动产物

在编辑器 Export 面板设置目标、包含资源、主场景与预设，安装**匹配精确版本/平台**的导出模板，核对 SDK/签名。`export_presets.cfg` 可按项目管理；`.godot/export_credentials.cfg` 等凭证不得提交。输出父目录先创建，预设名须与项目一致：

```powershell
# 示例目标为 Windows Desktop；其他平台用本项目实际预设和扩展名
& $Godot --headless --path $Project --export-debug 'Windows Desktop' $OutputExe
if ($LASTEXITCODE -ne 0) { throw 'Godot export failed' }
```

开发调试/正式发行分别使用对应导出选项，不把 debug 包称为正式包。检查日志、二进制和附属数据，再从实际导出目录启动。单独 `--export-pack` 只导出 PCK/ZIP 资源包；用引擎 `--main-pack` 运行可验证资源包加载，**不等于独立原生可执行文件已导出**。不要把编辑器二进制冒充正式导出模板。

Web 导出单独检查目标版本的渲染/语言/线程条件、HTTP/MIME、压缩与所需跨源隔离；移动目标核对 SDK/权限/签名并安装到设备。浏览器预览、原生构建和设备测试分别记录，不以桌面无头通过推断 Web/手机通过。

## 排错和交接

- 首次导入失败先查首个脚本解析/插件/资源错误与版本匹配，不先删缓存或升级工程。
- 角色不动先查输入动作名、焦点、暂停/处理模式、碰撞与物理调用；黑屏先查主场景、相机/可见性、资源和渲染器。
- 打包后丢资源核对大小写、显式/动态加载、导出过滤及依赖；导出失败区分模板缺失、预设错误、SDK和签名。
- 交接写精确二进制版本、主场景、输入映射、依赖/插件、测试与预设/构建命令、源码/产物证据和平台未运行项；将操作留在本项目，不仅引用本 Skill。

## 官方核对入口

2026-11-15 核对；`stable` 内容会随版本变化，执行时选择本项目版本：

- [命令行、导入、脚本与导出](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)。
- [导出预设、模板和凭证](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html)。
- [版本控制与生成文件](https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html)。
