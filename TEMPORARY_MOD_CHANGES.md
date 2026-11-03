# Carpathian Solid & Shade - 暂行视觉修复变动记录 (Temporary Visual Fixes Log)

> [!NOTE]
> 本文档记录的所有模型与特效调整均为**暂行过渡方案（Temporary Transition Solution）**。
> 目的：彻底解决 Linux/OpenGL 渲染环境下，原版多边形外壳因材质缺失（`pureblack.dds`）与后凸尺寸过大（向后凸出 2.17 米）导致的**第三人称镜头完全被死黑球体堵死**的严重视野 Bug。
> 未来一旦设计出更满意的艺术表现方案（如自制半透明着色器、骨骼吸附黑雾特效或重制 3D 模型），可随时根据本文档的原始参数进行无缝恢复与替换。

---

## 一、 变动条目快速对照表

| 物品 ID (`item_id`) | 物品全名 | 原版网格 (`Original Mesh`) | 原版缺陷 | 现暂行网格 (`Temp Mesh`) | 现暂行动态特效 (`Aura FX`) | 涉及角色 / 登场场景 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `itm_necrohelm6` | `Shadowlord's_Aura` | `Necrohelm6` | 头部外凸纯黑球壳，第三人称死黑 | `SWHead` | 头部升腾暗影粒子 (`psys_shadowlord_aura`) | 暗影领主 (`Shadowlord`) |
| `itm_necroarmor6` | `Shadowlord's_Projection` | `Necroarmor6` | 躯干向外膨胀纯黑球壳，贴脸遮挡 | `SWBody` | 躯干周身深渊翻滚粒子力场 | 暗影领主、夜之女神 (`Nyx`) |
| `itm_poehead` | `Poe's_Lore` | `PoeHead` | 头部外凸死黑块 | `SWHead` | 无（贴身暗影形态） | 爱伦坡 (`Poe`) |
| `itm_brollachanhead` | `Brollachan_Head` | `Brollachan` | 向后凸出整整 2.17 米，正对镜头堵死视野 | `SWHead` | 头部升腾暗影粒子 (`psys_shadowlord_aura`) | 无形之怪 (`Brollachan`)、韩塞尔 (`Hansel`)、格蕾特 (`Gretel`)、拉格纳竞技场老板 |
| `itm_tartarushead` | `The_Black_Pit_of_Tartarus` | `Tartarus` | 跨度达 6.33 米的巨型黑坑多边形 | `SWHead` | 头部升腾暗影粒子 (`psys_shadowlord_aura`) | 塔尔塔罗斯领主 (`Tartarus`)、锈蚀怪 (`Rustmonster`) |

---

## 二、 精确代码段对比与一键回退指南

文件路径：[item_kinds1.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20&%20Shade/item_kinds1.txt)

### 1. `itm_necrohelm6` (暗影领主之光环)
- **现行暂行代码**：
```txt
 itm_necrohelm6 Shadowlord's_Aura Shadowlord's_Aura 1  SWHead 0  2684354572 0 142 704643236 0.000000 100 33 0 0 7 0 0 0 0 0 0 0
 0
1
-50.000000  2 1955 3 0 0 15 1965 1 1008806316530991150 
```
- **原版初始代码（若需回退）**：
```txt
 itm_necrohelm6 Shadowlord's_Aura Shadowlord's_Aura 1  Necrohelm6 0  2684354572 0 142 704643236 0.000000 100 33 0 0 7 0 0 0 0 0 0 0
 0
0
```

---

### 2. `itm_necroarmor6` (暗影领主之投影)
- **现行暂行代码**：
```txt
 itm_necroarmor6 Shadowlord's_Projection Shadowlord's_Projection 1  SWBody 0  553648141 0 3680 704643236 0.000000 100 0 56 18 7 0 0 0 0 0 0 0
 0
1
-50.000000  1 1965 1 1008806316530991150 
```
- **原版初始代码（若需回退）**：
```txt
 itm_necroarmor6 Shadowlord's_Projection Shadowlord's_Projection 1  Necroarmor6 0  553648141 0 3680 704643236 0.000000 100 0 56 18 7 0 0 0 0 0 0 0
 0
0
```

