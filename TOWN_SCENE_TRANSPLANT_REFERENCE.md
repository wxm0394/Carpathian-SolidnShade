# 《喀尔巴阡：坚韧与阴影》城镇场景移植与替换全景档案 (TOWN SCENE TRANSPLANT REFERENCE)

> **版本**：v1.0 (最终定案版)  
> **归档时间**：2026-11-09  
> **适用模块**：`/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade`  
> **用途**：记录本次针对重点核心城镇进行全场景移植替换的来源 MOD、原始场景对应关系、底层技术参数及后续维护修复 SOP。

---

## 一、 城镇场景移植总览速查表

| 游戏内城镇 (Party ID) | 所属阵营/区域 | 来源模组 (Source MOD) | 来源聚落/场景原型 | 移植子场景数 | 核心特征与室内大厅 Mesh |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **伊斯坦布尔 (Constantinople)**<br>`p_town_10` | 奥斯曼帝国 | **天命 (Destiny)** + **奥斯曼1453** + **Nova Aetas** | 天命君士坦丁堡 + 奥斯曼大巴扎/双清真寺 + 沙瑞兹大清真寺主殿 | 8 | 宏伟双塔清真寺、封闭大巴扎内部四大商人、地毯主殿 (`scn_mosque`) |
| **布勒伊拉 (Braila)**<br>`p_town_12` | 瓦拉几亚大公国 | **World of Vasnar** | 德拉肯海尔庄园 (`p_town_10` Drakenheir Manor) | 8 | 吸血鬼哥特领主大厅 (`vampire_throneroom`)、专属暗黑酒馆 |
| **锡比乌 (Sibiu)**<br>`p_town_3` | 特兰西瓦尼亚 | **World of Vasnar** | 维登斯 (`p_town_4` Videns) | 8 | 北境严寒石砌领主大厅 (`aant_interior_castle_15`)、北境酒馆 |
| **克劳森堡 (Kolozsvar / Klausenburg)**<br>`p_town_5` | 匈牙利/特兰西瓦尼亚 | **World of Vasnar** | 威托尔 (`p_town_7` Wittal / Ebenhof) | 8 | 帝国砖石大殿 (`interior_castle_w_b`)、挂载丘陵远景 (`outer_terrain_steppe_hills`) |
| **苏恰瓦 (Suceava)**<br>`p_town_8` | 摩尔达维亚大公国 | **World of Vasnar** | 索菲亚 (`p_town_34` Sofya) | 8 | 斯拉夫平原大要塞、沙皇寝宫大厅 (`rus_tzar_palaty`) |
| **霍京 (Hotin)**<br>`p_town_11` | 摩尔达维亚大公国 | **World of Vasnar** | 普拉夫 (`p_town_31` Prav) | 8 | 斯拉夫高墙木石要塞、沙皇高顶议事殿 (`oim_interier_rus_zal_a`) |

---

## 二、 城镇子场景详细技术清单与映射

### 1. 伊斯坦布尔 / 君士坦丁堡 (`town_10`)
* **主城街道 (`scn_town_10_center`)**：
  - **基础地形**：天命 (Destiny) 原版 `scn_town_10_center.sco`，包围盒 `(0 0 100 100)`，水高 `-0.50m`。
  - **建筑重构**：
    - 植入奥斯曼大巴扎 `spr_osv2_kapali_carsi` (`damask_rinok_1_a`) 于 `(315.0, 385.0, 3.0)`；
    - 植入宏伟双塔清真寺，双宣礼塔左右严格对称分布于正门两侧：左塔 `(256.88, 432.28, 3.00)`，右塔 `(312.24, 471.22, 3.00)`，建筑偏航角朝向罗马广场中心；
    - 植入皇家次礼拜殿 `spr_osv2_muslim_yapi` 于 `(225.0, 375.0, 3.0)`。
  - **四大商人内室点位 (全部位于大巴扎内部走廊摊位)**：
    - 武器商人 (`Entry 9`)：$(320.13, 384.63, 3.20)$ —— 大巴扎内室东翼铁匠刀剑摊位
    - 防具商人 (`Entry 10`)：$(319.13, 380.85, 3.20)$ —— 大巴扎内室东南锁子甲头盔展位
    - 杂货商人 (`Entry 11`)：$(313.09, 380.81, 3.20)$ —— 大巴扎内室西南货柜摊位
    - 马贩 (`Entry 12`)：$(310.81, 386.91, 3.20)$ —— 大巴扎内室西北宽敞中庭
  - **特殊点位**：`Entry 35` 完整保留于 `(214.49, 221.84, 3.00)`。
