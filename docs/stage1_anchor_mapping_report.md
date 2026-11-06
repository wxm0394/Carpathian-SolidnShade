# 方案 C 阶段 1 & 阶段 2 归档报告：锚点几何对齐、海钓重绑与 S&S ↔ 1521 全聚落权威映射总表

> [!IMPORTANT]
> **落盘状态总览**：
> 1. **阶段 1（几何锚点对齐）**：基于 [map.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/map.txt)（6,779 顶点 / 13,111 三角面）校验，[parties.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/parties.txt) 全部 **210 个槽位（ID `0..209`）** 不可通行网格残留数为 **0**（备份于 [parties.txt.bak_stage1](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/parties.txt.bak_stage1)）。
> 2. **阶段 2（海钓重绑 & 双语纯 1521 地名替换）**：已将 [triggers.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/triggers.txt) 的 2 个内陆海钓村改绑至黑海与爱琴海沿岸，并对 **6 个英文 `.txt` 文件（共 164 行）** 与 **5 个简体中文 `languages/cns/*.csv` 文件（共 165 行 + 补译 15 行）** 完成纯 1521 历史地名对齐，中英文旧地名残留均为 **0**（全部修改前原件均已自动备份为 `*.bak_stage2`）。

---

## 一、 阶段 1 已落盘修复的 21 个异常/错位锚点汇总

### 1. 核心剧情、刑场与刷新锚点修复（6 处）

