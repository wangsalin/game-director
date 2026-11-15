# Cocos Creator 专项

适用于 Creator 工程开发/续接/构建。先读[共同流程](README.md)，本页以官方 **Creator 3.8** 文档为命令与 API 核对基线，不强制升级项目，也不承诺其他补丁/大版本完全一致。

## 版本与环境

- 3.x 从项目 `package.json` 的 `creator.version`、项目文档和编辑器 About 交叉核实；`package.json` 的顶层 `version` 是应用/包版本，不能作为引擎版本。Dashboard 是管理器，不等于目标 Creator 编辑器已安装。
- 旧 2.x 常见 `project.json`、`cc.Class`/旧命名空间；3.x 常用 TypeScript、从 `cc` 导入与装饰器。**不能把 3.x 片段直接放进 2.x，也不能将 Cocos2d-x 的 C++ 工程当 Creator。** 迁移是单独范围，保留备份，按官方升级指南检查场景、材质、脚本与平台插件。
- 核实真实 `CocosCreator.exe` / macOS 应用内二进制、精确版本、自定义引擎、插件、目标平台。原生目标另查编译器、Android SDK/NDK/JDK 或 Xcode/签名；版本要求随具体 Creator/平台变化，按当前工程核实，不硬编码一套“通用 SDK”。
- 本机没有 Creator 时，元数据/TS 静态审查可以做；`npm install`、单独 `tsc` 或浏览器运行一个独立 HTML 都不能证明 Creator 导入、构建或小游戏运行。

## 创建/导入与文件边界

新项目通过匹配版本 Dashboard/Creator 原生模板建立，选择符合需求的 2D/3D 模板；已有项目从原根目录打开，等资源导入和脚本处理结束，核对控制台和 Git 差异。不要凭手写几个 JSON 宣称完整 Creator 工程已创建。

`assets/` 放素材、脚本、场景与 Prefab，`settings/` 和 `package.json` 保留项目配置；按项目约定管理 `profiles/`。`library/`、`temp/` 等缓存/临时目录通常不进入源码，构建目录是否留存按交付要求决定，不能全量提交缓存。检查现有 `.gitignore` 而非覆盖。

保留资源及其 `.meta`，Creator 用 UUID 连接场景/Prefab/素材；优先在资源面板移动/重命名，外部移动时连同元数据并复核引用。不要删除 `.meta` 来解决导入报错，或复制同 UUID 当新资源。Inspector 引用、脚本类名和序列化字段变更要检查已有场景数据，不能只看 TS 编译。

## 场景、脚本和可玩切片

1. 明确启动场景、后续场景和构建包含列表。2D UI 核对 Canvas、Camera、UITransform、Widget/布局、层与适配策略；3D 核对相机、光照、单位、坐标和物理设置。按照项目已有结构组织节点，不为小切片引入全局框架。
2. 3.x 组件从 `cc` 导入类型，用 `_decorator` 的 `ccclass/property` 声明；通过 Inspector 绑定类型正确的节点/组件。规则尽量保持可独立测试，组件负责输入/状态显示和场景生命周期。场景/Prefab 用编辑器或经过该版本实测的扩展 API 建立，不臆造序列化内部格式。
3. 让一次键盘/触控操作真实推进状态并刷新显示。事件在合适生命周期成对注册/注销，防止场景重进后重复触发；不在未挂载的脚本中空写功能。检查节点激活、遮挡/层级、坐标空间、碰撞分组及暂停/时间缩放影响。
4. 代表性图片核对 SpriteFrame、尺寸、图集/过滤、透明与锚点；音频核对 AudioSource、首次用户手势和音量；3D 检查模型缩放、材质、骨骼/动画、碰撞与目标渲染管线。
5. Prefab 用实际资源引用及 `instantiate`；动态资源用项目选择的 resources/Asset Bundle 等机制，检查加载失败、异步返回后的节点有效性、重复请求和释放。不要把文件路径存在等同于运行时可加载。

下面只是 3.x 组件骨架，**须在实际场景挂载并绑定 `label` 后才能验证**；不是完整游戏、Prefab 或构建产物：

```typescript
import { _decorator, Component, Label } from 'cc';
const { ccclass, property } = _decorator;

@ccclass('CounterView')
export class CounterView extends Component {
  @property(Label) label: Label | null = null;
  private count = 0;
  public addOne(): void { // 在 Button 点击事件中绑定本组件的此方法
    this.count += 1;
    if (this.label) this.label.string = String(this.count);
  }
}
```

