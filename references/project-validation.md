# 项目文件验收

交付策划包、更新资产清单或检查既有项目时，用[项目脚本](../scripts/validate_project.py)做只读检查。需要 Python 3.10+，仅使用标准库，不安装依赖、不改文件、不启动游戏、不调用网络或付费工具。

## 调用

从任何工作目录运行（将 `<skill-dir>`、`<project-root>` 换成实际路径）：

```text
python -B "<skill-dir>/scripts/validate_project.py" "<project-root>"
python -B "<skill-dir>/scripts/validate_project.py" "<project-root>" --release
```

默认在项目内查找 `ASSET_MANIFEST.csv` 与可选 `AUDIO_MANIFEST.csv`，跳过 `.git/node_modules/.godot/Library` 等生成目录及符号链接目录。自定义文件名用可重复参数 `--asset-manifest relative/path.csv`、`--audio-manifest relative/path.csv`，不要求移动已有工程。CSV 沿用模板的完整列名/顺序；其他结构先记录映射并保留原文件，不能静默改写。不能把 Skill 自身目录当项目根目录。

## 检查什么

- 根目录有非空 README.md；从 README 和证据 Markdown 沿内联链接/图片链接检查文件是否存在、Markdown 标题锚点是否有效。LITE 合并章节和 STANDARD 分目录都适用。支持中文、空格、百分号编码、常用括号文件名、ATX/Setext 标题与显式 HTML 锚点；不是完整 CommonMark/HTML 解析器，不检查引用式链接、任意 HTML 链接或纯文本路径。
- CSV 表头、唯一 ID（包括跨清单重复）、枚举、数值及状态一致性；不允许残留 `EXAMPLE-` 模板行。
- 清单路径相对项目根目录；Markdown 链接相对所在文档。不允许本地绝对路径、file URI、逃逸路径或越界符号链接；远程 URL 不抓取、不认证有效性。
- planned/in_progress 可以登记未来文件；ready 或 approved/integrated/已验证记录要求源/导出文件真实存在且非空。approved/integrated/已验证还要求实际证据文件。`deprecated` 历史行不纳入当前文件/发布资产检查。
- PNG 检查签名、块结构、CRC、声明尺寸及透明通道要求；这是容器/元数据检查，不解码图像、不审查视觉质量。PCM WAV 检查实际样本是否完整、时长、采样率、声道；时长允许 5ms 或一个采样点的较大者作为舍入误差。
- JPEG/WebP/SVG、压缩或不支持的 WAV、模型、骨骼、材质、动画等输出 manual 警告，需用对应工具/引擎检查；不伪装成已经解码/验收。

未定授权/来源、planned 资产和不支持的格式输出 WARNING。缺文件、规格不符、PNG/WAV 的已检查容器错误、断链和状态矛盾输出 ERROR，退出码 1；无 ERROR 返回 0，同时保留警告。

`--release` **仅加强当前资产记录检查**：至少有一项当前资产；所有非 deprecated 项必须是 ready/approved/integrated/passed，且美术为 production；拒绝已知未定 license/provenance。它不判断授权文本是否合法、不核实证据陈述、不发现漏登记素材，也不验证构建、引擎、模型质量、真机、玩法或商店条件。通过脚本不能报告为“发布就绪”，必须继续执行项目自身 QA 和发布验收。

## 如何处理结果

文件检查通过时报告“项目文件检查通过，原型/真机按实际结果另列”。planned 行通过表示策划可以继续，不代表生产完成。证据不存在时保持 not_reviewed/not_integrated/not_run 或准确记录失败，不新建虚假证据填满字段。只在既有明确授权覆盖相应工作时制作资产或改代码。

独立编码交接仍须自包含：记录项目自身校验命令；若接收环境没有安装本 Skill，不把本机 Skill 绝对路径设成唯一验证入口。可以按授权复制两个校验脚本 `validate_project.py` 和其同目录依赖 `validate_skill.py`，或写明此辅助检查未在接收环境运行。

维护脚本时运行[真实文件回归测试](../scripts/test_validate_project.py)。测试在临时目录生成有效 PNG/PCM WAV，再验证缺失、损坏、错误规格、证据和路径场景；测试数据不代表任何游戏的真实 QA 证据。
