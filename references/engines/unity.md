# Unity 专项

先读[共同流程](README.md)。沿用工程精确 Editor 版本；下面参考 Unity 6 / `6000.0` 官方文档，旧 2022/2023 等工程查对应版本，不为了使用示例升级。

## 版本、依赖与导入

从 `ProjectSettings/ProjectVersion.txt` 读 `m_EditorVersion`，再与实际 Editor 核实；Hub 版本不是 Editor 版本。检查 `Packages/manifest.json`、包锁文件、渲染管线、输入系统、自定义包/插件、目标模块和平台 SDK。Editor 许可/授权必须有效，不能将账户登录信息或许可证密钥写进命令示例、日志或仓库。

新工程用匹配版本/渲染管线模板；已有工程保持 `Assets/`、`Packages/`、`ProjectSettings/` 和现有组织方式。资源及其 `.meta` 成对保留，GUID 决定引用；优先在 Project 窗口移动，不重新生成 `.meta` 解决丢引用。不要覆盖现有 `.gitignore`，通常忽略 `Library/`、`Temp/` 等生成数据，不能忽略源码包锁或正式工程设置。

首次打开等待包解析、资源导入、脚本编译完成，再核对 Console、Editor 日志与 Git 差异；没有目标 Build Support 模块或许可时明确阻塞。项目已由一个 Editor 打开时不启动另一个进程写同工程；CI 使用独立副本/工作目录。

## 场景、脚本与资产

1. 明确启动 Scene、场景切换与构建包含列表；Unity 6 的 Build Profiles 与旧版 Build Settings 按实际项目使用，不能只配置当前编辑器打开的 Scene。
2. 创建/复用 GameObject、MonoBehaviour、Prefab 与序列化引用；场景中实际挂载脚本，Inspector 绑定。不要将纯 C# 编译成功等同于 Unity 生命周期、组件、序列化或渲染通过；不能手写未经验证的场景 YAML/GUID 冒充编辑器产物。
3. 沿用已有 Input System 或旧输入设置，检查项目实际启用模式。真实操作改变规则并反馈，补目标/结算、重开和适用暂停/存档；检查 `OnEnable/OnDisable` 事件配对、`Time.timeScale` 恢复、场景重进和跨场景对象。
4. 代表性资源核对 Sprite 的 PPU/过滤/锚点/图集，3D 单位/材质/骨骼/动画/碰撞，以及音频与字体；确认 Built-in/URP/HDRP 兼容，不能将粉色材质简单解释为美术问题。
5. 核心规则尽量可独立测试；已有 Test Framework 时使用项目测试程序集和 EditMode/PlayMode 测试。测试发现为零不能报告全部通过，测试运行参数按已安装包版本核对。

## 命令行构建

使用项目已有构建脚本优先。批处理入口需为 Editor 程序集中的静态方法；`-executeMethod` 不会凭空创建方法。Windows PowerShell 调用形状如下，变量/方法名必须是本项目真实值：

```powershell
$unityArgs = @('-batchmode', '-quit', '-projectPath', ('"' + $Project + '"'),
  '-buildTarget', 'Win64', '-executeMethod', 'BuildEntry.BuildWindows',
  '-logFile', ('"' + $Log + '"'))
$process = Start-Process -FilePath $Unity -ArgumentList $unityArgs -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw 'Unity build failed' }
```

`-buildTarget`、Build Profile、构建脚本目标保持一致；参数不能替代已安装平台模块。`-nographics` 仅在确认该流程不依赖图形时使用，不能用它验证渲染或所有烘焙流程；禁止用忽略编译错误的参数掩盖失败。

如确实需要新增最小 Windows 构建入口，可在 **`Assets/Editor/BuildEntry.cs`** 采用下面模式，先对照项目版本和已有构建约定调整；它不是已验证的通用构建器，也不会自动创建游戏或场景：

```csharp
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;

public static class BuildEntry {
    public static void BuildWindows() {
        var scenes = EditorBuildSettings.scenes
            .Where(s => s.enabled).Select(s => s.path).ToArray();
        if (scenes.Length == 0)
            throw new BuildFailedException("No enabled scenes configured.");
        Directory.CreateDirectory("Builds/Windows");
        var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
            scenes = scenes,
            locationPathName = "Builds/Windows/Game.exe",
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.Development
        });
        if (report.summary.result != BuildResult.Succeeded)
            throw new BuildFailedException(report.summary.result.ToString());
    }
}
```

实际执行前保证输出属于本次构建、不覆盖需保留的文件；正式构建要核实发布配置。检查 Editor 返回状态、日志、`BuildReport` 和本次产物，不能只凭 `Game.exe` 已存在或方法未抛异常判断。Build Profiles 项目复用其真实配置和官方对应 API，不强行改回上述传统场景列表。

## 试玩、平台与验收

先 Play Mode 操作核心循环，检查 Console、物理/输入、相机/HUD、暂停/重开和存档；再在独立构建目录启动 Player，检查附带数据、资源/动态加载、保存位置与首次启动。两者分别记录，独立 C# 单测不替代其中任一项。

Web 需验证项目导出配置与所需服务器响应、压缩、WASM/线程/跨源条件；移动需真实 SDK、签名、安装与前后台测试。微信等小游戏适配依赖实际插件/渠道，不把 Unity Web 导出直接称为小游戏。账号、许可或设备缺失保持对应阶段 `not_run`，不擅自切 Web 或重做其他引擎。

排错优先沿首个 Console/导入/编译错误定位：缺包/宏/程序集边界、脚本类名与文件、GUID/序列化字段、渲染管线、输入设置、构建包含场景。只有证据指向缓存问题才考虑有恢复方案的局部缓存重建，不先删 `Library` 或更新全部依赖。

交接包括精确 Editor/模块、包及锁文件、启动场景与输入、构建入口/配置、实际测试/构建日志、产物和未运行平台；缺失原生 SDK、授权或包访问时写具体解锁条件。

## 官方核对入口

2026-11-15 核对下列 Unity 6 页面；按工程实际版本切换：

- [Editor 命令行参数](https://docs.unity3d.com/6000.0/Documentation/Manual/EditorCommandLineArguments.html)。
- [BuildPipeline.BuildPlayer 与 BuildReport](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/BuildPipeline.BuildPlayer.html)。
- [资产元数据与引用](https://docs.unity3d.com/6000.0/Documentation/Manual/AssetMetadata.html)。