新切片要实际补足业务规则、目标/结算、重开和需求中的输入；此骨架只能用于理解绑定，不能据此报告游戏已实现。

## 预览、调试与构建

先在编辑器预览实际主场景，检查 Console 和浏览器错误；覆盖鼠标/键盘或触控、胜负/持续进度、重开、重复进出、适用的存档和音频。编辑器预览通过后，还要单独构建并从产物启动。

优先在当前版本 Build 面板配置平台、包含场景/启动场景、调试开关、输出路径和实际平台选项，导出 JSON 构建配置并纳入合适的项目配置管理。主场景参数使用资源 UUID，不臆造文件路径充当 UUID。命令行复用导出的配置，避免依赖另一台机器的面板默认值。

以下是 **Windows PowerShell / Creator 3.8** 调用形状；变量先设为本机实际绝对路径，配置必须来自本项目，执行结果尚未由示例证明：

```powershell
# $Creator = 实际 CocosCreator.exe；$Project = 工程根；$Config = 导出的构建 JSON
$buildArgs = @('--project', ('"' + $Project + '"'), '--build', ('"configPath=' + $Config + '"'))
$process = Start-Process -FilePath $Creator -ArgumentList $buildArgs -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 36) { throw "Creator build failed: $($process.ExitCode)" }
```

官方 3.8 文档约定：`32` 参数无效、`34` 构建异常、**`36` 构建成功**。其他返回码不能默认为成功；与实际版本文档/日志对照。GUI 程序需等待真实构建进程，不把成功启动进程当构建完成。必要时在 `--build` 内设置该版本支持的 `logDest` 并保留日志。`--project` 必填；直接使用参数时 `--build "platform=web-desktop;debug=true"` 是官方示例形状，实际平台 ID、输出和场景仍须核实。PowerShell 中含分号的构建参数必须整体引用。

构建后检查日志和预期输出目录/主入口；36 不证明游戏可玩。Web 产物用符合输出要求的 HTTP 服务启动，检查首屏、资源、交互、重进、存档、音频和不同视口；原生需要后续编译/安装步骤，Creator 构建生成工程不等于 APK/IPA 已完成。

## 小游戏与移动目标

先区分 Web H5、微信/其他小游戏、原生 App、工具小程序；分别记录引擎平台支持、AppID/账户、插件/SDK、包体/分包、首包加载、资源域名/HTTPS、存储、前后台与输入/音频限制。按实际目标使用当前可用的平台专项，核对官方要求；不能把 Web 通过写成微信开发者工具、真机或渠道审核通过。

广告、分享、订阅、登录/支付等接口走平台适配层，覆盖失败、重复回调、前后台恢复；没有真实配置和调用保持未接通。构建配置/日志不能携带密钥、签名密码或私人账户数据。实际上传、发布与付费调用仍需对应授权。

## 常见排错与退出

| 现象 | 优先检查 |
|---|---|
| 脚本不执行/属性丢失 | 2.x/3.x 混用、类名/装饰器、脚本是否挂载、节点激活、Inspector 绑定/序列化变化 |
| 素材丢失/Prefab 断引用 | `.meta`/UUID、重命名方式、导入错误、构建场景和动态资源包含 |
| 预览可用但构建白屏 | 构建平台/启动场景、资源加载路径、网络/压缩/跨域条件、浏览器控制台 |
| 手机按钮错位/重复响应 | Canvas 适配/安全区、触控与鼠标重复监听、生命周期未清理 |
| CI 报失败但产物存在 | 真实退出码、36 判据、日志与本次输出；不能因产物目录存在就吞错 |

交付源码与 `.meta`、启动场景/绑定说明、精确版本、构建 JSON/步骤、依赖与平台缺口、日志/产物/流程证据。Creator、Web、小游戏工具、原生编译和实体设备分阶段记录；没运行保持 `not_run`。

## 官方核对入口

2026-11-15 核对以下 3.8 页面；执行时重新选择工程实际版本：

- [工程结构](https://docs.cocos.com/creator/3.8/manual/en/getting-started/project-structure/index.html)、[meta 与 UUID](https://docs.cocos.com/creator/3.8/manual/en/asset/meta.html)。
- [组件](https://docs.cocos.com/creator/3.8/manual/en/scripting/component.html)、[实例化与销毁](https://docs.cocos.com/creator/3.8/manual/en/scripting/create-destroy.html)。
- [命令行构建、配置与退出码](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html)、[2.x→3.0 升级差异](https://docs.cocos.com/creator/3.8/manual/en/release-notes/upgrade-guide-v3.0.html)。
