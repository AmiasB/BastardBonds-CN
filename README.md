# Bastard Bonds 简体中文补丁

Bastard Bonds（Steam，作者 Bigfingers）的非官方简体中文补丁。本仓库只有补丁源码、译文和字体构建脚本，**不包含游戏本体**。

针对的游戏版本是 Steam **1.2.9**（Unity 4.7.2f1）。请在自己合法拥有的副本上使用。

## 作者授权

**状态：等待中。**

已准备联系作者 Bigfingers，请求允许公开这个汉化补丁。在作者回复之前：

- 本仓库不提供游戏可执行文件、原版资源或存档。
- 请只给自己拥有的游戏打补丁，不要把打过补丁的游戏目录再发出去。
- 若作者拒绝或要求下架，以作者的要求为准。

## 补丁怎么工作

游戏显示文字时才替换成中文。物品、角色、特质、罪名在存档和程序里仍是英文键，存档不会被改写。存档位于 `%USERPROFILE%\Documents\BastardBonds\Save\`。

- 人名、魔脉（Arcus、Lux、Max、Nix、Pox、Rex）和法术专名保持拉丁字母。
- 国名、岛名、地区名和地图上的地点名译成中文。
- 世界地图图片上画死的地名改不了，那是贴图，不是文字控件。
- 中文字体是 12px 的像素字，嵌进游戏原来的 `FONT_XBOX_PRE` 图集。
- 词典在游戏第一次显示文字时读入。改了词典要完全退出游戏再开。

## 仓库内容

| 路径 | 内容 |
|---|---|
| `patch/BB_CN.cs` | 运行时翻译。游戏目录里还要有同名的 `BB_CN.dll`。 |
| `patch/patcher/` | 用 Mono.Cecil 改写玩家自己的 `Assembly-CSharp.dll`。 |
| `patch/literals.tsv` | 需要改掉的程序内字符串。目前只放宽了取名框，使中文和数字可以留下。 |
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

脚本会先把原版文件备份到 `BB_Data/BB_CN_backup`，再改写程序、换上中文字体、拷入词典。只对应 Steam 1.2.9 未改过的 `sharedassets0.assets`。想恢复原版，退出游戏后双击同一个文件夹里的 `还原.bat`。

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

`fonts/fp12/` 中的 Fusion Pixel 字体使用 SIL Open Font License 1.1，正文在 `fonts/fp12/OFL.txt`。其中合并的 cubic-11、ark-pixel 许可在 `fonts/fp12/LICENSES/`。字体不能单独拿去卖，衍生字体也要继续用 OFL。

补丁代码和译文的许可证，等作者授权有结果后再定。玩家包里的 `xdelta3.exe` 是 [Xdelta](https://github.com/jmacd/xdelta) 3.2.2，Apache License 2.0，只用来把字体差异打进玩家自己的资源文件。