* **城堡领主大厅 (`scn_town_10_castle`)**：
  - **来源**：Nova Aetas 沙瑞兹城市的大清真寺内部神殿场景（`scn_mosque.sco`）。
  - **修复**：注入内部地毯正门 `Entry Point 0`（坐标 `(448.44, 444.20, 0.99)`）及领主/侍卫点位，解决原版缺 `Entry 0` 导致出生在原点荒地看外墙的严重缺陷。
* **其他子场景**：
  - 城墙 (`walls`)：天命原版攻城场景；
  - 酒馆 (`tavern`)：`interior_town_house_steppe_d`；
  - 商店 (`store`)：`interior_town_house_steppe_d`；
  - 竞技场 (`arena`)：天命露天竞技场；
  - 地牢 (`prison`)：`interior_prison_o`；
  - 小巷 (`alley`)：天命原版后巷。

---

### 2. 布勒伊拉 (`town_12`)
* **来源原型**：`World of Vasnar` 模组之 `town_10`（德拉肯海尔庄园 Drakenheir Manor）。
* **对应文件与参数**：
  - `scn_town_12_center` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_center.sco` (Flags=256)
  - `scn_town_12_walls` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_walls.sco` (Flags=256)
  - `scn_town_12_castle` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_castle.sco` (Flags=**1**, Mesh=`vampire_throneroom`, BO=`bo_interior_castle_pravar`)
  - `scn_town_12_tavern` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_tavern.sco` (Flags=**1**, Mesh=`interior_tavern_g_vampire`, BO=`bo_interior_tavern_g`)
  - `scn_town_12_store` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_store.sco` (Flags=**1**, Mesh=`interior_town_house_j`)
  - `scn_town_12_arena` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_arena.sco` (Flags=256)
  - `scn_town_12_prison` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_prison.sco` (Flags=**1**, Mesh=`interior_prison_h`)
  - `scn_town_12_alley` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_10_alley.sco` (Flags=256)

---

### 3. 锡比乌 (`town_3`)
* **来源原型**：`World of Vasnar` 模组之 `town_4`（维登斯 Videns）。
* **对应文件与参数**：
  - `scn_town_3_center` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_center.sco` (Flags=256, 尺寸 527 KB)
  - `scn_town_3_walls` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_walls.sco` (Flags=256)
  - `scn_town_3_castle` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_castle.sco` (Flags=**1**, Mesh=`aant_interior_castle_15`, BO=`bo_aant_interior_castle_15`)
  - `scn_town_3_tavern` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_tavern.sco` (Flags=**1**, Mesh=`aant_interior_tavern_2`, BO=`bo_aant_interior_tavern_2`)
  - `scn_town_3_store` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_store.sco` (Flags=**1**, Mesh=`interior_house_b`)
  - `scn_town_3_arena` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_arena.sco` (Flags=256)
  - `scn_town_3_prison` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_prison.sco` (Flags=**1**, Mesh=`interior_prison_h`)
  - `scn_town_3_alley` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_4_alley.sco` (Flags=256)

---

### 4. 克劳森堡 (`town_5`)
* **来源原型**：`World of Vasnar` 模组之 `town_7`（威托尔 Wittal / Ebenhof）。
* **对应文件与参数**：
  - `scn_town_5_center` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_center.sco` (Flags=256, 远景=`outer_terrain_steppe_hills`)
  - `scn_town_5_walls` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_walls.sco` (Flags=256, 远景=`outer_terrain_steppe_hills`)
  - `scn_town_5_castle` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_castle.sco` (Flags=**1**, Mesh=`interior_castle_w_b`, BO=`bo_interior_castle_w`)
  - `scn_town_5_tavern` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_tavern.sco` (Flags=**1**, Mesh=`interior_tavern_b_empire`, BO=`bo_interior_tavern_b`)
  - `scn_town_5_store` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_store.sco` (Flags=**1**, Mesh=`interior_town_house_j`)
  - `scn_town_5_arena` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_arena.sco` (Flags=256, 远景=`outer_terrain_steppe_mountains`)
  - `scn_town_5_prison` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_prison.sco` (Flags=**1**, Mesh=`interior_prison_h`)
  - `scn_town_5_alley` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_7_alley.sco` (Flags=256, 远景=`outer_terrain_plain`)

---

### 5. 苏恰瓦 (`town_8`)
* **来源原型**：`World of Vasnar` 模组之 `town_34`（索菲亚 Sofya）。
* **对应文件与参数**：
  - `scn_town_8_center` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_center.sco` (Flags=256, 尺寸 516 KB)
  - `scn_town_8_walls` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_walls.sco` (Flags=256)
  - `scn_town_8_castle` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_castle.sco` (Flags=**1**, Mesh=`rus_tzar_palaty`, BO=`bo_rus_tzar_palaty`)
  - `scn_town_8_tavern` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_tavern.sco` (Flags=**1**, Mesh=`oim_interier_rus_taverna`, BO=`bo_oim_interier_rus_taverna`)
  - `scn_town_8_store` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_store.sco` (Flags=**1**, Mesh=`interior_tavern_a`)
  - `scn_town_8_arena` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_arena.sco` (Flags=256)
  - `scn_town_8_prison` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_prison.sco` (Flags=**1**, Mesh=`interior_prison_j`)
  - `scn_town_8_alley` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_34_alley.sco` (Flags=256)

