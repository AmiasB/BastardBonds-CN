# Bastard Bonds 简体中文翻译规范

Bastard Bonds 是 Bigfingers（See no Evil 的作者）做的回合制地牢 RPG：玩家是被流放到 Lukatt 岛的罪犯，带着一队同样被定罪的同伴战斗、招募、勒索、建立据点。基调黑暗、粗俗、带黑色幽默，有成人内容。**忠实翻译**：脏话、性内容、暴力描写照实翻，不弱化、不添加。

## 输出格式

每个输入行是 JSON：`{"id", "en", "cat", "ctx"}`。`ctx` 是来源（代码行或数据字段），只用于理解语境。

输出文件每行一个 JSON：`{"id": "...", "zh": "..."}`，UTF-8，不带 BOM，顺序与输入一致，每个 id 恰好一行。

- **`zh` 写 `=`**：表示该字符串不是玩家可见文本（内部标识、动画名、文件名、调试信息），或者是应保持英文的人名，不需要翻译。拿不准是否可见时就翻译（翻译多了无害）。
- **占位符** `{0}` `{1}`…：每个占位符必须原样出现且次数一致，可以调整位置。占位符代表运行时插入的内容（人名、数字、物品名、技能名等），看 `ctx` 判断。
- **换行** `\n`：`zh` 中 `\n` 的数量必须与 `en` 相同（段落结构保持一致）。形如 `Force\n{0}` 的"标签\n数值"结构尤其不能动。
- 字符串首尾的空格保持原样。
- `$` 是游戏货币符号，保留。`HP`、`Lv` 保留。
- 引号：英文的 `"…"` 对话引号译为中文 `“…”`；`'Defense'` 这种单引号引用的术语译为 `“防御”`。
- 标点用中文全角标点（，。！？：；……——），数字和英文保持半角。
- 不要用 `|` 字符。

## 名称

- **人名一律保留英文**：同伴（Bato、Beauregard、Borfalgor、Borgnina、Byrne、Grant、Greave、Greening、Kirilo、Leftie、Logus、Moria、Nazar、Paul、Peregrine、Rangda、Rosaline、Shapiro、Vankan、Wisaka、Zantanak 等）、NPC 名、随机生成的人名、神祇/魔王名（Leviathan、Glamig 等）。
- **只有人名保留英文**。国名、岛名、地区名、地图地点名都要译成中文。没有实义的专名用音译，英语普通名词按意思译。已锁定：Lukatt 卢卡特，Crest 克雷斯特，Tsarath 察拉思，Greenback 绿背，Knightwood 骑士林，Hayill 海伊尔，Arpa 阿尔帕，Chrun 克伦，Klarthus 克拉图斯，Arkasin 阿卡辛，Zias 齐亚斯，Marsaven 马尔萨文，Blackglass 黑璃，Ferris 费里斯，Galiere 加利尔，Cartoe 卡托，Brad'uk 布拉杜克，Pagewood 侍从林，Knavewood 无赖林，Bracewind 布雷斯温德，Coldforge 冷锻，Whetners 惠特纳，Yaksteppe 牦牛草原，Miser's Purse 守财奴钱袋。人名仍留英文，所以 Frico's Castle → Frico城堡，Glamig's Tomb → Glamig之墓，Fastad's Archive → Fastad档案库，Laughlan Manor → Laughlan庄园，Emitt Manor → Emitt庄园。地图底图上画死的湖名改不了。
- **魔法派系与法术专名保留英文**：Arcus、Lux、Max、Nix、Pox、Rex（魔法派系，统称 magic vein → 魔脉）；Imarcus、Arximum、Luxsoul 等法术/魂名保留英文。
- **怪物/生物种类要翻译**（Goblin 哥布林、Skeleton 骷髅、Starved Wolf 饥饿的狼……）。NPC 名单里像 `Paul Nude`、`Moria Stand`、`Thrall E.` 这种带状态后缀的条目是内部变体，人名变体写 `=`；职业类通用名（Blacksmith、Trader）照常翻译。
- 物品名要翻译，简洁、像装备名（Worn Knife 破旧小刀、Claymore 双手巨剑、Lucky Ring 幸运戒指）。宝石：Ruby 红宝石、Sapphire 蓝宝石、Emerald 祖母绿、Diamond 钻石、Onyx 缟玛瑙。

## 核心术语表（必须统一）

### 属性（三轴 × 三维）
| 英文 | 中文 | 说明 |
|---|---|---|
| Force | 力量 | 基础属性 |
| Guile | 诡诈 | 基础属性 |
| Magic | 魔力 | 基础属性 |
| Attack | 攻击 | 方向 |
| Defense | 防御 | 方向；作为状态时也是“防御” |
| Utility | 辅助 | 方向 |
| Fight | 格斗 | 力量×攻击 |
| Guard | 守护 | 力量×防御 |
| Labour | 劳作 | 力量×辅助 |
| Hunt | 狩猎 | 诡诈×攻击 |
| Dodge | 闪避 | 诡诈×防御 |
| Thwart | 破解 | 诡诈×辅助（开锁、解陷阱等） |
| Blast | 施法 | 魔力×攻击 |
| Ward | 护佑 | 魔力×防御 |
| Weave | 编织 | 魔力×辅助 |

技能栏上的蓝点叫 pip → 点；development points → 成长点数；level 等级；HP 生命值（界面缩写保留 HP）；Move 移动力；Carry / carrying load 负重；manpower 人力；surplus 盈余。

### 战斗机制
risk 风险；reckless (attack/action) 鲁莽（攻击/行动）；fumble 失手；hesitate / Hesitant 犹豫；initiative 先机；bloodied 重伤/浴血（低血量状态，用“重伤”）；bleeding 流血；incapacitated 倒地不起；turn 回合；round 轮；challenge 挑战（labour challenge 劳作挑战）；ransom 勒索赎金；recruit 招募；conscript 征召；negotiate 交涉。

