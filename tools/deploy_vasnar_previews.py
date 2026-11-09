#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade (1521)
在场景查看器中增加【World of Vasnar 城镇场景预展子类】
预展城镇:
1. 德拉肯海尔庄园 (Drakenheir Manor) <- Vasnar town_10
2. 维登斯 (Videns)                   <- Vasnar town_4
3. 埃本霍夫 (Ebenhof)                 <- Vasnar town_23
4. 索菲亚 (Sofya)                    <- Vasnar town_34
包含全部 8 个子场景: center, walls, castle, tavern, store, arena, prison, alley
绝对不改动游戏本体已有的 18 座历史城镇场景与配置！
"""

import os
import sys
import shutil

CARPATHIAN_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
VASNAR_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/World of Vasnar"

TOWNS_CONFIG = [
    {
        "key": "drakenheir",
        "name_en": "Drakenheir_Manor",
        "name_cn": "德拉肯海尔庄园",
        "vn_tid": 10
    },
    {
        "key": "videns",
        "name_en": "Videns",
        "name_cn": "维登斯",
        "vn_tid": 4
    },
    {
        "key": "ebenhof",
        "name_en": "Ebenhof",
        "name_cn": "埃本霍夫",
        "vn_tid": 23
    },
    {
        "key": "sofya",
        "name_en": "Sofya",
        "name_cn": "索菲亚",
        "vn_tid": 34
    }
]

SUB_CONFIG = [
    ("center", "Center_Square_(Town_Center)", "1. 城镇街道中心 (Center)"),
    ("walls",  "Siege_Walls_(Walls)",         "2. 城墙攻城防守 (Walls)"),
    ("castle", "Castle_Lord_Hall_(Castle)",   "3. 城堡大厅与王座 (Castle)"),
    ("tavern", "Tavern_(Tavern)",             "4. 酒馆 (Tavern)"),
    ("store",  "Merchant_Store_(Store)",      "5. 杂货商铺 (Store)"),
    ("arena",  "Arena_Grounds_(Arena)",       "6. 竞技场 (Arena)"),
    ("prison", "Dungeon_Prison_(Prison)",     "7. 地牢监狱 (Prison)"),
    ("alley",  "Dark_Alley_(Alley)",          "8. 阴暗小巷 (Alley)")
]

OPMASK_SCENE = 0x0a00000000000000
OPMASK_MENU  = 0x0c00000000000000


def step1_patch_scene_props():
    print("=== Step 1: 补齐缺失的 spr_espectador1 ===")
    sp_path = os.path.join(CARPATHIAN_DIR, "scene_props.txt")
    lines = open(sp_path, "r", encoding="latin1").read().splitlines()
    props = {l.split()[0] for l in lines if l.startswith("spr_")}
    if "spr_espectador1" not in props:
        lines.append("spr_espectador1 0 0 espectador1 0 0")
        lines[1] = f" {len(props) + 1}"
        with open(sp_path, "w", encoding="latin1") as f:
            f.write("\n".join(lines) + "\n")
        print("  成功追加 spr_espectador1，总计数更新为", lines[1].strip())
    else:
        print("  spr_espectador1 已存在，跳过")


def step2_copy_scos():
    print("\n=== Step 2: 复制 32 个预展 .sco 场景文件 ===")
    dst_dir = os.path.join(CARPATHIAN_DIR, "SceneObj")
    src_dir = os.path.join(VASNAR_DIR, "SceneObj")

    copied = 0
    for t in TOWNS_CONFIG:
        for sub, _, _ in SUB_CONFIG:
            src_name = f"scn_town_{t['vn_tid']}_{sub}.sco"
            dst_name = f"scn_preview_{t['key']}_{sub}.sco"
            src_path = os.path.join(src_dir, src_name)
            dst_path = os.path.join(dst_dir, dst_name)
            shutil.copy2(src_path, dst_path)
            copied += 1
    print(f"  已成功复制 {copied} 个场景文件至 SceneObj/")


def step3_register_scenes():
    print("\n=== Step 3: 在 scenes.txt 中注册 32 个预展场景 ===")
    scenes_path = os.path.join(CARPATHIAN_DIR, "scenes.txt")
    csns_lines = open(scenes_path, "r", encoding="latin1").read().splitlines()
    
    vn_scenes_path = os.path.join(VASNAR_DIR, "scenes.txt")
    vn_lines = open(vn_scenes_path, "r", encoding="latin1").read().splitlines()

    # 读取 Vasnar 场景块
    vn_blocks = {}
    i = 2
    while i < len(vn_lines):
        if vn_lines[i].startswith("scn_"):
            sname = vn_lines[i].split()[0]
            vn_blocks[sname] = vn_lines[i:i+4]
            i += 4
        else:
            i += 1

    # 检查是否已注册过
    existing_scenes = set()
    i = 2
    while i < len(csns_lines):
        if csns_lines[i].startswith("scn_"):
            existing_scenes.add(csns_lines[i].split()[0])
            i += 4
        else:
            i += 1

    added_blocks = []
    for t in TOWNS_CONFIG:
        for sub, _, _ in SUB_CONFIG:
            new_sname = f"scn_preview_{t['key']}_{sub}"
            if new_sname in existing_scenes:
                continue
            src_sname = f"scn_town_{t['vn_tid']}_{sub}"
            src_block = list(vn_blocks[src_sname])

            # Line 0: 将名字改为 new_sname, tag 改为 preview_xxx
            toks = src_block[0].split()
            toks[0] = new_sname
            toks[1] = f"preview_{t['key']}_{sub}"
            # 保持 S&S 的标准 flags=256
            toks[2] = "256"
            src_block[0] = " ".join(toks)

            # Line 3: outer_terrain
            # 室外场景统一使用 outer_terrain_plain 避免模型丢失或悬崖
            if sub in ["center", "walls", "arena", "alley"]:
                src_block[3] = " outer_terrain_plain "
            else:
                src_block[3] = " 0 "

            added_blocks.extend(src_block)

    if added_blocks:
        total_scenes = int(csns_lines[1].strip()) + (len(added_blocks) // 4)
        csns_lines[1] = f" {total_scenes}"
        csns_lines.extend(added_blocks)
        with open(scenes_path, "w", encoding="latin1") as f:
            f.write("\n".join(csns_lines) + "\n")
        print(f"  成功追加 {len(added_blocks)//4} 个新场景，scenes.txt 总场景数更新为 {total_scenes}")
    else:
        print("  场景已全部在 scenes.txt 中注册，跳过")


def step4_patch_menus():
    print("\n=== Step 4: 在 menus.txt 中挂载预展菜单与选项 ===")
    menus_path = os.path.join(CARPATHIAN_DIR, "menus.txt")
    lines = open(menus_path, "r", encoding="latin1").read().splitlines()

    # 1. 查找 scenes.txt 中 32 个场景的下标 (0-based)
    scenes_path = os.path.join(CARPATHIAN_DIR, "scenes.txt")
    sc_lines = open(scenes_path, "r", encoding="latin1").read().splitlines()
    scene_indices = {}
    sc_idx = 0
    for i in range(2, len(sc_lines)):
        if sc_lines[i].startswith("scn_"):
            sname = sc_lines[i].split()[0]
            scene_indices[sname] = sc_idx
            sc_idx += 1

    # 2. 统计当前 menu_ 列表与索引
    menu_positions = []
    for i, l in enumerate(lines):
        if l.startswith("menu_"):
            menu_positions.append((i, l.split()[0]))
    current_menu_count = len(menu_positions)
    print(f"  当前总菜单数: {current_menu_count}")

    # 查找 menu_scene_viewer 的位置与 menu_id
    sv_idx = -1
    sv_line_num = -1
    for m_idx, (l_num, m_name) in enumerate(menu_positions):
        if m_name == "menu_scene_viewer":
            sv_idx = m_idx
            sv_line_num = l_num
            break
    print(f"  menu_scene_viewer ID={sv_idx}, 所在行={sv_line_num}")
    sv_menu_opmask = OPMASK_MENU | sv_idx

    # 定义 5 个新菜单 ID
    preview_hub_id   = current_menu_count
    dh_menu_id       = current_menu_count + 1
    videns_menu_id   = current_menu_count + 2
    ebenhof_menu_id  = current_menu_count + 3
    sofya_menu_id    = current_menu_count + 4

    # 3. 检查是否已经追加过 menu_sv_vasnar_preview
    if any(m[1] == "menu_sv_vasnar_preview" for m in menu_positions):
        print("  menu_sv_vasnar_preview 已存在，跳过重复追加")
        return

    # 4. 修改 menu_scene_viewer 增加预展入口
    # 查看 menu_scene_viewer 标题行:
    # menu_scene_viewer 0 ... none 0 10
    sv_header_tokens = lines[sv_line_num].split()
    old_opt_count = int(sv_header_tokens[-1])
    sv_header_tokens[-1] = str(old_opt_count + 1)
    lines[sv_line_num] = " ".join(sv_header_tokens)

    # 在 mno_sv_to_reports 之前插入 mno_sv_to_vasnar_preview
    insert_line = sv_line_num + 1
    while insert_line < len(lines):
        if lines[insert_line].strip().startswith("mno_sv_to_reports"):
            break
        insert_line += 1

    vp_hub_opmask = OPMASK_MENU | preview_hub_id
    opt_line = f" mno_sv_to_vasnar_preview  0  9._[World_of_Vasnar]_Town_Scenes_Preview_(4_Cities)...  1 2060 1 {vp_hub_opmask}  . "
    lines.insert(insert_line, opt_line)
    print(f"  已在 menu_scene_viewer 插入预展入口选项 (选项总数由 {old_opt_count} -> {old_opt_count + 1})")

    # 5. 构建 5 个新菜单代码块 (纯 ASCII 英文，中文在 game_menus.csv)
    new_menu_lines = []

    # 菜单 1: 预展总入口 menu_sv_vasnar_preview
    new_menu_lines.append(f"menu_sv_vasnar_preview 0 World_of_Vasnar_Town_Scenes_Preview:_Select_a_candidate_city_to_inspect_sub-scenes._(Press_TAB_to_return) none 0 5")
    new_menu_lines.append(f" mno_sv_vp_back  0  [Back_to_Scene_Viewer_Hub]  1 2060 1 {sv_menu_opmask}  . ")
    new_menu_lines.append(f" mno_sv_vp_dh    0  1._Drakenheir_Manor_(8_Sub-Scenes)...  1 2060 1 {OPMASK_MENU | dh_menu_id}  . ")
    new_menu_lines.append(f" mno_sv_vp_vi    0  2._Videns_(8_Sub-Scenes)...  1 2060 1 {OPMASK_MENU | videns_menu_id}  . ")
    new_menu_lines.append(f" mno_sv_vp_eb    0  3._Ebenhof_(8_Sub-Scenes)...  1 2060 1 {OPMASK_MENU | ebenhof_menu_id}  . ")
    new_menu_lines.append(f" mno_sv_vp_so    0  4._Sofya_(8_Sub-Scenes)...  1 2060 1 {OPMASK_MENU | sofya_menu_id}  . ")

    # 菜单 2~5: 4 座城市的子场景详情菜单
    town_menu_map = [
        (dh_menu_id,      TOWNS_CONFIG[0]),
        (videns_menu_id,  TOWNS_CONFIG[1]),
        (ebenhof_menu_id, TOWNS_CONFIG[2]),
        (sofya_menu_id,   TOWNS_CONFIG[3]),
    ]

    for this_mid, t in town_menu_map:
        this_menu_opmask = OPMASK_MENU | this_mid
        new_menu_lines.append(f"menu_sv_vp_{t['key']} 0 {t['name_en']}_(World_of_Vasnar):_Select_a_sub-scene_to_enter._(Press_TAB_to_return) none 0 9")
        new_menu_lines.append(f" mno_sv_vp_{t['key']}_back  0  [Back_to_Vasnar_Preview_Menu]  1 2060 1 {vp_hub_opmask}  . ")

        for sub, sub_en, sub_cn in SUB_CONFIG:
            sname = f"scn_preview_{t['key']}_{sub}"
            scn_idx = scene_indices[sname]
            scn_opmask = OPMASK_SCENE | scn_idx
            # 字节码:
            # 1304 1 <this_menu_opmask> (set_back_menu)
            # 1911 1 0                  (set_jump_entry)
            # 1910 1 <scn_opmask>       (jump_to_scene)
            # 2048 0                    (change_screen_mission)
            opt_str = f" mno_sv_vp_{t['key']}_{sub}  0  {sub_en}  4 1304 1 {this_menu_opmask} 1911 1 0 1910 1 {scn_opmask} 2048 0  . "
            new_menu_lines.append(opt_str)

    # 6. 更新 menus.txt 总数并写入
    lines.extend(new_menu_lines)
    lines[1] = f" {current_menu_count + 5}"

    with open(menus_path, "w", encoding="latin1") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  成功追加 5 个新菜单，menus.txt 总菜单数更新为 {current_menu_count + 5}")


def step5_patch_chinese_translation():
    print("\n=== Step 5: 添加中文本地化翻译 (languages/cns/game_menus.csv) ===")
    csv_path = os.path.join(CARPATHIAN_DIR, "languages/cns/game_menus.csv")
    if not os.path.exists(csv_path):
        print("  未找到 game_menus.csv，跳过")
        return

    csv_lines = open(csv_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    existing_keys = {l.split("|")[0] for l in csv_lines if "|" in l}

    new_trans = [
        ("mno_sv_to_vasnar_preview", "9.【瓦斯那世界】4座候选城镇场景实机预展 (包含全部子场景)..."),
        ("menu_sv_vasnar_preview", "瓦斯那世界城镇场景实机预展：请选择你想实地漫游核查的城镇。场景内按 TAB 随时原路返回。"),
        ("mno_sv_vp_back", "【返回场景查看器大厅】"),
        ("mno_sv_vp_dh", "1. 德拉肯海尔庄园 (Drakenheir Manor - 8个子场景)..."),
        ("mno_sv_vp_vi", "2. 维登斯 (Videns - 8个子场景)..."),
        ("mno_sv_vp_eb", "3. 埃本霍夫 (Ebenhof - 8个子场景)..."),
        ("mno_sv_vp_so", "4. 索菲亚 (Sofya - 8个子场景)..."),
        ("menu_sv_vp_drakenheir", "德拉肯海尔庄园 (Drakenheir Manor)：请选择你想进入的子场景。在场景中按 TAB 随时返回。"),
        ("mno_sv_vp_drakenheir_back", "【返回瓦斯那城镇预展菜单】"),
        ("mno_sv_vp_drakenheir_center", "1. 城镇街道中心 (Center)"),
        ("mno_sv_vp_drakenheir_walls", "2. 城墙攻城防守 (Walls)"),
        ("mno_sv_vp_drakenheir_castle", "3. 领主大厅与王座 (Castle)"),
        ("mno_sv_vp_drakenheir_tavern", "4. 酒馆 (Tavern)"),
        ("mno_sv_vp_drakenheir_store", "5. 杂货商铺 (Store)"),
        ("mno_sv_vp_drakenheir_arena", "6. 竞技场 (Arena)"),
        ("mno_sv_vp_drakenheir_prison", "7. 地牢监狱 (Prison)"),
        ("mno_sv_vp_drakenheir_alley", "8. 阴暗小巷 (Alley)"),
        ("menu_sv_vp_videns", "维登斯 (Videns)：请选择你想进入的子场景。在场景中按 TAB 随时返回。"),
        ("mno_sv_vp_videns_back", "【返回瓦斯那城镇预展菜单】"),
        ("mno_sv_vp_videns_center", "1. 城镇街道中心 (Center)"),
        ("mno_sv_vp_videns_walls", "2. 城墙攻城防守 (Walls)"),
        ("mno_sv_vp_videns_castle", "3. 领主大厅与王座 (Castle)"),
        ("mno_sv_vp_videns_tavern", "4. 酒馆 (Tavern)"),
        ("mno_sv_vp_videns_store", "5. 杂货商铺 (Store)"),
        ("mno_sv_vp_videns_arena", "6. 竞技场 (Arena)"),
        ("mno_sv_vp_videns_prison", "7. 地牢监狱 (Prison)"),
        ("mno_sv_vp_videns_alley", "8. 阴暗小巷 (Alley)"),
        ("menu_sv_vp_ebenhof", "埃本霍夫 (Ebenhof)：请选择你想进入的子场景。在场景中按 TAB 随时返回。"),
        ("mno_sv_vp_ebenhof_back", "【返回瓦斯那城镇预展菜单】"),
        ("mno_sv_vp_ebenhof_center", "1. 城镇街道中心 (Center)"),
        ("mno_sv_vp_ebenhof_walls", "2. 城墙攻城防守 (Walls)"),
        ("mno_sv_vp_ebenhof_castle", "3. 领主大厅与王座 (Castle)"),
        ("mno_sv_vp_ebenhof_tavern", "4. 酒馆 (Tavern)"),
        ("mno_sv_vp_ebenhof_store", "5. 杂货商铺 (Store)"),
        ("mno_sv_vp_ebenhof_arena", "6. 竞技场 (Arena)"),
        ("mno_sv_vp_ebenhof_prison", "7. 地牢监狱 (Prison)"),
        ("mno_sv_vp_ebenhof_alley", "8. 阴暗小巷 (Alley)"),
        ("menu_sv_vp_sofya", "索菲亚 (Sofya)：请选择你想进入的子场景。在场景中按 TAB 随时返回。"),
        ("mno_sv_vp_sofya_back", "【返回瓦斯那城镇预展菜单】"),
        ("mno_sv_vp_sofya_center", "1. 城镇街道中心 (Center)"),
        ("mno_sv_vp_sofya_walls", "2. 城墙攻城防守 (Walls)"),
        ("mno_sv_vp_sofya_castle", "3. 领主大厅与王座 (Castle)"),
        ("mno_sv_vp_sofya_tavern", "4. 酒馆 (Tavern)"),
        ("mno_sv_vp_sofya_store", "5. 杂货商铺 (Store)"),
        ("mno_sv_vp_sofya_arena", "6. 竞技场 (Arena)"),
        ("mno_sv_vp_sofya_prison", "7. 地牢监狱 (Prison)"),
        ("mno_sv_vp_sofya_alley", "8. 阴暗小巷 (Alley)")
    ]

    added = 0
    for k, v in new_trans:
        if k not in existing_keys:
            csv_lines.append(f"{k}|{v}")
            added += 1

    if added:
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("\n".join(csv_lines) + "\n")
        print(f"  已追加 {added} 条中文汉化文本至 game_menus.csv")
    else:
        print("  中文翻译已存在，跳过")


if __name__ == "__main__":
    step1_patch_scene_props()
    step2_copy_scos()
    step3_register_scenes()
    step4_patch_menus()
    step5_patch_chinese_translation()
    print("\n>>> [全部完成] 瓦斯那 4 城镇全套 32 子场景预展已成功挂载至场景查看器！<<<")
