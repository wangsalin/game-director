# Unreal Engine 专项

先读[共同流程](README.md)。从实际 `.uproject` 与匹配 Engine 出发，区分 Launcher/源码/自定义构建、Blueprint-only 与 C++ 项目；不为了统一示例重新生成用户工程。

## 版本和工具链

`.uproject` 的 `EngineAssociation` 可能是版本或自定义标识；结合项目文档、引擎安装/注册和 `Engine/Build/Build.version` 或编辑器 About 核实精确构建。不要将 `.uproject` 的 `FileVersion` 当 UE 版本。

检查插件及其目标平台支持、`.uproject` 中 Modules/Plugins、`Source/`、`.Build.cs/.Target.cs`、配置和目标 SDK。C++ 构建需要对应版本支持的编译器/Windows SDK 等；源码 Engine 还需其构建前置条件，不能用系统有 Visual Studio 就声称工具链匹配。Blueprint-only 在某些插件或平台下仍可能需要编译工具链。

新项目通过实际版本模板/编辑器创建；已有项目保持 `.uproject`、`Config/`、`Content/`、`Source/` 和项目插件源文件。`.uasset/.umap` 是真实二进制资产，不能用同名文本、图片或伪 JSON 代替；已确认的 Git LFS/大文件策略继续沿用。按项目约定忽略 `Intermediate/`、`Saved/`、派生缓存与生成工程文件，不能误忽略插件所必需的二进制或正式交付产物。

打开前保留差异和恢复点；引擎转换、重新保存资产、升级插件可能不可逆影响旧版本，迁移需要独立范围和备份。导入后检查日志、插件加载、C++ 编译或 Blueprint 编译结果，不仅看编辑器窗口出现。

## 可玩地图、逻辑与代表性资产

1. 明确默认 Game Map/Editor Map、GameMode、Pawn/Character、PlayerController、输入和生成点。验证玩家实际被控制、相机正确、UI 可见；只放一个 Actor 不算可玩场景。
2. Blueprint / C++ 沿用已有分工；蓝图用原生编辑器或项目已有已验证工具建立，不能仅口述节点图就称已实现。C++ 逻辑注意 UCLASS/UPROPERTY/UFUNCTION、模块依赖和 UObject 生命周期；没有编译就标实现待验证。
3. 真实输入→规则→反馈，补目标/结束或持续进度、重开与适用保存。核对碰撞预设、通道/Trace、物理、坐标/单位、Tick/定时器、场景重载与委托注销；使用项目现有 Enhanced Input 或旧输入，不混设无效映射。
4. 导入一组真实模型/材质/贴图、骨骼/动画、音频和字体；检查缩放、轴向、LOD、碰撞、材质/渲染特性与目标硬件。资产移动优先在 Content Browser 中处理并审查 Redirector，不能在资源管理器搬二进制后直接认定引用完整。
5. 先 PIE 验证核心流程，再 Standalone/打包产物验证；PIE、多客户端模拟和真实联网/设备不是同一证据。自动测试使用项目现有 Automation/Functional Tests 等机制，核对实际发现与运行的测试数量和失败日志。

## 编译、Cook 和打包

先用编辑器 Platforms / Project Launcher 配置本项目目标、配置、地图、Cook/Stage/Package 和输出；有已有脚本或构建 Profile 时复用。UnrealBuildTool 负责目标编译，UAT 的 `BuildCookRun` 可组织编译、资源 Cook、暂存、打包等阶段；C++ 编译通过不代表 Cook、打包和运行通过。

Windows 的 UAT 通常为实际 Engine 内的 `Engine/Build/BatchFiles/RunUAT.bat`；其他宿主用其对应脚本。推荐由 Project Launcher 生成/核对当前版本命令，避免手写一大串不匹配参数。下面只是 **Windows / Win64 / Development** 调用形状，须先替换变量、核实当前版本帮助及项目配置：

```powershell
& $RunUAT BuildCookRun "-project=$ProjectFile" -noP4 -platform=Win64 `
  -clientconfig=Development -build -cook -stage -pak -archive `
  "-archivedirectory=$OutputDirectory"
if ($LASTEXITCODE -ne 0) { throw 'Unreal BuildCookRun failed' }
```

输出使用本次独立目录，不覆盖源码或旧证据；游戏默认地图、需打包的地图/动态资源、插件和配置必须真实设置。不要在缺 SDK 时随意省掉编译/Cook 阶段或开启“跳过”来伪装成功。Packaging 日志失败时保存 UAT/Editor 日志和首个根因，区分 C++ 编译、资源引用、Cook、平台工具和签名。

打包完成后核实本次产物，再从归档目录独立启动；不能直接运行编辑器替代游戏。Development 和 Shipping 的控制台/配置/调试差异按实际验证，不假定开发包结果覆盖发行包。移动/主机/商店目标需相应 SDK、平台资格、签名和设备；没有权限/工具保持 `not_run`。

## 调试、性能和交接

黑屏/不能移动先查默认地图、GameMode/Pawn、输入焦点/映射、相机和玩家出生；碰撞不对查通道/组件/模拟开关；Cook 丢资源查软引用、地图/目录打包规则、大小写和插件内容。不要通过禁用碰撞、吞日志或移除问题资产降低目标来“通过”。

性能预算绑定真实目标硬件；按需用 Unreal Insights、统计/Profiler 等实际记录帧时间、内存、加载与渲染/物理成本，不能仅凭编辑器 FPS 推断设备性能。缺 GPU/设备时将渲染/性能测试列未运行。

交接精确 Engine/插件/编译器、默认地图与输入、蓝图/C++ 资产路径、构建 Profile/命令、日志/产物及独立启动证据。编译、Blueprint 检查、PIE、Cook/Package、独立运行和设备分阶段报告；不能以文本描述蓝图、代码静态检查或打包目录存在替代。

## 官方核对入口

2026-11-15 核对；页面需选择本项目实际 UE 版本：

- [Build / Cook / Stage / Package / Deploy / Run 与命令生成](https://dev.epicgames.com/documentation/en-us/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine)。
- 实际 Engine 的 `Engine/Build/Build.version`、`RunUAT.bat -List` 及所选命令的帮助，是本机版本/可用命令的补充证据；不要把未执行的帮助命令记作通过。