---

### 6. 霍京 (`town_11`)
* **来源原型**：`World of Vasnar` 模组之 `town_31`（普拉夫 Prav）。
* **对应文件与参数**：
  - `scn_town_11_center` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_center.sco` (Flags=256, 尺寸 297 KB，与苏恰瓦完全不同)
  - `scn_town_11_walls` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_walls.sco` (Flags=256, 尺寸 315 KB)
  - `scn_town_11_castle` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_castle.sco` (Flags=**1**, Mesh=`oim_interier_rus_zal_a`, BO=`bo_oim_interier_rus_zal_a`)
  - `scn_town_11_tavern` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_tavern.sco` (Flags=**1**, Mesh=`oim_interier_rus_taverna`)
  - `scn_town_11_store` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_store.sco` (Flags=**1**, Mesh=`interior_tavern_a`)
  - `scn_town_11_arena` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_arena.sco` (Flags=256)
  - `scn_town_11_prison` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_prison.sco` (Flags=**1**, Mesh=`interior_prison_j`)
  - `scn_town_11_alley` $\leftarrow$ `World of Vasnar/SceneObj/scn_town_31_alley.sco` (Flags=256)

---

## 三、 核心技术避坑与修复要点 (SOP)

### 1. 室内场景 Flags 严格规约为 `1`
- **问题现象**：进门后没有地板、墙壁和天花板，桌椅、领主王座悬挂在万丈虚空，角色踩在空气墙上或掉下深渊。
- **根因**：`scenes.txt` 中第 3 列 Flags 被误标为 `256`（室外地形标志）。战团引擎在检测到 `flags=256` 时会强行作为室外场景初始化，忽略室内 mesh 外壳渲染。
- **规范**：所有封闭室内场景（`castle`, `tavern`, `store`, `prison`）第 3 列必须严格为 **`1`** (`sf_indoors`)。

### 2. 远景网格 (Outer Terrain) 缺失与修补
- **问题现象**：城镇或竞技场四周地平线空旷无山脉，或者远景缺失。
- **根因**：场景定义第 4 行指定的远景网格（如 `outer_terrain_steppe_hills` 和 `outer_terrain_steppe_mountains`）未在 CSNS 本地 BRF 中注册。
- **修补方案**：
  - 从 `World of Vasnar/Resource/` 拷贝 `panorames_bons.brf` 与 `manitas.brf` 到 CSNS 的 `Resource/`；
  - 在 `module.ini` 中加入：
    ```ini
    load_mod_resource = manitas
    load_mod_resource = panorames_bons
    ```
  - 远景贴图 `op_steppe_far.dds`、`steppemountainsfar.dds` 确保位于 `Textures/` 目录。

### 3. 地表平整与纹理通道重定向 (`ground_specs.txt`)
- **问题现象**：地表翘起 30 度斜坡，或者出现大面积纯白雪地撕裂、空气墙卡死。
- **根因**：天命原版场景依赖其特定地表种子代码 `0x0000000130038980...` 与包围盒 `(0 0 100 100)`。若误塞入其他模组的丘陵种子，地表直接变形撕裂。
- **解决方案**：在 `Data/ground_specs.txt` 中将雪地材质通道重定向至 S&S 专属怪异龟裂土地贴图 `ground_earth`，在保持天命平整地表网格的同时呈现原汁原味的 S&S 地表氛围。

### 4. 室内场景 Entry Point 0 缺失导致原点面壁
- **问题现象**：进入城堡或宫殿后，角色被抛在建筑外墙外几十米甚至几百米处面壁。
- **根因**：部分源场景（如 Nova Aetas 的 `scn_mosque.sco`）原版仅通过脚本跳转 `Entry 2`，内部没有定义 `Entry 0`。常规机制或场景查看器进入时寻找 `Entry 0` 失败，默认丢到原点 `(0, 0, 0)`。
- **解决方案**：向 `.sco` 文件中直接注入重合于正门地毯位置的 `Entry Point 0`。

---

## 四、 增量冷备快照归档
在每次关键替换操作前均执行了完整的冷备份，可供随时回滚：
1. `backup_pre_town_migration_1794235856/`：5 城镇迁移前原始数据（scenes.txt + 40 个旧 sco）
2. `backup_pre_hotin_swap_1794237481/`：霍京迁移与锡比乌/克劳森堡互换前数据