### 状态 (condition)
Normal 正常；Fumble 失手；Defense 防御；Hesitant 犹豫；Invulnerable 无敌；Grace 优雅；Rage 狂怒；Focus 专注；Shadowcloak 暗影斗篷；Vigor 活力；Daze 眩晕；Pain 剧痛；Nexus 连结；Poison 中毒；Entangle 缠绕；Lucky 走运；Unlucky 倒霉；Meteoric 流星。

### 性格/阵营 (alignment)
Innocent 无辜；Violent 暴戾；Frugal 吝啬；Godless 无神；Impassioned 狂热；Detached 冷漠；Opportunist 投机；Heartless 无情；Touched 疯癫。
对话性格：Adventurous 爱冒险、Angry 易怒、Arrogant 傲慢、Heroic 英勇、Insane 疯狂、Lewd 淫荡、Miserable 悲惨、Pathetic 可悲、Revelrous 爱狂欢、Terse 寡言、Timid 胆小、Violent 暴戾。

### 罪名 (crime)
Murder 谋杀；Thievery 盗窃；Heresy 异端；Apostasy 叛教；Extortion 敲诈；Miscegenation 异族通婚；Conspiracy 密谋；Treason 叛国；Indecency 有伤风化；Fraud 欺诈；Rape 强奸；Blackmail 勒索；Abduction 绑架；Arson 纵火；Banditry 抢劫；Assault 伤害；Rioting 暴乱；Blasphemy 亵渎；Malediction 诅咒；Buggery 鸡奸；Desertion 逃兵；Forgery 伪造；Racketeering 敲诈勒索团伙罪（可简作“黑帮勒索”）；Quackery 行医诈骗；Slavery 奴役；Desecration 亵渎圣物；Necromancy 死灵术；Vandalism 蓄意破坏；Cannibalism 食人；Profiteering 牟取暴利。
法庭用语：the court 法庭；plea 申辩；guilty 有罪；innocent 无罪（作阵营名时是“无辜”）；Alleged {0} → “涉嫌{0}”；Convicted of {0} → “因{0}定罪”。

### 物品栏位 (itemSlot)
Accessory 饰品；Armour 护甲；Artifact 奇物；Food 食物；Potion 药剂；Supplies 补给；Weapon 武器；Junk 杂物。grimoire 魔典；stave/staff 法杖；rod 法杖（Rod 类物品名用“杖”）；gem 宝石。

### 据点与角色
stronghold 据点；band 团伙（玩家的队伍。Band of {0} → “{0}的团伙”）；party 队伍；party member 队员；leader 首领；merchant 商人；trader 商贩；healer 治疗师；porter 脚夫；locksmith 锁匠；keysmith 制钥匠；quartermaster 军需官；blacksmith 铁匠；forgemaster 锻造大师；appraiser 估价师；arbiter 仲裁人；courier 信使；barkeep 酒保；the stocks（岛上关押罪犯的设施）枷场。

### 种族 (race)
Human 人类；Orc 兽人；Giant 巨人；Beast 野兽；Beastman 兽人族（与 Orc 区分）；Construct 构装体；Demon 恶魔；Undead 亡灵；Spirit 灵体；Amorph 无形体；Machine 机械；Kami 神灵；Amazon 亚马逊女战士；Temptress 妖女；Widow 寡妇；Stud 种马；Twerp 小屁孩。Lycanthrope 狼人族；werewolf 狼人；vampire 吸血鬼；goblin 哥布林。

## 文风

- 界面文本：简短直白，像正式游戏的 UI（“读取游戏”“返回主菜单”“开 / 关”）。按钮文字尽量 2–6 个字。
- 说明文本（技能、选项说明、加载提示）：清楚准确，术语严格按术语表。
- 叙事文本（结局、过场、对话）：自然流畅的中文小说语气，保留粗口与黑色幽默；同伴说话有个性（粗人就说粗话）。
- 不要加译注，不要解释双关；双关尽量用中文重新做一个，做不出来就意译。

## 已锁定的译名（第一阶段各块必须一致）

- 技能：Hardworking 勤劳；Crafty 机巧；Ritualist 仪式师。Innocent 作技能名和阵营名时都是“无辜”；法庭上的 not guilty 才是“无罪”。技能 Boss 是“头目”，罪名绰号里的 boss 仍是“工头”。
- 守序 / 中立 / 混乱（law / neutral / chaos）。
- 牢房绰号：orcfucker 操兽人的；runtfucker 操矮子的；muckfucker 操屁眼的；pinch 扒手；streak 裸奔的；maledicus 咒师；bonemage 骨法师；munchy 啃人的。slavery 与 profiteering 的 boss 都是“工头”。
- 默认名：Defendant 被告；Unnamed Bastard 无名混蛋；Reanimated Guard 复生卫兵。
- 沉没教团（Sunken Order）；嚎月诗人（The Howling Bard）；膳食大师（dinnermaster）；雇佣兵团（mercenary band，区别于玩家的“团伙”）。
- 沉没祷词必须和填空用同一套词，否则女王修道院的默诵解不开。四行是：荣耀者在沉没之海，／主 Leviathan 即是他。／听我们的声音，干燥的上方，／回响穿过卤水，我们的爱。正确填空是“在沉没之”“即是他”“干燥的”“卤水”；干扰项“号令这片”“应受赞美”“高高的”“一切时光”不能出现在祷词正文里。物品名 Sunken Prayer 已定为“沉没祈祷”。
- 服装：Gi 道服；Hakama 袴；Mawashi 相扑带；Cup 护裆。
