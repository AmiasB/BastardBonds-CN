# Bastard Bonds 简体中文补丁

Bastard Bonds（Steam，作者 Bigfingers）的非官方简体中文补丁。本仓库只有补丁源码、译文和字体构建脚本，**不包含游戏本体**。

针对的游戏版本是 Steam **1.2.9**（Unity 4.7.2f1）。请在自己合法拥有的副本上使用。

## 作者授权

**状态：已获作者授权，可以公开。**

作者 Bigfingers 已允许公开这个汉化补丁。

- 本仓库不提供游戏可执行文件、原版资源或存档。
- 请只给自己拥有的游戏打补丁，不要把打过补丁的游戏目录再发出去。

## 补丁怎么工作

游戏显示文字时才替换成中文。物品、角色、特质、罪名在存档和程序里仍是英文键，存档不会被改写。存档位于 `%USERPROFILE%\Documents\BastardBonds\Save\`。

- 人名、魔脉（Arcus、Lux、Max、Nix、Pox、Rex）和法术专名保持拉丁字母。
- 国名、岛名、地区名和地图上的地点名译成中文。
- 世界地图是贴图。英文地名仍画在图上，下面另写了中文。
- 中文字体是 12px 的像素字，嵌进游戏原来的 `FONT_XBOX_PRE` 图集。
- 词典在游戏第一次显示文字时读入。改了词典要完全退出游戏再开。

## 仓库内容

| 路径 | 内容 |
|---|---|
| `patch/BB_CN.cs` | 运行时翻译。游戏目录里还要有同名的 `BB_CN.dll`。 |
| `patch/patcher/` | 用 Mono.Cecil 改写玩家自己的 `Assembly-CSharp.dll`。 |
| `patch/literals.tsv` | 需要改掉的程序内字符串。取名框允许中文和数字；战斗里加满生命的 Max 改成 HPFull，避免把魔脉名译掉。 |
| `patch/draw_help.py`、`patch/inject_help.py` | 重画五张 F1 说明图，并写回资源。说明图用 `fonts/fp10/` 的 10px 字。 |
| `patch/build_dll.ps1` | 编译 `BB_CN.dll` 并运行补丁器。 |
| `build/BB_CN/*.tsv` | 游戏实际加载的英中词典。 |
| `build_font.py`、`make_charset.py`、`charset.txt` | 把中文字形写进字体图集。 |
| `fonts/fp12/` | [Fusion Pixel](https://github.com/TakWolf/fusion-pixel-font) 12px，SIL OFL 1.1。 |
| `translation/STYLE_GUIDE.md` | 译名和文风。玩家可见的译文以 `build/BB_CN/` 为准。 |

这些内容不在仓库里：反编译结果、游戏原文件备份、打过补丁的 DLL、改过的 `sharedassets0.assets`，以及从游戏里整包抽出的文本。见 `.gitignore`。

## 安装

退出游戏。把整个 `BastardBonds_CN` 文件夹放进游戏根目录，和 `BB.exe` 放在同一层。不要把文件夹里的文件拆出来。放好之后是这样：

```text
Bastard Bonds\
  BB.exe
  BB_Data\
  BastardBonds_CN\
    打补丁.bat
    还原.bat
    使用说明.txt
    cn_patch\
```

然后双击 `BastardBonds_CN` 里面的 `打补丁.bat`。

脚本会先把原版文件备份到 `BB_Data/BB_CN_backup`，再改写程序、换上中文字体、换上五张中文 F1 说明图、拷入词典。只对应 Steam 1.2.9 未改过的 `sharedassets0.assets`、`sharedassets4.assets` 和 `sharedassets5.assets`。想恢复原版，退出游戏后双击同一个文件夹里的 `还原.bat`。

玩家用的压缩包是 `package/BastardBonds_CN.zip`，由 `package/build_package.ps1` 生成。压缩包里没有游戏本体。游戏正在运行时 Windows 会锁住 DLL，脚本会直接停下来。

## 从源码构建

需要 .NET SDK、Python，以及 Python 包 `UnityPy` 和 `Pillow`。补丁器在读取游戏 DLL 时还要能找到游戏自带的 `UnityEngine.dll`。

`patch/build_dll.ps1` 里的游戏目录和 `csc` 路径是本机路径，换机器要先改。它读取一份**未打过补丁**的 `backup/Assembly-CSharp.dll`（这个备份不进仓库），写出 `patch/BB_CN.dll` 和 `patch/Assembly-CSharp.dll`。

补丁器本身的参数是：

```text
patcher <原版 Assembly-CSharp.dll> <BB_CN.dll> <literals.tsv> <输出 DLL> [Managed 目录]
```

字体：

```text
python make_charset.py
python build_font.py charset.txt 输出的 sharedassets0.assets
```

`build_font.py` 读取 `backup/sharedassets0.assets` 里的原版图集，只补上中文字形。

## 字体许可

`fonts/fp12/` 和 `fonts/fp10/` 中的 Fusion Pixel 字体使用 SIL Open Font License 1.1。12px 用于游戏界面，10px 用于 F1 说明图。许可正文在各自目录的 `OFL.txt`。字体不能单独拿去卖，衍生字体也要继续用 OFL。

补丁代码和译文随本仓库公开。玩家包里的 `xdelta3.exe` 是 [Xdelta](https://github.com/jmacd/xdelta) 3.2.2，Apache License 2.0，只用来把字体差异打进玩家自己的资源文件。

## 结语与致谢(2026.11.23)

**项目大体完结！**

我曾有一段时间对人生的意义感到迷茫，害怕被遗忘，总希望能在这个世界上留下些什么。今天这个汉化项目的落幕，也算是向着那个曾经朦胧的愿望迈出了一小步。

### 从2022到2026：跨越四年的执念

汉化本作一直是我的一个心愿。早在2022年刚接触汉化圈并加入**峰青汉化组**时，我便已立项，一边尝试与原作者沟通，一边摸索补丁制作。受限于当时的技术能力，项目在实操阶段屡屡碰壁，最终无奈搁置。

2026年，AI技术在逆向工程与代码理解上的飞跃为游戏社区带来了巨大变革。得益于这一时代红利，当年难以逾越的技术壁垒在如今迎刃而解——仅通过数条提示词，AI便在10分钟内构建出了优雅的汉化补丁架构：

- **高度契合的视觉表现**：实现了美观且完美融入原版美术风格的字体渲染。
- **自动化文本管线**：自动提取了硬编码在源代码各处的5,000+条文本，并通过部署20个并发子Agent完成初翻与术语词典整理，极大缩短了前期周期。
- **图像本地化突破**：仅用半天时间便完成了原先最棘手的图片格式（F1帮助页面）的本地化调试。
- **原版恶性Bug修复**：顺带解决了营地内退出按钮隐藏延迟导致的误触死锁，以及退出营地后短时间内快速返回引发的软锁问题。

### 人工校对与打磨

在AI完成底层框架与初翻后，我在两周的业余时间里（累计游戏时长40小时）完成了全部的人工收尾工作：

- 对照全要素攻略，实机触发并验证了几乎所有剧情分支。
- 逐行肉眼审查了全部5,000+条文本，修复了因转义字符与字典译文格式导致的漏翻，并对生硬的机翻进行了全面润色。
- 累计发布8个迭代补丁，基本解决了目前已知的所有文本与运行问题。

### 致敬原作者

由衷致敬本作的创作者**Geremy Walker**（X、Furaffinity：`@CaptainGerBear`）。作为一名集程序、美术、剧本于一身的全能独立开发者，他一人包办了《See No Evil》与《Bastard Bonds》的全部开发工作，也曾为《Extracurricular Activities》FVN献上过惊艳的画作。自大学时期接触他的作品以来，他便一直是我的偶像。

当最终战那首每轮游戏仅能聆听一次的主题曲响起时，既有对作品完成度的震撼，也有对项目即将收官的不舍。虽然我如今的人生轨迹已与早年渐行渐远，但这个项目，算是给当年的梦想交出了一份满意的答卷。

最后，衷心感谢开发过程中提供帮助的朋友们，以及在B站积极反馈Bug的各位玩家。我的人生也即将迎来下一个重要节点，带着这份热忱与干劲，相信未来依然可期。

**维护说明**：虽然目前汉化主体工作已告一段落，但我仍会持续关注本作动态与社区反馈。如在游玩过程中遇到任何遗漏、Bug 或文本瑕疵，欢迎随时提交 Issue 或留言，我会积极响应并持续跟进更新。

AmiasBerner

Bilibili：狼因夜北
