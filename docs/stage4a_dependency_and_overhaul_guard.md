# 阶段 4A：S&S 全系统功能依赖总表与 1521 大换皮安全护栏手册

本手册基于对 [`Carpathian Solid & Shade`](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade) 全部编译字节码表（`371` 个脚本、`1,312` 个菜单、`180` 个触发器、`86` 个简单触发器、`conversation.txt`、`mission_templates.txt`）的逐指令扫描构建，作为你接下来**全面替换 1521 聚落场景、五大王国兵种树、武器甲胄、领主与旗帜**期间的静态防呆基准。

---

## 一、全模组静态字节码引用完整性审计结论

通过按战团 `header_common.py` 高位标签（`2=var`, `3=str`, `4=itm`, `5=trp`, `6=fac`, `7=qst`, `8=pt`, `9=p`, `10=scn`, `12=mnu`, `13=script`, `15=spr`）及无标签物品操作码（`500`, `1530`, `1531`, `1535`, `1536`, `1538`, `1543`, `1726`）进行全量交叉核验，当前阶段 1–3 修复后的模组基线状态如下：

| 核心数据表 | 文件链接 | 基线总条目 | S&S 锁定保护数 | 允许 1521 原地换皮槽位 | 越界/断链引用 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **物品表** | [item_kinds1.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/item_kinds1.txt) | `902` (`0..901`) | `743` 锁定 ID | `159` 件零引用原版装备可安全下架；新装备追加至 `>= 902` | **0** |
| **兵种/人物表** | [troops.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/troops.txt) | `850` (`0..849`) | `655` 锁定 ID | `195` 个五国槽位（`64` 士兵 + `5` 国王 + `100` 领主 + `5` 复国者 + `21` 女士）；新兵种追加至 `>= 850` | **0** |
| **队伍模板表** | [party_templates.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/party_templates.txt) | `114` (`0..113`) | `99` 锁定 ID | `15` 个五国增援模板（`93..107`） | **0** |
| **派系表** | [factions.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/factions.txt) | `33` (`0..32`) | `23` 锁定 ID | `10` 个五国文化/国家槽位（`7..11`, `15..19`） | **0** |
| **场景表** | [scenes.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/scenes.txt) | `436` (`0..435`) | `35` 个红名单 `.sco` | 其余 `331` 个五国聚落场景完全自由替换（红名单须用 [sco_sns_tool.py](file:///home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/sco_sns_tool.py) 移植机关） | **0** |
| **任务表 / 全局变量** | [quests.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/quests.txt) / [variables.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/variables.txt) | `41` / `1,298` | 全量锁定 | S&S 实现了 **0 条自定义 `qst_`**，100% 隐藏剧情与仪式状态机由 `variables.txt` 的 `1,298` 个全局变量驱动 | **0** |

---

## 二、1521 大换皮施工安全护栏与槽位白名单

### 2.1 铁律一：严禁插行或删行，新增一律尾部追加
由于没有原始 `.py` 源码，全部字节码通过**整数下标**寻址 `itm_*`、`trp_*`、`pt_*`、`scn_*`。
- **绝对禁止**在 `0..901`（物品）、`0..849`（兵种）、`0..113`（队伍模板）中间删除任何一行或插入新行。
- 新增 1521 历史装备一律追加在 [item_kinds1.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/item_kinds1.txt) 末尾（索引 **`>= 902`**，注意 `901` 是占位符 `itm_end_items`，无任何脚本把它当循环上限，直接往 `902+` 追加并同步累加文件第 2 行总数即可）。
- 新增 1521 历史兵种分支一律追加在 [troops.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/troops.txt) 末尾（索引 **`>= 850`**，同步累加文件第 2 行总数）。

> [!WARNING]
> **重大掩码勘误：`itp_merchandise` 的真实位值是 `0x00010000`（十进制 `65536`），绝不是 `0x01000000`！**
> 在 [item_kinds1.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/item_kinds1.txt) 每件物品首行的 `flags` 字段（位于第 `4 + 2 * 模型数` 个 token，单模型物品为 `toks[6]`）中：
> - 上架售卖：`flags | 65536`（`0x00010000`）
> - 从商店下架隐藏：`flags & ~65536`（不要误改 `0x01000000`，那是其它武器属性位！）

---

### 2.2 [item_kinds1.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/item_kinds1.txt)（`0..901`）精确分区与“商店生命线”清单

#### （A）S&S 原生专属物品区（共 `543` 件 —— 100% 严禁改动）
- `[56..101]`：全部《亡灵之书》神器、魔典、灵应盘、仙石、无限之石、魔宠契约物（`46` 件）
- `[114..141]`、`[147]`、`[156..176]`：尸体、马尸、人体器官（心/肝/脑/眼/骨/皮/血/肉/头/手/足/躯干）、面粉、蜡、粘土、丝绸、蜡烛、木头、水晶、白银、硫酸、甲醛、黄金、钻石、草药、鬼木、万灵油、象牙（`50` 件）
- `[255]`、`[344]`、`[379]`、`[448..786]`、`[788..816]`、`[823..826]`、`[828..829]`、`[832..901]`：全部亡灵肢体/坐骑、焚化/腐烂/抗腐三系变异体、吸血鬼/狼人/猎魔人/发条机械/大巧匠/反英雄/妖精/日本付丧神装备及铲子（`447` 件）

#### （B）S&S 字节码强绑定的原版物品区（必须保留槽位，其中 `64` 件严禁取消商店售卖 `0x00010000`！）
许多看似普通的 Native 商品、马匹和低级农具/护具，实际上是 S&S 仪式的硬编码耗材或触发条件。一旦你在清理原版装备时把它们下架，相关死灵线会直接卡死：

| 保护类别 | 精确索引与物品 ID | 绑定的 S&S 核心机制 | 换皮约束 |
| :--- | :--- | :--- | :--- |
| **1. 基础食物与贸易炼金耗材** | `[102..113]` 熏鱼/风干肉/牛猪鸡肉/面包/苹果/奶酪/蜂蜜/腊肠/圆白菜/黄油；`[142..155]` 葡萄酒/麦芽酒/香料/盐/小麦/面粉(`147`)/铁/油/陶器/亚麻布/毛皮/羊毛/天鹅绒/工具；`[420]` 石头 | 《亡灵之书》炼金（油焚化、盐光荣之手、铁锁链/铁魔像/点金术、香料恶魔/喜来芝、陶器+亚麻布瘟疫炮、羊毛人皮娃娃）、尸妻 12 步防腐、魔宠喂食（面包/葡萄酒）、巴特镇以物易物 | **必须保留 `itp_merchandise (0x10000)`** |
| **2. 全部 7 种原版活马** | `[180..186]` `itm_sumpter_horse`（驮马）.. `itm_charger`（战马） | 扎营屠宰活马产出 `itm_horsecorpse`（死马/瘟疫炮/贪婪魔宠/爱人献祭唯一稳定来源）；`scn_village_35` 海神波塞冬召唤克拉肯硬性消耗 **4 匹骏马 (`[183] itm_courser`)**；炼制万灵油与脏卜 | **必须保留 ID 与 `0x10000` 在售**（可改 1521 马匹贴图/模型，勿删改槽位） |
| **3. 盐矿大巧匠暗门献祭护具** | `[189]` 带倒刺箭、`[197]` 链甲连指手套、`[198]` 鳞甲臂铠、`[202]` 蓝色紧身裤、`[238]` 蓝色软甲、`[273]` 羊毛风帽、`[305]` 棒 (`itm_club`) | `mission_templates.txt` 盐矿 (`scn_salt_mine`) 机关校验与大巧匠前置交互硬编码检查 | **必须保留 `0x10000` 在售** |
| **4. 尸妻解剖刀具与农具/海钓靴/驱魔帽** | `[200]` **绑腿靴 (`itm_wrapping_boots`)**、`[196]` 皮手套、`[201]` 羊毛紧身裤、`[302]` 木杖、`[317]` 镰刀、`[319]` 小刀、`[320]` 屠夫小刀、`[321]` 短剑、`[444]` 黑风帽、`[459]` 铁铲 (`itm_shovel2`) | **`[200]` 绑腿靴是海钓 (`triggers.txt L57..60`) 隐藏加成判定物**；刀具用于尸妻摘眼/剜心/削肉；镰刀用于村庄收割；黑风帽用于驱魔师偷梁换柱；铁铲用于盗墓与换子仪式 | **必须保留 `0x10000` 在售** |
| **5. 战场材质环境检测池（全 35 个战斗模板实时扫描）** | **银器 (`$silverpresent`)**：`[162]` 白银及银制武器；**盐/圣物 (`$saltpresent`)**：`[145]` 盐及盐弹；**铁 (`$ironpresent`)**：`[148]` 铁；**木制武器 (`$woodheld`)**：`[2..13]` 练习武器、`[302, 303, 305]` 木杖/小棍/棒、`[373, 374]` 棍/细棍、`[386]` 木盾、`[424..430]` 猎弓至战弓 | 狼人怕银灼烧、吸血鬼/恶魔怕盐灼烧、妖精/换子怕生铁、德鲁伊/树精木制武器判定 | 切勿把木弓/木棍改成铁器模型或删除槽位 |
| **6. 隐藏彩蛋套装** | `[787]` 珀耳塞福涅神圣外衣、`[817..822]` 奇异武士套装（`trp_bonus_chest_1..3` 及太阳传说引用）、`[827, 830, 831]` 黑暗盔甲三件套（天启/反英雄） | 冥后任务、付丧神/日出传说、反英雄晋升 | **100% 锁定保护** |

> [!TIP]
> **一键净化 1521 商店池（已内置于守卫脚本）**：
> 除上述受保护物品外，原版槽位中共有 **`159` 件中世纪武器/铠甲在全模组字节码中引用数为 `0`**（其中 `109` 件当前开启了商店刷新）。无需用编辑器逐个点选，直接运行：
> ```bash
> python3 "/home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_guard.py" strip-unused-merch --apply
> ```
> 即可自动清除这 `109` 件无引用原版装备的 `0x00010000` 位，既不破坏槽位序号，又能让 1521 城镇商店只刷新历史新装备与 S&S 生命线物资。

---

### 2.3 [troops.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/troops.txt)（`0..849`）精确槽位地图与三大“三明治陷阱”

`troops.txt` 中五国可编辑区与 S&S 亡灵核心区**高度穿插**，批量粘贴或用工具刷领主/国王时务必避开以下三个夹心槽位：

| 索引区间 | 条目数 | 当前身份 | 换皮权限与高危警示 |
| :---: | :---: | :--- | :--- |
| `[0..34]` | `35` | 引擎核心、竞技场、农夫、`[23]` 屠夫、`[25]` 侍祭、`[28]` 训鹰者、雇佣兵 | **锁定**（雇佣兵 `[29..33]` 可微调装备，但切勿碰 `[23, 25, 28]` 及边界 `[34]`） |
| `[35..183]` | `149` | **S&S 全部亡灵兵种、罗宾汉团伙、童话秘境 Boss、冥王、波塞冬、大巧匠、付丧神 (`99..101`)、坟墓之主 (`140`)、第六国士兵 (`168..183`)** | **100% 绝对锁定** |
| **`[184..247]`** | **`64`** | **1521 五大历史王国常规兵种树**（匈牙利 `184..197`、摩尔达维亚 `198..211`、奥斯曼 `212..221`、瓦拉几亚 `222..234`、克罗地亚/特兰西瓦尼亚 `235..247`） | **完全自由原地换皮**！仅需保持 5 国一级新兵槽位（`184, 198, 212, 222, 235`）仍为各国起点；若 64 槽不够用，新分支追加到 `>= 850` 并用 `upgrade1/upgrade2` 连过去 |
| `[248..357]` | `110` | 野怪、教练、**`[283]` 喷血池 (`trp_constable_hareck`)**、拉蒙、炼金术士 (`320`)、塔罗解读者玛尔斯 (`321`)、**全部 34 名 NPC 队友 (`323..356`)** | **100% 绝对锁定**（尤其 `[283]` 原版哈렉警官已被 S&S 改造成喷血池交互实体！） |
| **`[358..362]`** | **`5`** | **1521 五大历史君主**（路易二世、斯特凡四世、苏莱曼大帝、拉杜大公、伊万班） | **可原地改名/改脸/改属性/改常服**，但注意下方的**“天启三君主变异钩子”**！ |
| **`[363]`** | **`1`** | **高危夹心陷阱 #1：`trp_kingdom_6_lord`（万魔之父堤丰）** | **严禁触碰！** 夹在第 5 国君主 (`362`) 与第 1 国领主 (`364`) 正中间！ |
| **`[364..463]`** | **`100`** | **1521 五大历史王国领主**（每国 20 名，`trp_knight_1_1 .. trp_knight_5_20`） | **完全自由原地换皮**（0 条 S&S 剧情硬绑定） |
| **`[464..484]`** | **`21`** | **高危夹心陷阱 #2：`trp_knight_6_1..21`（厄喀德娜、命运三女神、塔耳塔洛斯等 21 位冥府魔神领主）** | **严禁触碰！** 紧接在第 5 国最后一名领主 (`463`) 之后！ |
| **`[485..489]`** | **`5`** | **1521 五大历史王国复国者**（`trp_kingdom_1..5_pretender`） | **完全自由原地换皮** |
| **`[490]`** | **`1`** | **高危夹心陷阱 #3：`trp_kingdom_6_pretender`（黑男爵 Black Baron）** | **严禁触碰！** 夹在第 5 国复国者 (`489`) 与第 1 国贵族女士 (`491`) 正中间！ |
| **`[491..511]`** | **`21`** | **1521 五大历史王国贵族女士** | **完全自由原地换皮**（`[512]` 为 `trp_heroes_end` 边界） |
| `[513..796]` | `284` | 城镇总管、竞技场主、镇长、村长、武器/防具/杂货/马商、街道行人 | 保持槽位不动（商人库存由脚本按文化/商品标志自动刷新） |
| `[797..824]` | `28` | **`trp_zendar_chest` + `trp_bonus_chest_1..27`（全地图 28 个秘境与红名单隐藏宝箱实体）** | **100% 绝对锁定**（内含全部 S&S 神器、配方件与特殊套装） |
| `[825..849]` | `25` | 系统临时数组槽位 | **锁定**；新增 1521 士兵从 **`[850]`** 开始追加 |

> [!IMPORTANT]
> **隐藏机制预警：天启死灵城（Necropolis）与反英雄线的“三君主黑化变异”**
> 在 `menu_necropolis`（将拉蒙头骨按入喷血池唤醒第六国）及 `menu_player_earns_antihero` 中，S&S 脚本会强行向三位历史君主背包塞入魔神装备使其黑化：
> - `[359] trp_kingdom_2_lord`（摩尔达维亚君主）→ 被注入全套 `itm_vampire_*` 化为**吸血鬼大公**
> - `[360] trp_kingdom_3_lord`（奥斯曼苏丹）→ 被注入全套 `itm_black_*` 化为**黑暗反英雄大帝**
> - `[361] trp_kingdom_4_lord`（瓦拉几亚大公）→ 被注入全套 `itm_wolf*` 化为**狼人亲王**
>
> **换皮建议**：你可以完全正常给他们换 1521 历史姓名、脸型、旗帜和历史苏丹/大公铠甲，只需**保留 `tf_hero (0x10)` 标志，且力量（STR）不低于 `15`**，这样平时他们是纯正 1521 历史君主，一旦玩家触发末日天启，又能无缝兼容黑化变身。

---

### 2.4 [party_templates.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/party_templates.txt) 与 [factions.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20%26%20Shade/factions.txt) 换皮边界

- **队伍模板（`0..113`）**：
  - **唯一允许修改的五国增援槽位**：**`pt[93..107]`**（`pt_kingdom_1_reinforcements_a/b/c` 至 `pt_kingdom_5_reinforcements_a/b/c`，共 15 行），当你重做五国兵种树后，把里面的兵种 ID 同步换成你的新五国兵种即可，领主募兵与城镇驻军会自动读取这 15 个模板。
  - **严禁触碰的 S&S 模板**：`pt[5..32]`（潜行猎杀平民与全地形狩猎动物群）、`pt[35..36]`（猎魔人与炼金术士巡逻队）、`pt[41..71]`（冥河海盗、七大邪教阶梯部队、吸血鬼、狼人、冥府大军 `pt_hell`、海怪 `pt_kraken`、梦魇/魅魔/宿敌）、以及末尾的 **`pt[108..113]`（`pt_kingdom_6_reinforcements_a..f` 第六国亡灵六阶增援模板）**！
- **派系表（`0..32`）**：
  - 允许调整名称与外交颜色：`fac_culture_1..5`（`[7..11]`）与 `fac_kingdom_1..5`（`[15..19]`）。
  - **严禁改动**：`fac_culture_6`（`[12]`）、`fac_kingdom_6`（`[20] The_Unknown`）、`fac_kingdoms_end`（`[21]`）及 `[29] fac_undeads`。

---

## 三、Solid & Shade 全系统功能依赖总表

以下总表按 **“入口 → 前置条件与消耗耗材 → 核心状态变量 → 执行载体 → 产出与后果”** 完整收录 S&S 全部核心玩法链路（供后续阶段 4B 逐项实机勾验）。

### 3.1 尸源获取、解剖、盗墓与酷刑场链路

| 子系统 | 触发入口 | 前置条件 / 消耗物品 | 核心状态变量 | 执行菜单 / 触发器 / 场景 | 产出物品 / 后果 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **白昼拾荒腐物** | 扎营 → 行动 / 《亡灵之书》第一卷 | 持有 `itm_book_necronomicon [84]` | `$scavenging`, `$betterscavenge`, `$filthchance` | `menu_camp_action_necronomicon_patchwork` → `triggers.txt L71..73` | 周期产出腐肉、骨骼、内脏；概率遭遇 `trp_filth`（不洁者） |
| **夜间村庄/城镇盗墓** | 午夜潜入城镇/村庄墓地 | 夜间时段 + 背包持有铲子（`itm_shovel2 [459]` 或 `itm_boneshovel [832]`） | `$graverobbing`, `$deathchance`, `$deathitself`, `$medusahead` | `menu_start_graverobbing` → `triggers.txt L74..75` (`p_zendar` 传送坐标结算) | 每次最高产出 `itm_corpse x8`、`itm_soil x9`、`itm_diamonds x2`、`itm_gold`；小概率惊醒守墓人/死神 |
| **人体尸体精细解剖** | 扎营 → 解剖尸体 / 村庄屠宰场 | `itm_corpse [132]`（屠夫出身加成双倍血液/肌肉） | `$background_type` | `menu_camp_action_necronomicon_dismember*` / `menu_village_action_processing*` | 拆解产出：`itm_blood`、`itm_bones`、`itm_flesh`、`itm_skin`、`itm_heart`、`itm_liver`、`itm_brain`、`itm_eyes`、`itm_entrails` 或四肢躯干（`itm_deathhead/body/hands/feet`） |
| **活马屠宰与马尸处理** | 扎营 → 宰杀马匹 / 村庄屠马 | `[180..186]` 任意 7 种原版活马 | `$background_type` | `menu_camp_action_kill_horses` / `menu_village_action_processing_horse*` | 产出 `itm_horsecorpse [133]`（马尸）或 `itm_blood` + `itm_horse_meat [1]` |
| **五大酷刑场采集** | 大地图进入 `p_training_ground_1..5` (`[180..184]`) | 战俘或自由探索 | `$torture*` | `menu_training_ground` + `scn_training_ground_ranged_1..5` | 处决俘虏量产尸体、恐惧面具线索与邪道声望 |
| **海岸捕鱼与捞尸** | 沿海村庄（含阶段 2 重绑的黑海 `Enisala [159]`、爱琴海 `Gelibolu [118]`） | 穿着或持有 `[200] itm_wrapping_boots`（绑腿靴）影响判定 | `$fgathering`, `$izgathering`, `$whaledone`, `$spiritaffinity` | `triggers.txt L57..61` | 产出鲜鱼、`itm_corpse`、`itm_horsecorpse`、`itm_bones`、`itm_pottery`；衔接鲸腹奇遇 |

---

### 3.2 《亡灵之书》全神器与炼金配方矩阵

所有配方均在 `menu_camp_action_necronomicon_make_*` 中执行，前置均需持有 `itm_book_necronomicon [84]`（部分高阶需先造出 `itm_book_philosopherstone [64]` 仙石）：

| 产物 ID 与名称 | 精确消耗材料（含原版商品依赖） | 置位状态变量 | 核心功能与后续链路依赖 |
| :--- | :--- | :--- | :--- |
| `[56] itm_book_ouijaboard`（灵应盘） | `itm_wood [160]` + `itm_soil [168]` + `itm_blood [129]` | `$ouijaboardonce` | **死灵基石**：通灵问卜 (`menu_askouija`)，召唤死灵、死马、恶魔、克雷斯、地狱蠕虫的必需法器 |
| `[59] itm_book_bezoar`（结石护身符） | `itm_liver [124]` + `itm_silver [162]` | `$bezoaramuletonce` | 背包常驻免疫/缓解中毒与疫病；计入战场 `$silverpresent` 银器检定 |
| `[58] itm_book_skindrum`（军团之鼓） | `itm_heart [123]` + `itm_wood [160]` + `itm_skin [131]` | `$legiondrumonce` | 背包统御/士气神器 |
| `[57] itm_book_handofglory`（光荣之手） | `itm_deathhands [137]` + **`itm_salt [145]`** + `itm_candles [159]` | `$handofgloryonce` | 潜行/盗窃加成；计入战场 `$saltpresent` 圣盐检定 |
| `[60] itm_book_evileye`（邪恶之眼） | `itm_crystal [161]` + `itm_eyes [126]` + `itm_candles [159]` | `$evileyeonce` | 侦察/索敌神器；制造小矮人 (`homunculus`)、布罗拉罕及晋升半巫妖 (`demilich` 需 3 颗) 必需品 |
| `[61] itm_book_pandorasbox`（潘朵拉之盒） | `itm_bones [128]` + `itm_gold [165]` + `itm_entrails [127]` | `$pandorasboxonce` | 灾厄释放与高阶仪式法器 |
| `[62] itm_book_chains`（梅菲斯托费勒斯之链） | **`itm_oil [149]`** + `itm_bones [128]` + `itm_heart [123]` + **`itm_iron [148]`** | `$chainsofmephistophelesonce` | 奴役俘虏/恶魔束缚神器 |
| `[63] itm_book_poppet`（人皮娃娃） | `itm_skin [131]` + `itm_brain [125]` + **`itm_wool [153]`** + **`itm_tools [155]`** | `$skinpoppetonce` | 巫毒替身/手术急救加成 |
| `[65] itm_book_artillery`（瘟疫炮） | `itm_horsecorpse [133]` + `itm_sulphur [163]` + **`itm_pottery [150]`** + **`itm_linen [151]`** | `$plaguedartilleryonce` | 攻城/生化范围杀伤神器 |
| `[66] itm_book_shrunkenhead`（缩小之头） | `itm_deathhead [134]` + `itm_formaldehyde [164]` + **`itm_salt [145]`** + `itm_wood [160]` | `$shrunkenheadonce` | 战术通灵加成；计入 `$saltpresent` |
| `[67] itm_book_blackring`（黑指环） | `itm_deathfeet [136]` + **`itm_oil [149]`** + `itm_silver [162]` + **`itm_tools [155]`** | `$blackringonce` | 魅力/暗影伪装加成；计入 `$silverpresent` |
| `[68] itm_book_dummy`（训练模型人） | `itm_deathbody [135]` + **`itm_tools [155]`** + `itm_wood [160]` | `$trainingdummyonce` | 部队每日经验训练神器 |
| **`[64] itm_book_philosopherstone`（仙石）** | `itm_heart [123]` + `itm_brain [125]` + `itm_gold [165]` + `itm_diamonds [166]` | `$philosopherstoneonce` | **炼金终极核心**：解锁焚化/腐烂/抗腐三系亡灵改造、血酒酿造、点铁成金、魔像铸造、半巫妖与死灵魔宠转化 |
| `[115] itm_bonebread`（死者面包） | `itm_bones [128]` + `itm_flour [147]`（面包师出身双倍产出） | `$bonebreadonce` | 高容量不腐军粮 |
| `[117] itm_bloodwine`（血酒） | `itm_blood [129]` + **`itm_wine [142]`**（需持有仙石；装瓶师双倍） | `$bloodwineonce` | 治愈重病魔宠、酒馆黑市高价交易 (`trp_buxworth`)、狂暴饮品 |
| `[165] itm_gold`（炼金点铁成金） | `itm_blood [129]` + **`itm_iron [148]`**（需持有仙石） | `$goldonce` | 无限印钞经济闭环 |
| `[118] itm_mumiyo`（喜来芝） | `itm_flesh [130]` + **`itm_spice [144]`** + `itm_soil [168]` | `$mumiyoonce`, `$mumiyoaddict` | 疗伤圣药；持有心脏+喜来芝满 72 小时触发木乃伊事件 (`triggers.txt L147..148` 赠予 `itm_mummydagger`) |

---

### 3.3 亡灵、恶魔与魔像召唤/进阶矩阵

| 兵种/产物线 | 菜单入口 | 消耗材料与法器要求 | 关联兵种/物品槽位 |
| :--- | :--- | :--- | :--- |
| **基础死灵大军**（死灵 → 亡魂 → 惧妖 → 残魔） | `menu_camp_action_necronomicon_raise_zombie*`（支持 ×1/×5/×10/×20 批量） | `itm_corpse` + 持有 `itm_book_ouijaboard` | `trp_undead1 [80]` → `trp_undead2 [81]` → 惧妖/残魔（`[82..98]` 全锁定） |
| **死马坐骑召唤** | `menu_camp_action_necronomicon_raise_deathhorse` | `itm_horsecorpse [133]` + `itm_book_ouijaboard` | 产出 `[448] itm_deathhorse`（死马） |
| **三系炼金变异改造**（焚化 Burned / 腐烂 Putrid / 抗腐 Preserved） | `menu_camp_action_necronomicon_raise_burned*` / `putrid*` / `preserved*` | 需持有 `itm_book_philosopherstone` + `4` 匹死马；分别消耗 **`itm_oil [149]`**（焚化）、`itm_sulphur [163]`（腐烂）、`itm_formaldehyde [164]`（抗腐） | 改造玩家自身亡灵躯体或批量转化死灵/亡魂/惧妖/残魔及死马坐骑 |
| **恶魔三阶召唤**（恶魔 / 克雷斯 / 地狱蠕虫） | `raise_demon` / `raise_keres` / `raise_hellworm` | `itm_corpse` + `itm_candles` + **`itm_spice [144]`（×1 / ×2 / ×4）** + `itm_book_ouijaboard` | 召唤恶魔系精锐部队（置于 `$demononce`, `$keresonce`, `$hellwormonce`） |
| **银眼造物**（小矮人 Homunculus / 布罗拉罕 Brollachan） | `raise_homunculus` / `raise_brollachan` | `itm_corpse` + **`itm_oil [149]`** + `itm_silver [162]`（×2 / ×4）+ `itm_book_evileye` | 召唤炼金人造人与无形暗影怪 |
| **三大魔像铸造**（粘土 / 钢铁 / 黄金魔像） | `raise_golem` / `raise_irongolem` / `raise_goldgolem` | 粘土魔像：`itm_clay x3` + `itm_corpse` + **`itm_tools`** + 仙石；钢铁魔像：**`itm_iron [148] x9`** + **`itm_oil`** + **`itm_tools`** + 仙石；黄金魔像：`itm_blood x5` + 黄金 + 仙石 | 召唤重装构装体（`$golemspace` 控制编队容量） |

---

### 3.4 玩家晋升、诅咒、尸妻与宠物养成状态机

| 路线名称 | 关键入口与触发点 | 前置条件 / 核心耗材 | 核心全局变量 | 结果与机制影响 |
| :--- | :--- | :--- | :--- | :--- |
| **吸血鬼化与治愈** | 感染战斗 / 喷血池 `dlga_vampire_making_2`；治愈：`menu_player_cures_vampire` | 喷血池直变或装备 `itm_vampire_*` 套装；治愈需特定草药（大蒜 `169` 等，`triggers.txt L51`） | `$infected`, `$solarcure`, `$lunarcure`, `$saltpresent` | 昼夜属性剧变、惧怕圣盐 (`$saltpresent`)；`[359]` 君主在天启线同步共享该套装 |
| **狼人化与治愈** | 狼人战感染 / 喷血池 `dlga_werewolf_making_2`；治愈：`menu_player_cures_werewolf` | 满月周期 (`$moonphase`, `triggers.txt L144` 每 12h 推进)；草药乌头 `itm_aconite [170]` | `$infected`, `$moonphase`, `$silverpresent` | 满月狂化、惧怕白银 (`$silverpresent`)；`[361]` 君主在天启线共享该套装 |
| **巫妖 (Lich) / 半巫妖 (Demilich)** | 冥府入口 `menu_player_enters_underworld_lich` / `_demilich` | 巫妖：手持 `[85] itm_book_infinitystone`（无限之石）直面冥王 `trp_hades [73]`；半巫妖：`itm_book_philosopherstone x3` + `itm_book_evileye x3` + 献祭 3 名战俘 | `$lichdom`, `$hadeschoice`, `$deathitself` | 彻底不死化，改变死亡判定与冥府大军 (`pt_hell`) 敌友关系 |
| **天启死灵城 & 反英雄 (Antihero)** | `menu_necropolis`（喷血池献上 `[83] itm_book_ramunskull` 拉蒙头骨）→ `menu_player_earns_antihero` | 击杀或取得拉蒙头骨并在 `p_bloodfountain_spawn_point [199]` 触发 | `$Necropolis`, `$antihero`, `$warday`, `$pledge` | **第六国 `fac_kingdom_6` 全面苏醒**，`[359, 360, 361]` 三国君主黑化，赐予玩家普罗米修斯之盔与诸神之火 |
| **尸妻系统 (Corpse-Wife)** | `menu_corpsewife1` → `menu_action_corpsewife2_*`（共 12 步器官防腐改造） | 毒杀自愿女奴；12 步分别消耗：木头+铁+羊毛+天鹅绒、直剃刀+银、金+皮手套(`196`)、羊毛袜(`201`)+蓝紧身裤(`202`)、小刀(`319`)+水晶+亚麻布、麦芽酒+面粉+粘土、酒+毛皮+盐、1000 第纳尔+蜡、陶器+钻石、短剑(`321`)+油、屠夫刀(`320`)、丝绸、工具 | `$Corpsewife`, `$Corpsedecay` (`triggers.txt L149` 每 24h 腐烂递增), `$Corpseprogress` | 若未完成对应部位防腐，依次触发 `corpsedecay1..4` 直至化为脓水；12 步圆满达成永恒尸妻与伊斯塔 (`corpsewifeishtar`) 赐福 |
| **恶魔宠物契约 (Familiar)** | `menu_camp_action_necronomicon_make_familiar` → 每 48h `triggers.txt L165` 饥病检定 | 召唤：`itm_horsecorpse` + `itm_candles` + `itm_spice`；日常喂养：`itm_bread [106]`、`itm_blood`、`itm_horsecorpse`、中毒喂 `itm_milk`/`itm_nog`、重病喂 `itm_wine [142]`/`itm_bloodwine` | `$Familiartype`, `$Familiarneeds`, `$Lifepoints`, `$Familiarstasis` | 随机契约蟾蜍/蛇/蜘蛛/鼠/白鸮/黑猫 (`[88..93]`) 提供属性共享；在冥府可用仙石转化为不朽死灵宠 `[95] itm_book_necrotic` |
| **换子/妖精仪式 (Changeling)** | 村庄长老夜间事件 `menu_changeling_ritual` → `_ritual2` | 严格按序使用烧红的铲子 (`shovelburned`) 与铁笼 (`ironcage`)、生铁棒 (`ironbar`) | `$Terrormask`, `$woodengift` | 成功捕获妖精换子 `[94] itm_book_changeling`；顺序错误则仪式损毁 |
| **恐怖面具与玛尔斯驱魔** | 酒馆 `trp_tarot_reader_1 [321]`（解读者玛尔斯）`menu_tarot_exorcism2` | 30,000 第纳尔或持有 `[444] itm_black_hood`（黑风帽）嫁祸转移诅咒 | `$Terrormask`, `$Mopsus`, `$exorcism_chance`, `$loverpossess` | 摘除锁定头部的 `[835] itm_terrormask`；失败可能导致玛尔斯暴毙 |

---

### 3.5 世界秘境、喷血池“黑暗传说”与特殊聚落总表

| 秘境 / 实体 | 大地图锚点 / 场景载体 | 核心交互 NPC | 机制摘要与保护要求 |
| :--- | :--- | :--- | :--- |
| **喷血池 (The Bloodfountain)** | `p_bloodfountain_spawn_point [199]`（与 `p_zendar [18]` 同轴于 `(-192.65, 95.36)`） | `trp_constable_hareck [283]` | 锻造《亡灵之书》、骸骨钥匙、血琴，以及用传奇媒介交换**七大邪教全套神装**（侍祭/亡灵巫师/肉体焚烧者/鼠疫医生/血液防腐者/地狱召唤者/巧匠）与吸血鬼/狼人直变；周期由 `triggers.txt L108..125` 校验传说唯一性 |
| **废弃盐矿与大巧匠** | `p_salt_mine [19]` / `scn_salt_mine` | `trp_greatartificer [119]`、`trp_galatea [126]` | 发条机械学核心、无情猎手 (`trp_npc28`) 招募、万能炼钻药交换、工兵炸药与魔毯支线；依赖蓝色软甲/鳞甲臂铠等原版护具检定 |
| **巴特镇 / 迷宫 / 博物馆** | `p_dhorak_keep [21]` 及子场景 | `trp_barterer [166]`、`trp_drdealgood [165]`、`trp_mamad [164]` | 无货币以物易物黑市、童话迷宫 Boss 群 (`trp[145..163]`)、古物陈列室 |
| **罗宾汉森林秘境** | 阶段 3 已锚定于 `[81] Pozsony` 多瑙河畔 `(-272.09, 281.73)` (`Pressburg_Woods`) | `trp_robin [57]`、`trp_marian [53]` 等 (`[49..60]`) | 绿林劫富与幽灵罗宾双分支 (`menu_robinwin` / `menu_robinrushghost`) |
| **海神波塞冬、克拉肯与鲸腹** | 爱琴海岛村 `[138] Limnos` (`scn_village_35`) + 海战模板 | `trp_poseidon [127]`、`trp_kraken [74]`、`trp_akhadthell [48]` | 献祭 4 匹骏马 (`itm_courser [183]`) 唤醒 `pt_kraken`，战败/吞噬进入 `menu_whalebelly` 决战阿克哈德·瑟尔与冥河海盗 |
| **三大盲搜雷达秘境 + 故园 + 象牙神殿** | 阶段 3 已完成 3 倍雷达半径适配与可通行坐标校准 | 命运三女神 (`trp_knight_6_20`)、尼古拉 (`trp_nikola [124]`)、家庭成员 (`trp[36..46]`) | 大地图靠近自动弹出隐藏菜单；严禁改动 `simple_triggers.txt` 中已校准的坐标与半径常量 |
| **34 座红名单历史聚落** | 详见 [settlement_scene_migration_guide.md](file:///home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/settlement_scene_migration_guide.md) | 宝箱 `trp_bonus_chest_*` 及场景暗门 `spr_Passage` | 替换这 35 个 `.sco` 时必须运行 [`sco_sns_tool.py transplant`](file:///home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/sco_sns_tool.py) 移植机关与出生点 |

---

## 四、自动化换皮守卫工具（`overhaul_guard.py`）使用说明

我已在工作区部署好零依赖静态守卫脚本 [`overhaul_guard.py`](file:///home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_guard.py)，并为你拍下了当前阶段 4A 黄金基线快照 [`overhaul_baseline.json`](file:///home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_baseline.json)。

### 常用命令速查

1. **每次改完一批兵种/装备/领主后，1 秒跑全量安全体检**：
   ```bash
   python3 "/home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_guard.py" check
   ```
   > 自动拦截：表头计数不一致、删行缩水、S&S 锁定槽位错位（含 `trp[363]` 堤丰、`trp[464..484]` 亡灵领主、`trp[490]` 黑男爵、`pt[108..113]` 亡灵增援）、`64` 件商店生命线物资丢失 `0x00010000` 售卖位、兵种升级链越界、以及全模组字节码越界引用。

2. **替换了红名单聚落 `.sco` 地形后，校验 35 个特殊场景机关与暗门**：
   ```bash
   python3 "/home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/sco_sns_tool.py" audit
   ```

3. **查看或一键下架 `109` 件零 S&S 引用的原版中世纪商店装备**：
   ```bash
   # 仅查看完整清单（共 159 件零引用原版物品，其中 109 件当前在售）
   python3 "/home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_guard.py" list-hideable

   # 预览下架效果（不改文件）
   python3 "/home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_guard.py" strip-unused-merch

   # 正式写入磁盘（自动备份 item_kinds1.txt.bak_pre_strip_merch 并复跑 check 体检）
   python3 "/home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_guard.py" strip-unused-merch --apply
   ```

---

## 五、何时启动阶段 4B（最终动态实机验收）？

现在你可以**零顾虑全速推进 1521 历史大换皮**（替换全部聚落 `.sco`、重做五国兵种树、导入 1521 火器/板甲/轻骑装备、重塑 100 名历史领主与 5 大君主）。

全部换皮收工、且 [`overhaul_guard.py check`](file:///home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/overhaul_guard.py) 与 [`sco_sns_tool.py audit`](file:///home/wxm/.gemini/antigravity/brain/bd205a2a-4507-45aa-b018-901a2066a38e/scratch/sco_sns_tool.py) 双双全绿后，告诉我启动 **阶段 4B**：我们将对照本手册第三章的依赖矩阵，执行开新档 Day 1–30 周期刷新压测、海航登岸闭环、代表性死灵仪式走查与存取档稳定性终审。