---

### 3. `itm_poehead` (爱伦坡之知)
- **现行暂行代码**：
```txt
 itm_poehead Poe's_Lore Poe's_Lore 1  SWHead 0  2684354572 0 568 704643236 0.000000 100 66 0 0 7 0 0 0 0 0 0 0
 0
0
```
- **原版初始代码（若需回退）**：
```txt
 itm_poehead Poe's_Lore Poe's_Lore 1  PoeHead 0  2684354572 0 568 704643236 0.000000 100 66 0 0 7 0 0 0 0 0 0 0
 0
0
```

---

### 4. `itm_brollachanhead` (布罗拉罕无形之首)
- **现行暂行代码**：
```txt
 itm_brollachanhead Brollachan_Head Brollachan_Head 1  SWHead 0  2684354572 0 142 704643236 0.000000 100 44 0 0 7 0 0 0 0 0 0 0
 0
1
-50.000000  2 1955 3 0 0 15 1965 1 1008806316530991150 
```
- **原版初始代码（若需回退）**：
```txt
 itm_brollachanhead Brollachan_Head Brollachan_Head 1  Brollachan 0  2684354572 0 142 704643236 0.000000 100 44 0 0 7 0 0 0 0 0 0 0
 0
0
```

---

### 5. `itm_tartarushead` (塔尔塔罗斯·无底黑渊)
- **现行暂行代码**：
```txt
 itm_tartarushead The_Black_Pit_of_Tartarus The_Black_Pit_of_Tartarus 1  SWHead 0  2684354572 0 1 704643238 55.000000 10 125 0 0 0 0 0 0 0 0 0 0
 0
1
-50.000000  2 1955 3 0 0 15 1965 1 1008806316530991150 
```
- **原版初始代码（若需回退）**：
```txt
 itm_tartarushead The_Black_Pit_of_Tartarus The_Black_Pit_of_Tartarus 1  Tartarus 0  2684354572 0 1 704643238 55.000000 10 125 0 0 0 0 0 0 0 0 0 0
 0
0
```

---

## 三、 自定义粒子系统注册记录

文件路径：[particle_systems.txt](file:///home/wxm/GOG%20Games/Mount%20Blade%20Warband/game/Modules/Carpathian%20Solid%20&%20Shade/particle_systems.txt)
- 总粒子数已由 `46` 递增为 `47`；
- 尾部新增粒子系统索引：`46`（在物品触发器中 64 位编码为 `1008806316530991150`）；
- 定义内容：
```txt
psys_shadowlord_aura 530 prtcl_dust_a  30 1.200000 0.200000 -0.400000 8.000000 0.200000 
0.300000 0.350000   1.000000 0.000000
0.000000 0.040000   1.000000 0.020000
0.000000 0.020000   1.000000 0.010000
0.000000 0.060000   1.000000 0.030000
0.000000 0.350000   1.000000 1.000000
0.350000 0.350000 0.600000   0.000000 0.000000 0.500000   0.200000 
0.200000 0.000000 
```

---

## 四、 未来接入新方案时的操作流程

1. **若制作了新的 3D 模型（如全新半透明气场网格 `MyAuraMesh`）**：
   - 将模型导入 `Resource/solidandshade.brf`；
   - 在 `item_kinds1.txt` 中将 `SWHead` 或 `SWBody` 直接改名为 `MyAuraMesh` 即可；
2. **若制作了全透明/半透明黑雾 Shader**：
   - 可将原版 `Necrohelm6` / `Necroarmor6` 的材质 Shader 切换为支持 Alpha 通道的新 Shader，然后恢复原版 Mesh 名称；
3. **若完全不需要粒子特效，仅要贴身模型**：
   - 将对应物品末尾两行的 `1` 和 `-50.000000 ...` 删改回 `0` 即可。