| 槽位 ID | 内部标识符 | 1521 显示名称 | 修复前坐标与故障 | 修复后精确坐标与地形 | 关联脚本/菜单引用与修复意义 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`18`** | `p_zendar` | `Old_Zendar` | `(-45.00, 72.00)` ❌多瑙河水面 | **`(-40.624153, 64.580136)`** `plain=3` | [menus.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/menus.txt#L37) 旧曾扎尔出身及 `The_Unknown` (`37`) 重定位不再卡死河中 |
| **`201`** | `p_bloodfountain_spawn_point` | `bloodfountain_sp` | `(72.00, 174.00)` ⚠️与旧曾扎尔脱节 | **`(-40.624153, 64.580136)`** `plain=3` | 恢复原版 S&S 中 `p_zendar` 与血泉刷新点严格同轴锁定的空间设计 |
| **`176`** | `p_training_ground_2` | `Old_Breaking_Field` | `(-114.00, 245.10)` ❌蒂萨河水面 | **`(-110.333161, 243.868522)`** `plain=3` | 修复坐标粗暴 $\times 3$ 落入河道导致玩家无法进入旧裂刑场搜集刑具的死锁 |
| **`196`** | `p_steppe_bandit_spawn_point` | `steppe_bandit_sp` | `(121.12, -219.57)` ❌不可通行河道 | **`(117.099121, -216.431366)`** `plain=3` | 修复草原强盗刷新与游牧出身卡死在河道内的 Bug |
| **`171`** | `p_test_scene` | `test_scene` | `(32.40, -58.80)` ❌高山 `mountain=1` | **`(12.150787, -70.056364)`** `plain=3` | 移出不可通行高山网格 |
| **`172`** | `p_battlefields` | `battlefields` | `(32.40, -49.80)` ❌高山 `mountain=1` | **`(36.636001, -32.885732)`** `plain=3` | 移出不可通行高山网格 |

### 2. 15 座桥梁（`p_bridge_1..15`）重对齐至 1521 真实跨河渡口

| 槽位 ID | 标识符 | 新对齐渡口坐标 | 网格地形 | 桥面弧度角 | 1521 对应水系与邻近地标 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`180`** | `p_bridge_1` | **`(-247.47, 83.26)`** | `ford=7` | `1.6805` | 萨瓦河渡口（近 Sisak） |
| **`181`** | `p_bridge_2` | **`(-72.34, -17.09)`** | `ford=7` | `0.4992` | 摩拉瓦河渡口（近 Krusevac） |
| **`182`** | `p_bridge_3` | **`(-123.99, 188.36)`** | `ford=7` | `2.2521` | 蒂萨河中游渡口（近 Szeged） |
| **`183`** | `p_bridge_4` | **`(178.39, -122.85)`** | `ford=7` | `1.3300` | 马里查河渡口（近 Edirne） |
| **`184`** | `p_bridge_5` | **`(223.43, -244.53)`** | `ford=7` | `2.4246` | 达达尼尔海峡浅滩（近 Sultaniye） |
| **`185`** | `p_bridge_6` | **`(-256.96, 308.68)`** | `plain=3` | `1.4684` | 多瑙河上游通道（近 Pozsony） |
| **`186`** | `p_bridge_7` | **`(-184.39, 226.69)`** | `plain=3` | `2.6672` | 多瑙河中游通道（近 Buda） |
| **`187`** | `p_bridge_8` | **`(-163.29, 119.70)`** | `plain=3` | `1.4240` | 多瑙-德拉瓦河口通道（近 Mohacs） |
| **`188`** | `p_bridge_9` | **`(-167.80, 76.22)`** | `plain=3` | `2.2591` | 萨瓦河下游通道（近 Mitrovica） |
| **`189`** | `p_bridge_10` | **`(-88.49, 93.56)`** | `plain=3` | `2.9689` | 多瑙-蒂萨汇流通道（近 Belgrade） |
| **`190`** | `p_bridge_11` | **`(57.56, 21.71)`** | `plain=3` | `0.1537` | 多瑙河铁门下段通道（近 Turnu Magurele） |
| **`191`** | `p_bridge_12` | **`(217.23, 65.62)`** | `plain=3` | `1.6013` | 多布罗加多瑙河通道（近 Silistra） |
| **`192`** | `p_bridge_13` | **`(249.13, 156.98)`** | `plain=3` | `2.1238` | 普鲁特-多瑙河口通道（近 Reni/Braila） |
| **`193`** | `p_bridge_14` | **`(298.37, 125.88)`** | `plain=3` | `3.0638` | 多瑙河三角洲北支通道（近 Chilia） |
| **`194`** | `p_bridge_15` | **`(-43.26, 316.15)`** | `plain=3` | `1.3871` | 蒂萨河上游通道（近 Szabolcs） |

---

## 二、 阶段 2：海钓/巨鲸吞噬槽位重绑与中英双语纯 1521 地名对齐

### 1. 海钓与利维坦（鲸腹迷宫）5 大触发海岸村重绑结果

在 [triggers.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/triggers.txt#L57-L60) 第 `57..60` 行中，引擎通过 `store_distance_to_party_from_party (2281)` 判定玩家与 5 个指定村庄距离是否 `< 1` 来区分内陆河钓与加速海钓（含 1% 概率被利维坦巨鲸吞入腹中触发 `menu 1249`）。
经核对 `parties.txt` 精确索引与 `map.txt` 海岸线顶点距离（注：槽位 `159 p_village_82` 实为摩尔达维亚北部内陆 `Botosani`，真正的黑海恩伊萨拉湾 Enisala/Razim 沿岸村槽位为 **`160 p_village_83 Babadag`**），已完成如下重绑（不影响 `143 Gyula` 原有的安娜贝尔·李墓穴场景）：

| 海钓寄存器 | 原槽位与地理错位 | 现绑定槽位 | 1521 英文名 | 1521 中文名 | 坐标与海域归属 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `:var0` (`reg0`) | ❌ `133`（内陆 `Tighina`） | **`158`** (`p_village_81`) | **`Mangalia`** | **曼加利亚** | `(270.96, 27.63)` **黑海西岸港口（阶段 3 对齐）** |
| `:var1` (`reg1`) | `112`（原 `Fearichen`） | **`112`** (`p_village_35`) | `Constanta` | **康斯坦察港社** | `(271.89, 52.71)` 黑海西岸大港（鲸腹逃生冲上岸点） |
| `:var2` (`reg2`) | ❌ `143`（匈牙利腹地 `Gyula`） | **`160`** (`p_village_83`) | **`Babadag`** | **巴巴达格** | `(270.69, 101.93)` **黑海恩伊萨拉湾（Enisala）海岸** |
| `:var3` (`reg3`) | ❌ `144`（内陆 `Vaslui`） | **`125`** (`p_village_48`) | **`Rodoscuk`** | **罗多斯楚克** | `(246.72, -173.81)` **马尔马拉海港口（阶段 3 对齐）** |
| `:var4` (`reg4`) | ❌ `113`（塞尔维亚内陆 `Kosovo`） | **`118`** (`p_village_41`) | **`Gelibolu_Gallipoli`** | **格利博卢（加里波利）** | `(214.53, -220.26)` **爱琴海/达达尼尔海峡海岸** |

### 2. 中英双语批量替换统计与关键边界修复清单

| 文件路径 | 更新行数 | 核心修复内容摘要 |
| :--- | :--- | :--- |
| [triggers.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/triggers.txt#L57-L60) | 4 行 | 海钓距离判定槽位 `143 -> 160` (`Babadag`)、`113 -> 118` (`Gelibolu_Gallipoli`) |
| [item_kinds1.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/item_kinds1.txt#L679-L687) | 3 行 | 三大解咒草药改名：`Neamt_Garlic`、`Poenari_Aconite`、`Braila_Mullein` |
| [troops.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/troops.txt#L3398-L3426) | 2 行 | 英文复国者头衔地名对齐：`Lady_Isolla_of_Pecs`、`Lord_Kastor_of_Sibiu` |
| [conversation.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/conversation.txt) | 33 行 | 修复原作者拼写错误 `Rhadogir_Castle`/`Rhadogir_Garlic` $\to$ `Neamt_Citadel`/`Neamt_Garlic`；对齐博物馆挂毯 22 处秘境、罗宾汉 `Wallachian_Forest`/`Pozsony`、矿主通缉令 `Edirne`、地牢藏匿点 `Buda` 等 |
| [menus.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/menus.txt) | 15 行 | 对齐四方客栈与黑市 4 扇传送门 (`Targoviste`/`Jassy`/`Edirne`/`Kolozsvar`)、鲸腹逃生海岸 (`Constanta`)、酷刑笔记 (`Braila`/`Vaslui`)，精准保留普通短语 `a_circle_of_standing_stones` |
| [strings.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/strings.txt) | 109 行 | 对齐通灵板 18 主城全大写答案 (`TARGOVISTE..SALONIKA`)、NPC 姓氏后缀（含拼写异体 `Uxhal`/`Uxkhall`/`Ehlerdag`/`Culdarr_pass`/`Velucan_wine`）、全部 34 名同伴背景故事，精准保留老兵人名 `Grunwalder` |
| [quick_strings.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/quick_strings.txt) | 2 行 | 出身背景故事 `Praven -> Buda`、`Halmar -> Edirne` |
| [dialogs.csv](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/languages/cns/dialogs.csv) | 34 行 (+15 行补译) | 修正博物馆挂毯 1.011 错位旧译（如 `林迪阿尔` $\to$ `普列波列`、`阿茨加德` $\to$ `锡比乌`、`马曾` $\to$ `索菲亚`、`乌尔布尔班` $\to$ `萨洛尼卡`）；修复 `dlga_fountain1` 误粘贴交任务文本的致命 Bug；补齐杰克·弗罗斯特关于无限之石在 `布勒伊拉堡垒` 梅菲斯特手中的 15 行漏译对话 |
| [game_menus.csv](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/languages/cns/game_menus.csv) | 26 行 | 四方客栈 4 扇传送门按钮汉化、鲸腹逃生海岸 `康斯坦察港社`、处决剧情 `埃迪尔内`、罗宾汉剧情 `波若尼（布拉迪斯拉发）` |
| [game_strings.csv](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/languages/cns/game_strings.csv) | 97 行 | 修复 `str_tutorial_map4` 误把 `Nomar` 译作 `苏诺` 的错译（改为 `波若尼（布拉迪斯拉发）`）；重译 `str_npc21_home_*` 还原爱伦·坡《告密的心》指向 **`雅西酒馆地下室`** 的核心彩蛋线索；统一全部同伴家乡与姓氏汉化 |
| [item_kinds.csv](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/languages/cns/item_kinds.csv) | 6 行 | `尼亚姆茨大蒜`、`波耶纳里乌头`、`布勒伊拉毛蕊花`（单复数） |
| [quick_strings.csv](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/languages/cns/quick_strings.csv) | 2 行 | 苦役矿山出身 `埃迪尔内`、流亡贵族出身 `布达城` |

---

## 三、 博物馆挂毯 22 处秘境新旧名称速查表（`dlga_tapestry1c` & `1e`）

| 秘境内容 | S&S 原版地名 | 槽位 ID | 1521 历史英文名 | 1521 官方中文名 |
| :--- | :--- | :--- | :--- | :--- |
| 主教塔 (Bishop's Tower) | `Fenada` | `133` | `Tighina` | **蒂吉纳（本德尔）** |
| 波塞冬神庙 (Temple of Poseidon) | `Fearichen` | `112` | `Constanta` | **康斯坦察港社** |
| 安娜贝尔·李之墓 (Sepulchre of Annabelle Lee) | `Fisdnar` | `143` | `Gyula` | **久洛** |
| 吸血鬼洞穴 (Cave) | `Tebandra` | `144` | `Vaslui` | **瓦斯卢伊** |
| 付丧神三要塞 (Three Castles) | `Jelbegi, Ryibelet, Reindi Castles` | `73, 62, 61` | `Silistre_Fortress, Ozalj_Castle, Kanizsa_Castle` | **锡利斯特拉要塞、奥扎利城堡、考尼饶要塞** |
| 狼人小屋 (Hut) | `Ambean` | `108` | `Braila` (村) | **布勒伊拉郊庄** |
| 旧风车 (Old Windmill) | `Chelez` | `161` | `Tulcea` | **图尔恰** |
| 酒馆地下室《告密的心》(Tavern Basement) | `Khudan` | `27` | `Jassy` | **雅西** |
| 古老石塔 (Old Stone Tower) | `Glunmar` | `104` | `Prijepolje` | **普列波列** |
| 暗影塔 (Shadow Tower) | `Uslum` | `97` | `Pecs` (村) | **佩奇郊庄** |
| 地底冥府大门 (Underworld Gate) | `Veidar` | `125` | `Rodoscuk` | **罗多斯楚克** |
| 蛇坛 (Snake Altar) | `Ergellon_Castle` | `52` | `Brasov_Kronstadt` | **克隆施塔特要塞** |
| 杂货店密室 (Store) | `Veluca` | `21` | `Sibiu` | **锡比乌** |
| 鲜血方尖碑 (Blood Obelisk) | `Dashbigha` | `102` | `Gacko` | **加茨科** |
| 酒馆秘境 (Tavern) | `Ichamur` | `35` | `Sofia` | **索菲亚** |
| 阿佛洛狄忒神庙 (Temple of Aphrodite) | `Narra` | `36` | `Salonika` | **萨洛尼卡** |
| 失落的圣骨匣 (Lost Reliquary in Castle) | `Halmar` | `32` | `Edirne` | **埃迪尔内** |
| 雅典娜神庙 (Temple of Athena) | `Tulbuk` | `165` | `Barlad` | **伯尔拉德** |
| 古墓 (Tomb) | `Zagush` | `120` | `Usak` | **乌沙克** |
| 伊施塔尔祭坛 (Altar of Ishtar) | `Dugan` | `118` | `Gelibolu_Gallipoli` | **格利博卢（加里波利）** |

---

## 四、 权威总表：全聚落与特殊据点《S&S 原名 ↔ 1521 历史名》完整映射（169 项）

| 槽位 ID | 内部标识符 | S&S 英文原名 | S&S 旧汉化名 | 1521 历史英文名 | 1521 官方汉化名 | 1521 精确坐标 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `18` | `p_zendar` | `Old_Zendar` | 旧曾扎尔 | **`Old_Zendar`** | **旧曾扎尔** | `(-40.62, 64.58)` |
| `19` | `p_town_1` | `Sargoth` | 萨尔戈特 | **`Targoviste`** | **特尔戈维什特** | `(125.49, 92.73)` |
| `20` | `p_town_2` | `Tihr` | 蒂赫尔 | **`Bucharest`** | **布加勒斯特** | `(156.98, 60.60)` |
| `21` | `p_town_3` | `Veluca` | 弗吕卡 | **`Sibiu`** | **锡比乌** | `(61.95, 147.91)` |
| `22` | `p_town_4` | `Suno` | 苏诺 | **`Pecs`** | **佩奇** | `(-202.93, 144.82)` |
| `23` | `p_town_5` | `Jelkala` | 热尔卡拉 | **`Kolozsvar`** | **克劳森堡** | `(31.61, 212.78)` |
| `24` | `p_town_6` | `Praven` | 普拉芬 | **`Buda`** | **布达** | `(-175.56, 246.42)` |
| `25` | `p_town_7` | `Uxkhal` | 乌克斯哈尔 | **`Belgrade`** | **贝尔格莱德** | `(-96.18, 66.80)` |
| `26` | `p_town_8` | `Reyvadin` | 雷瓦金 | **`Suceava`** | **苏恰瓦** | `(144.55, 283.22)` |
| `27` | `p_town_9` | `Khudan` | 胡丹 | **`Jassy`** | **雅西** | `(206.67, 254.31)` |
| `28` | `p_town_10` | `Tulga` | 图勒和 | **`Constantinople`** | **君士坦丁堡** | `(307.32, -146.76)` |
| `29` | `p_town_11` | `Curaw` | 楚拉辅 | **`Hotin`** | **霍京** | `(149.56, 343.36)` |
| `30` | `p_town_12` | `Wercheg` | 韦尔克格 | **`Braila`** | **布勒伊拉** | `(235.04, 125.38)` |
| `31` | `p_town_13` | `Rivacheg` | 里瓦切格 | **`Akkerman`** | **阿克曼（白堡）** | `(324.73, 205.89)` |
| `32` | `p_town_14` | `Halmar` | 哈里麻儿 | **`Edirne`** | **埃迪尔内** | `(194.12, -127.34)` |
| `33` | `p_town_15` | `Yalen` | 亚朗 | **`Zagreb`** | **萨格勒布** | `(-301.38, 118.68)` |
| `34` | `p_town_16` | `Dhirim` | 迪里姆 | **`Szeged`** | **塞格德** | `(-118.65, 164.27)` |
| `35` | `p_town_17` | `Ichamur` | 也察末儿 | **`Sofia`** | **索菲亚** | `(33.86, -80.98)` |
| `36` | `p_town_18` | `Narra` | 那剌 | **`Salonika`** | **萨洛尼卡** | `(39.46, -212.33)` |
| `37` | `p_town_19` | `The_Unknown` | 神秘之地 | **`The_Unknown`** | **厄瑞玻斯冥府之门** | `(45.00, -495.00)` |
| `38` | `p_castle_1` | `Culmarr_Castle` | 屈尔马尔城堡 | **`Bran_Castle`** | **布朗城堡** | `(107.08, 160.96)` |
| `39` | `p_castle_2` | `Malayurg_Castle` | 马拉玉儿哥城堡 | **`Filibe_Castle`** | **菲利贝城堡** | `(110.78, -101.57)` |
| `40` | `p_castle_3` | `Bulugha_Castle` | 布卢加城堡 | **`Hotin_Fortress`** | **霍京要塞** | `(142.51, 342.40)` |
| `41` | `p_castle_4` | `Radoghir_Castle` | 拉多吉尔城堡 | **`Neamt_Citadel`** | **尼亚姆茨要塞** | `(153.39, 238.80)` |
| `42` | `p_castle_5` | `Tehlrog_Castle` | 特赫尔罗格城堡 | **`Poenari_Castle`** | **波耶纳里要塞** | `(63.33, 119.13)` |
| `43` | `p_castle_6` | `Tilbaut_Castle` | 蒂尔包特城堡 | **`Trencsen_Castle`** | **特伦钦城堡** | `(-228.49, 338.57)` |
| `44` | `p_castle_7` | `Sungetche_Castle` | 孙合忒者城堡 | **`Sultaniye_Castle`** | **苏丹尼耶城堡（Kale-i Sultaniye）** | `(212.18, -236.59)` |
| `45` | `p_castle_8` | `Jeirbe_Castle` | 叶伊尔别城堡 | **`Soroca_Castle`** | **索罗卡要塞** | `(227.31, 323.77)` |
| `46` | `p_castle_9` | `Jamiche_Castle` | 雅米什城堡 | **`Hunedoara_Castle`** | **胡内多阿拉城堡** | `(0.71, 142.77)` |
| `47` | `p_castle_10` | `Alburq_Castle` | 阿尔布尔克城堡 | **`Giurgiu_Castle`** | **久尔久要塞** | `(154.41, 23.58)` |
| `48` | `p_castle_11` | `Curin_Castle` | 库林城堡 | **`Severin_Iron_Gates`** | **塞维林铁门要塞** | `(2.74, 62.46)` |
| `49` | `p_castle_12` | `Chalbek_Castle` | 卡尔伯克城堡 | **`Braila_Citadel`** | **布勒伊拉堡垒** | `(231.18, 120.69)` |
| `50` | `p_castle_13` | `Kelredan_Castle` | 克尔勒丹城堡 | **`Jajce_Castle`** | **亚伊采城堡** | `(-235.11, 22.02)` |
| `51` | `p_castle_14` | `Maras_Castle` | 马拉斯城堡 | **`Varad_Oradea`** | **瓦拉德要塞** | `(-47.68, 220.51)` |
| `52` | `p_castle_15` | `Ergellon_Castle` | 厄尔热隆城堡 | **`Brasov_Kronstadt`** | **克隆施塔特要塞** | `(125.51, 157.11)` |
| `53` | `p_castle_16` | `Almerra_Castle` | 阿尔梅拉城堡 | **`Sighisoara_Citadel`** | **塞格斯堡要塞** | `(87.86, 179.22)` |
| `54` | `p_castle_17` | `Distar_Castle` | 底斯塔儿城堡 | **`Bursa_Castle`** | **布尔萨要塞** | `(314.33, -220.91)` |
| `55` | `p_castle_18` | `Ismirala_Castle` | 伊斯米拉拉城堡 | **`Akkerman_Fortress`** | **阿克曼要塞** | `(320.31, 213.50)` |
| `56` | `p_castle_19` | `Yruma_Castle` | 伊鲁马城堡 | **`Chilia_Castle`** | **奇利亚堡垒** | `(286.41, 143.78)` |
| `57` | `p_castle_20` | `Derchios_Castle` | 德尔希奥斯城堡 | **`Siklos_Castle`** | **希克洛什城堡** | `(-198.48, 129.93)` |
| `58` | `p_castle_21` | `Ibdeles_Castle` | 伊布德勒斯城堡 | **`Fagaras_Castle`** | **弗格拉什城堡** | `(93.98, 158.65)` |
| `59` | `p_castle_22` | `Unuzdaq_Castle` | 玉奴即答乞城堡 | **`Larissa_Castle`** | **拉里萨要塞** | `(22.41, -283.19)` |
| `60` | `p_castle_23` | `Tevarin_Castle` | 特瓦林城堡 | **`Mitrovica_Castle`** | **米特罗维察城堡** | `(-134.95, 74.72)` |
| `61` | `p_castle_24` | `Reindi_Castle` | 赖因迪城堡 | **`Kanizsa_Castle`** | **考尼饶要塞** | `(-260.44, 167.16)` |
| `62` | `p_castle_25` | `Ryibelet_Castle` | 里伯勒特城堡 | **`Ozalj_Castle`** | **奥扎利城堡** | `(-322.41, 103.05)` |
| `63` | `p_castle_26` | `Senuzgda_Castle` | 塞努茨格达城堡 | **`Klis_Fortress`** | **克利斯要塞** | `(-266.79, -36.66)` |
| `64` | `p_castle_27` | `Rindyar_Castle` | 林迪阿尔城堡 | **`Knin_Castle`** | **克宁城堡** | `(-281.31, -2.61)` |
| `65` | `p_castle_28` | `Grunwalder_Castle` | 格兰瓦尔德尔城堡 | **`Bistrita_Castle`** | **比斯特里察要塞** | `(69.45, 240.91)` |
| `66` | `p_castle_29` | `Nelag_Castle` | 涅拉格城堡 | **`Senj_Castle`** | **塞尼城堡** | `(-344.46, 58.17)` |
| `67` | `p_castle_30` | `Asugan_Castle` | 阿书敢城堡 | **`Rodoscuk_Castle`** | **罗多斯楚克堡垒** | `(240.61, -172.12)` |
| `68` | `p_castle_31` | `Vyincourd_Castle` | 温科乌尔德城堡 | **`Szabolcs_Castle`** | **萨博尔奇要塞** | `(-66.83, 288.01)` |
| `69` | `p_castle_32` | `Knudarr_Castle` | 克努达尔城堡 | **`Turnu_Magurele_Fortress`** | **图尔努·梅古雷莱要塞** | `(45.00, 36.00)` |
| `70` | `p_castle_33` | `Etrosq_Castle` | 厄特罗斯克城堡 | **`Deva_Citadel`** | **德瓦堡垒** | `(6.33, 148.88)` |
| `71` | `p_castle_34` | `Hrus_Castle` | 赫鲁斯城堡 | **`Craiova_Manor`** | **克拉约瓦堡** | `(55.37, 44.58)` |
| `72` | `p_castle_35` | `Haringoth_Castle` | 哈林戈特城堡 | **`Krusevac_Castle`** | **克鲁舍瓦茨要塞** | `(-46.87, -11.54)` |
| `73` | `p_castle_36` | `Jelbegi_Castle` | 耶尔伯伊城堡 | **`Silistre_Fortress`** | **锡利斯特拉要塞** | `(210.89, 43.51)` |
| `74` | `p_castle_37` | `Dramug_Castle` | 德拉穆格城堡 | **`Gyulafehervar_Alba_Iulia`** | **久洛费黑瓦尔（阿尔巴尤利亚）** | `(34.53, 164.43)` |
| `75` | `p_castle_38` | `Tulbuk_Castle` | 土立八哥城堡 | **`Varna_Castle`** | **瓦尔纳要塞** | `(244.87, -16.89)` |
| `76` | `p_castle_39` | `Slezkh_Castle` | 斯列兹赫城堡 | **`Suceava_Seat_Fortress`** | **苏恰瓦王座要塞** | `(153.54, 283.23)` |
| `77` | `p_castle_40` | `Uhhun_Castle` | 月浑城堡 | **`Athens_Castle`** | **雅典卫城要塞** | `(90.79, -393.54)` |
| `78` | `p_village_1` | `Yaragar` | 亚拉加尔 | **`Nesebar`** | **内塞伯尔** | `(240.20, -55.47)` |
| `79` | `p_village_2` | `Burglen` | 布尔格伦 | **`Campulung`** | **康普隆格** | `(112.32, 103.32)` |
| `80` | `p_village_3` | `Azgad` | 阿茨加德 | **`Pitesti`** | **皮特什蒂** | `(99.69, 85.74)` |
| `81` | `p_village_4` | `Nomar` | 诺马尔 | **`Pozsony`** | **波若尼（布拉迪斯拉发）** | `(-265.30, 283.44)` |
| `82` | `p_village_5` | `Kulum` | 库卢姆 | **`Gumulcine`** | **居米尔吉内（科莫蒂尼）** | `(145.94, -170.21)` |
| `83` | `p_village_6` | `Emirin` | 埃米林 | **`Razgrad`** | **拉兹格勒** | `(181.12, 0.08)` |
| `84` | `p_village_7` | `Amere` | 阿默勒 | **`Szatmar`** | **萨特马尔（萨图马雷）** | `(-6.60, 280.47)` |
| `85` | `p_village_8` | `Haen` | 海恩 | **`Zolyom`** | **兹沃伦** | `(-178.14, 321.19)` |
| `86` | `p_village_9` | `Buvran` | 比夫朗 | **`Ramnicu_Valcea`** | **拉姆尼库沃尔恰** | `(71.76, 96.63)` |
| `87` | `p_village_10` | `Mechin` | 梅钦 | **`Szombathely`** | **松博特海伊** | `(-281.56, 218.90)` |
| `88` | `p_village_11` | `Dusturil` | 笃思图邻 | **`Belgrade`** | **贝尔格莱德郊庄** | `(-104.75, 67.37)` |
| `89` | `p_village_12` | `Emer` | 厄梅尔 | **`Mystras`** | **米斯特拉斯** | `(35.15, -452.95)` |
| `90` | `p_village_13` | `Nemeja` | 内默亚 | **`Kalocsa`** | **考洛乔** | `(-172.37, 179.29)` |
| `91` | `p_village_14` | `Sumbuja` | 孙布亚 | **`Eger`** | **埃格尔** | `(-118.88, 278.85)` |
| `92` | `p_village_15` | `Ryibelet` | 里伯勒特 | **`Izmit`** | **伊兹密特** | `(349.94, -177.69)` |
| `93` | `p_village_16` | `Shapeshte` | 沙佩什捷 | **`Zrin`** | **兹林** | `(-287.22, 79.56)` |
| `94` | `p_village_17` | `Mazen` | 马曾 | **`Bribir`** | **布里比尔** | `(-291.33, -11.11)` |
| `95` | `p_village_18` | `Ulburban` | 乌尔布尔班 | **`Bihac`** | **比哈奇** | `(-300.21, 49.29)` |
| `96` | `p_village_19` | `Hanun` | 哈农 | **`Temesvar`** | **蒂米什瓦拉** | `(-67.65, 134.44)` |
| `97` | `p_village_20` | `Uslum` | 乌斯卢姆 | **`Pecs`** | **佩奇郊庄** | `(-206.21, 150.29)` |
| `98` | `p_village_21` | `Bazeck` | 巴泽茨克 | **`Rupea`** | **鲁佩亚** | `(108.99, 158.04)` |
| `99` | `p_village_22` | `Shulus` | 舒卢斯 | **`Odorhei`** | **奥多海** | `(110.07, 186.63)` |
| `100` | `p_village_23` | `Ilvia` | 伊尔维阿 | **`Targu_Mures`** | **特尔古穆列什** | `(75.72, 200.46)` |
| `101` | `p_village_24` | `Ruldi` | 吕尔迪 | **`Dej`** | **代日** | `(41.82, 239.34)` |
| `102` | `p_village_25` | `Dashbigha` | 答失必哥虎 | **`Gacko`** | **加茨科** | `(-171.55, -54.01)` |
| `103` | `p_village_26` | `Pagundur` | 帕甘迪尔 | **`Kljuc`** | **克柳奇** | `(-253.04, 37.90)` |
| `104` | `p_village_27` | `Glunmar` | 格兰马尔 | **`Prijepolje`** | **普列波列** | `(-133.25, -54.68)` |
| `105` | `p_village_28` | `Tash_Kulun` | 塔失阔栾 | **`Srebrenica`** | **斯雷布雷尼察** | `(-143.40, 12.90)` |
| `106` | `p_village_29` | `Buillin` | 布伊林 | **`Bucharest`** | **布加勒斯特郊庄** | `(147.72, 60.27)` |
| `107` | `p_village_30` | `Ruvar` | 鲁瓦尔 | **`Arges`** | **阿尔杰什** | `(96.44, 95.33)` |
| `108` | `p_village_31` | `Ambean` | 安伯安 | **`Braila`** | **布勒伊拉郊庄** | `(243.63, 130.05)` |
| `109` | `p_village_32` | `Tosdhar` | 托斯德哈尔 | **`Targu_Jiu`** | **特尔古日乌** | `(27.45, 92.28)` |
| `110` | `p_village_33` | `Ruluns` | 鲁伦斯 | **`Jassy`** | **雅西郊庄** | `(210.60, 249.19)` |
| `111` | `p_village_34` | `Ehlerdah` | 埃勒尔达 | **`Chilia`** | **旧基利亚** | `(289.00, 150.34)` |
| `112` | `p_village_35` | `Fearichen` | 费亚里肯 | **`Constanta`** | **康斯坦察港社** | `(271.89, 52.71)` |
| `113` | `p_village_36` | `Jayek` | 亚伊厄克 | **`Kosovo`** | **科索沃波列** | `(-54.56, -80.48)` |
| `114` | `p_village_37` | `Ada_Kulun` | 阿答阔栾 | **`Prilep`** | **普里莱普** | `(-26.66, -168.47)` |
| `115` | `p_village_38` | `Ibiran` | 伊比兰 | **`Lamia`** | **拉米亚** | `(27.34, -334.18)` |
| `116` | `p_village_39` | `Reveran` | 勒弗朗 | **`Kastoria`** | **卡斯托里亚** | `(-34.07, -226.73)` |
| `117` | `p_village_40` | `Saren` | 萨朗 | **`Aydin`** | **艾登** | `(274.73, -386.70)` |
| `118` | `p_village_41` | `Dugan` | 朵干 | **`Gelibolu_Gallipoli`** | **格利博卢（加里波利）** | `(214.53, -220.26)` |
| `119` | `p_village_42` | `Dirigh_Aban` | 底里哈班 | **`Akhisar`** | **阿克希萨尔** | `(267.79, -312.96)` |
| `120` | `p_village_43` | `Zagush` | 咱古失 | **`Usak`** | **乌沙克** | `(339.06, -323.75)` |
| `121` | `p_village_44` | `Peshmi` | 伯失迷 | **`Sisak`** | **锡萨克** | `(-282.12, 98.04)` |
| `122` | `p_village_45` | `Bulugur` | 布鲁兀尔 | **`Slatina`** | **斯拉蒂纳** | `(80.04, 54.24)` |
| `123` | `p_village_46` | `Fedner` | 费德内尔 | **`Slunj`** | **斯卢尼** | `(-315.00, 69.63)` |
| `124` | `p_village_47` | `Epeshe` | 厄珀斯 | **`Varazdin`** | **瓦拉日丁** | `(-288.42, 154.47)` |
| `125` | `p_village_48` | `Veidar` | 韦达尔 | **`Rodoscuk`** | **罗多斯楚克** | `(246.74, -173.84)` |
| `126` | `p_village_49` | `Tismirr` | 铁思密儿 | **`Turda`** | **图尔达** | `(40.83, 199.68)` |
| `127` | `p_village_50` | `Karindi` | 卡林季 | **`Medias`** | **梅迪亚什** | `(68.61, 174.18)` |
| `128` | `p_village_51` | `Jelbegi` | 耶尔伯伊 | **`Bacau`** | **巴克乌** | `(180.03, 211.14)` |
| `129` | `p_village_52` | `Amashke` | 阿马失客 | **`Nis`** | **尼什** | `(-23.05, -31.35)` |
| `130` | `p_village_53` | `Balanli` | 巴兰利 | **`Udbina_Krbava`** | **乌德宾那（克尔巴瓦）** | `(-302.97, 29.64)` |
| `131` | `p_village_54` | `Chide` | 希德 | **`Arad`** | **阿拉德北庄** | `(-66.64, 163.70)` |
| `132` | `p_village_55` | `Tadsamesh` | 塔察梅什 | **`Scutari`** | **斯库台** | `(-115.35, -135.39)` |
| `133` | `p_village_56` | `Fenada` | 费纳达 | **`Tighina`** | **蒂吉纳（本德尔）** | `(292.71, 238.49)` |
| `134` | `p_village_57` | `Ushkuru` | 乌斯库鲁 | **`Roman`** | **罗曼** | `(178.80, 235.35)` |
| `135` | `p_village_58` | `Vezin` | 韦津 | **`Mohacs`** | **摩哈赤集镇** | `(-175.13, 152.43)` |
| `136` | `p_village_59` | `Dumar` | 迪马尔 | **`Szentendre`** | **圣安德烈** | `(-173.16, 263.62)` |
| `137` | `p_village_60` | `Tahlberl` | 塔尔伯尔 | **`Esztergom`** | **埃斯泰尔戈姆** | `(-190.69, 265.29)` |
| `138` | `p_village_61` | `Aldelen` | 阿尔德伦 | **`Visegrad`** | **维谢格拉德** | `(-180.40, 265.44)` |
| `139` | `p_village_62` | `Rebache` | 列巴切 | **`Vac`** | **瓦茨** | `(-171.56, 274.13)` |
| `140` | `p_village_63` | `Rduna` | 勒杜纳 | **`Hatvan`** | **豪特万** | `(-148.16, 260.46)` |
| `141` | `p_village_64` | `Serindiar` | 塞兰迪阿尔 | **`Cegled`** | **采格莱德** | `(-139.79, 226.42)` |
| `142` | `p_village_65` | `Iyindah` | 因达 | **`Szolnok`** | **索尔诺克** | `(-125.21, 233.78)` |
| `143` | `p_village_66` | `Fisdnar` | 菲斯德纳尔 | **`Gyula`** | **久洛** | `(-70.83, 196.00)` |
| `144` | `p_village_67` | `Tebandra` | 捷班德拉 | **`Vaslui`** | **瓦斯卢伊** | `(216.06, 218.97)` |
| `145` | `p_village_68` | `Ibdeles` | 伊布德勒斯 | **`Lugoj`** | **卢戈日** | `(-37.43, 132.07)` |
| `146` | `p_village_69` | `Kwynn` | 克温 | **`Caransebes`** | **卡兰塞贝什** | `(-36.72, 115.99)` |
| `147` | `p_village_70` | `Dirigsene` | 迪里格桑 | **`Orsova`** | **奥尔绍瓦** | `(-9.19, 65.64)` |
| `148` | `p_village_71` | `Tshibtin` | 特希布廷 | **`Kladovo`** | **克拉多沃** | `(3.32, 53.89)` |
| `149` | `p_village_72` | `Elberl` | 埃尔伯尔 | **`Negotin`** | **内戈廷** | `(-0.56, 33.71)` |
| `150` | `p_village_73` | `Chaeza` | 沙厄扎 | **`Vidin`** | **维丁** | `(16.46, 18.45)` |
| `151` | `p_village_74` | `Ayyike` | 艾克 | **`Lom`** | **洛姆** | `(33.06, 8.01)` |
| `152` | `p_village_75` | `Bhulaban` | 布拉班 | **`Oryahovo`** | **奥里亚霍沃** | `(66.51, 4.52)` |
| `153` | `p_village_76` | `Kedelke` | 克德勒哥 | **`Nikopol`** | **尼科波尔集市** | `(107.28, 15.43)` |
| `154` | `p_village_77` | `Rizi` | 里锡 | **`Svishtov`** | **斯维什托夫** | `(128.54, 1.99)` |
| `155` | `p_village_78` | `Sarimish` | 萨里米斯 | **`Ruse`** | **鲁塞** | `(158.45, 15.11)` |
| `156` | `p_village_79` | `Istiniar` | 伊斯蒂尼阿尔 | **`Tutrakan`** | **图特拉坎** | `(182.85, 36.34)` |
| `157` | `p_village_80` | `Vayejeg` | 瓦伊厄约格 | **`Silistra`** | **锡利斯特拉郊庄** | `(218.35, 46.62)` |
| `158` | `p_village_81` | `Odasan` | 奥达桑 | **`Mangalia`** | **曼加利亚** | `(270.96, 27.63)` |
| `159` | `p_village_82` | `Yalibe` | 亚利伯 | **`Botosani`** | **博托沙尼** | `(163.89, 287.04)` |
| `160` | `p_village_83` | `Gisim` | 伊西姆 | **`Babadag`** | **巴巴达格** | `(270.69, 101.93)` |
| `161` | `p_village_84` | `Chelez` | 舍勒兹 | **`Tulcea`** | **图尔恰** | `(272.49, 122.22)` |
| `162` | `p_village_85` | `Ismirala` | 伊斯米拉拉 | **`Ismail`** | **伊兹梅尔** | `(273.24, 134.09)` |
| `163` | `p_village_86` | `Slezkh` | 斯列兹赫 | **`Reni`** | **雷尼** | `(247.73, 138.93)` |
| `164` | `p_village_87` | `Udiniad` | 乌迪尼阿德 | **`Galati`** | **加拉茨** | `(237.62, 136.70)` |
| `165` | `p_village_88` | `Tulbuk` | 土立八哥 | **`Barlad`** | **伯尔拉德** | `(215.88, 190.47)` |
| `166` | `p_village_89` | `Uhhun` | 月浑 | **`Focsani`** | **福克沙尼** | `(197.30, 152.13)` |
| `167` | `p_village_90` | `Jamiche` | 雅米什 | **`Buzau`** | **布泽乌** | `(184.63, 112.89)` |
| `168` | `p_salt_mine` | `Old_Salt_Mine` | 旧盐矿场 | **`Carpathian_Salt_Mine`** | **喀尔巴阡盐矿场** | `(40.80, 199.80)` |
| `169` | `p_four_ways_inn` | `Old_Four_Ways_Inn` | 四方客栈 | **`Balkan_Four_Ways_Inn`** | **巴尔干四方客栈** | `(30.00, 0.00)` |
| `170` | `p_barter_town` | `Barter_Town` | 巴特尔 | **`Barter_Town`** | **巴特尔（以物易物黑市）** | `(30.00, 0.00)` |
| `171` | `p_test_scene` | `test_scene` | 测试场景 | **`test_scene`** | **测试场景** | `(12.15, -70.06)` |
| `172` | `p_battlefields` | `battlefields` | 战场 | **`battlefields`** | **战场** | `(36.64, -32.89)` |
| `173` | `p_dhorak_keep` | `Dhorak_Keep` | 多拉克要塞 | **`Dhorak_Keep`** | **多拉克隐秘要塞** | `(60.00, 180.00)` |
| `174` | `p_training_ground` | `Training_Ground` | 训练场地 | **`Training_Ground`** | **训练场地** | `(-105.00, 84.00)` |
| `175` | `p_training_ground_1` | `Old_Stoning_Field` | 旧石刑场 | **`Old_Stoning_Field`** | **旧石刑场** | `(132.00, 183.00)` |
| `176` | `p_training_ground_2` | `Old_Breaking_Field` | 旧裂刑场 | **`Old_Breaking_Field`** | **旧裂刑场（轮刑场）** | `(-110.33, 243.87)` |
| `177` | `p_training_ground_3` | `Old_Hanging_Field` | 旧吊刑场 | **`Old_Hanging_Field`** | **旧吊刑场（绞刑场）** | `(267.60, 48.00)` |
| `178` | `p_training_ground_4` | `Old_Burning_Field` | 旧火刑场 | **`Old_Burning_Field`** | **旧火刑场** | `(28.50, -241.50)` |
| `179` | `p_training_ground_5` | `Old_Drowning_Field` | 旧水刑场 | **`Old_Drowning_Field`** | **旧水刑场（溺刑水牢）** | `(-104.25, -90.90)` |
| `202` | `p_greenmeteorite` | `Open_Field` | 开放场地 | **`Open_Field`** | **陨星开阔地** | `(45.00, -495.00)` |
| `203` | `p_spiritcircle` | `Standing_Stones` | 上古立石 | **`Dacian_Standing_Stones`** | **达契亚巨石圣地（上古立石）** | `(30.30, 138.60)` |
| `204` | `p_homestead` | `Hiraeth` | 席拉斯 | **`Hiraeth`** | **席拉斯（Hiraeth隐居庄园）** | `(90.00, 240.00)` |
| `205` | `p_sherwood` | `Usherwood` | 厄舍伍德 | **`Pressburg_Woods`** | **普雷斯堡密林** | `(-272.09, 281.73)` |
| `206` | `p_sherwood2` | `Thieves_Den` | 盗贼之巢 | **`Thieves_Den`** | **盗贼之巢** | `(-272.09, 281.73)` |
| `207` | `p_deadantihero` | `The_Fallen_Antihero` | 堕落之地 | **`The_Fallen_Antihero`** | **堕落反英雄之墓** | `(45.00, -495.00)` |
| `208` | `p_ivorytemple` | `Ivory_Temple` | 象牙寺 | **`Ivory_Temple`** | **象牙神殿** | `(60.00, -435.00)` |
