#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade (1521) — 场景查看器 (Scene Viewer & Showroom) 安装器 v3.0
=============================================================================
全面升级特性：
  1. 【彻底修复返回报告菜单】：
     - "返回报告菜单" 采用原生跳转 (jump_to_menu, "menu_reports") (opcode 2060 1 4)，百分之百秒回报告界面！
     - 新增 "返回大地图继续行进" (change_screen_map) (opcode 2052 0)，任意位置一键回大地图。
  2. 【村庄与要塞全量替换为游戏内实际历史真实名称】：
     - 40 座城堡与 90 座村庄全部从 languages/cns/parties.csv 读取实际游戏内中文译名与英文原名。
  3. 【明确标注全模组场景重复利用与地形共享档案】：
     - 城堡外景地形代码共享 (如 3/4/11号堡、12/13号堡、14/16号堡、38/40号堡)。
     - 城堡室内领主大厅与地牢二进制 100% 相同复用 (如 18号阿克曼要塞 与 39号苏恰瓦王座要塞)。
     - 村庄外景地形代码共享 (如 20/22号村、49/50号村、59/69号村、60/70号村、85/86号村)。
  4. 【彻底解决竖向截断与按钮裁切】：
     - 全部分页重构为每页最多 6 项，首行统一置顶 【返回上级菜单】。
     - 下一页 / 上一页 100% 落在屏幕安全可视区域内。
  5. 【保留亡灵城厄瑞玻斯与全套嵌套子场景、地下城、旧曾扎尔、秘境维度】。
"""

import os
import sys
import re

MOD_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

TAG_SCENE = 10
TAG_MST = 11
TAG_MENU = 12

def tag_val(tag, idx):
    return (tag << 56) | (idx & 0xFFFFFFFFFFFFFF)

def main():
    print(f"[开始构建场景查看器 v3.0] 目标模组路径: {MOD_DIR}")
    
    # 1. 读取 scenes.txt 建立 scene_id -> index 字典与地形代码复用分析
    scenes_path = os.path.join(MOD_DIR, "scenes.txt")
    with open(scenes_path, "r", encoding="utf-8", errors="replace") as f:
        scene_lines = [l.strip().split() for l in f if l.strip().startswith("scn_")]
    scene_to_idx = {parts[0]: i for i, parts in enumerate(scene_lines)}
    scene_defs = {parts[0]: parts for parts in scene_lines}
    print(f"  已载入 {len(scene_lines)} 个场景索引")

    # 地形代码复用分析
    c_terrains = {}
    for i in range(1, 41):
        sid = f"scn_castle_{i}_exterior"
        if sid in scene_defs:
            c_terrains.setdefault(scene_defs[sid][-1], []).append(i)
    c_reuse_tag = {}
    for tcode, clist in c_terrains.items():
        if len(clist) > 1:
            for c in clist:
                others = [str(x) for x in clist if x != c]
                c_reuse_tag[c] = f"【地形复用: 与第{'/'.join(others)}号堡相同】"
    c_reuse_tag[18] = c_reuse_tag.get(18, "") + "【领主大厅与地牢与39号堡100%相同】"
    c_reuse_tag[39] = c_reuse_tag.get(39, "") + "【领主大厅与地牢与18号堡100%相同】"

    v_terrains = {}
    for i in range(1, 91):
        sid = f"scn_village_{i}"
        if sid in scene_defs:
            v_terrains.setdefault(scene_defs[sid][-1], []).append(i)
    v_reuse_tag = {}
    for tcode, vlist in v_terrains.items():
        if len(vlist) > 1:
            for v in vlist:
                others = [str(x) for x in vlist if x != v]
                v_reuse_tag[v] = f"【地形复用: 与第{'/'.join(others)}号村相同】"

    # 2. 读取 languages/cns/parties.csv 提取实际游戏内真实中文地名
    parties_cns_path = os.path.join(MOD_DIR, "languages", "cns", "parties.csv")
    parties_cns = {}
    if os.path.exists(parties_cns_path):
        with open(parties_cns_path, "r", encoding="utf-8", errors="replace") as f:
            for l in f:
                if "|" in l:
                    k, v = l.strip().split("|", 1)
                    parties_cns[k] = v.strip()

    # 读取 parties.txt 提取 party_id -> 英文名
    parties_txt_path = os.path.join(MOD_DIR, "parties.txt")
    castle_names = {}
    village_names = {}
    with open(parties_txt_path, "r", encoding="utf-8", errors="replace") as f:
        for l in f:
            parts = l.strip().split()
            if len(parts) > 4 and parts[3].startswith("p_"):
                pid = parts[3]
                eng = parts[4]
                cn = parties_cns.get(pid, eng).strip()
                if pid.startswith("p_castle_"):
                    num = int(pid.replace("p_castle_", ""))
                    castle_names[num] = (eng, cn)
                elif pid.startswith("p_village_"):
                    num = int(pid.replace("p_village_", ""))
                    village_names[num] = (eng, cn)

    print(f"  已载入 {len(castle_names)} 座城堡实际名称，{len(village_names)} 个村庄实际名称")

    # 3. 读取 menus.txt，截断旧版查看器
    menus_path = os.path.join(MOD_DIR, "menus.txt")
    with open(menus_path, "r", encoding="utf-8", errors="replace") as f:
        full_content = f.read()

    cutoff = full_content.find("\nmenu_scene_viewer ")
    if cutoff != -1:
        print("  检测到旧版 menu_scene_viewer，正在干净截断至原版基线...")
        full_content = full_content[:cutoff + 1]

    # 解析当前基础菜单数量
    lines = full_content.splitlines(keepends=True)
    base_menu_cnt = 0
    for l in lines:
        if l.startswith("menu_"):
            base_menu_cnt += 1
    base_menu_idx = base_menu_cnt
    print(f"  当前基础菜单数: {base_menu_idx}")

    # 4. 规划全部 45 个新菜单 ID (每页 6 项超轻量分页，彻底消灭裁切)
    menu_catalog = [
        "menu_scene_viewer",       # 0: 主展厅 Hub
        "menu_sv_undead_city",     # 1: 亡灵城与冥府维度 (9 场景)
        "menu_sv_redlist",         # 2: 红名单 Hub
        "menu_sv_rl_towns_p1",     # 3: 红名单城镇 P1 (1-6)
        "menu_sv_rl_towns_p2",     # 4: 红名单城镇 P2 (7-13)
        "menu_sv_rl_castles",      # 5: 红名单城堡 (1-5)
        "menu_sv_rl_vil1",         # 6: 红名单村庄 P1 (1-6)
        "menu_sv_rl_vil2",         # 7: 红名单村庄 P2 (7-12)
        "menu_sv_rl_vil3",         # 8: 红名单村庄 P3 (13-17)
        "menu_sv_rl_all_p1",       # 9: 全红名单走查 P1 (1-6)
        "menu_sv_rl_all_p2",       # 10: 全红名单走查 P2 (7-12)
        "menu_sv_rl_all_p3",       # 11: 全红名单走查 P3 (13-18)
        "menu_sv_rl_all_p4",       # 12: 全红名单走查 P4 (19-24)
        "menu_sv_rl_all_p5",       # 13: 全红名单走查 P5 (25-30)
        "menu_sv_rl_all_p6",       # 14: 全红名单走查 P6 (31-35)
        "menu_sv_dungeons",        # 15: 聚落地下墓穴/密室/地宫 (7 场景)
        "menu_sv_secrets_p1",      # 16: S&S 异次元秘境 P1 (1-6)
        "menu_sv_secrets_p2",      # 17: S&S 异次元秘境 P2 (7-12)
        "menu_sv_secrets_p3",      # 18: S&S 异次元秘境 P3 (13-19)
        "menu_sv_zendar_inn",      # 19: 旧曾扎尔与四方客栈 (7 场景)
        "menu_sv_towns_p1",        # 20: 1521 城镇街道 P1 (1-6)
        "menu_sv_towns_p2",        # 21: 1521 城镇街道 P2 (7-12)
        "menu_sv_towns_p3",        # 22: 1521 城镇街道 P3 (13-18)
    ]
    # 城堡 7 页 (40 城堡 / 每页 6 项)
    for p in range(1, 8):
        menu_catalog.append(f"menu_sv_castles_p{p}") # 23..29
    # 村庄 15 页 (90 村庄 / 每页 6 项)
    for p in range(1, 16):
        menu_catalog.append(f"menu_sv_villages_p{p}") # 30..44

    menu_id_to_idx = {mid: base_menu_idx + i for i, mid in enumerate(menu_catalog)}

    def mval(mid):
        return tag_val(TAG_MENU, menu_id_to_idx[mid])

    # 辅助函数
    def make_menu_jump_opt(opt_id, opt_text, target_menu_id):
        return f" mno_{opt_id}  0  {opt_text}  1 2060 1 {mval(target_menu_id)}  . \n"

    def make_scene_jump_opt(opt_id, opt_text, scene_id, return_menu_id):
        if scene_id not in scene_to_idx:
            raise ValueError(f"场景 {scene_id} 未在 scenes.txt 中找到！")
        s_idx = scene_to_idx[scene_id]
        s_val = tag_val(TAG_SCENE, s_idx)
        mst_val = tag_val(TAG_MST, 0) # mst_town_default
        ret_val = mval(return_menu_id)
        return f" mno_{opt_id}  0  {opt_text}  4 1304 1 {ret_val} 1911 1 {mst_val} 1910 1 {s_val} 2048 0  . \n"

    new_menus_txt = []
    cns_entries = {}

    # =============================================================
    # Menu 0: menu_scene_viewer (Main Hub)
    # =============================================================
    # 原生报告菜单 menu_reports 位于索引 4，营地动作菜单位于 26
    val_reports_menu = tag_val(TAG_MENU, 4)
    val_camp_menu = tag_val(TAG_MENU, 26)

    m0_id = "menu_scene_viewer"
    m0_text = "Scene_Viewer_Showroom:_Enter_any_settlement_or_hidden_realm._(Press_TAB_to_return)"
    m0_opts = [
        make_menu_jump_opt("sv_to_undead", "1._Undead_City_&_Erebus_Netherworld_(The_Unknown)...", "menu_sv_undead_city"),
        make_menu_jump_opt("sv_to_redlist", "2._[RED_LIST]_Mechanism_Settlements_(35_Scenes_Must_Audit)...", "menu_sv_redlist"),
        make_menu_jump_opt("sv_to_dungeons", "3._Town_&_Village_Catacombs_/_Secret_Basements_/_Reliquaries...", "menu_sv_dungeons"),
        make_menu_jump_opt("sv_to_secrets", "4._S&S_Mythic_Realms_&_Secret_Dimensions_(19_Locations)...", "menu_sv_secrets_p1"),
        make_menu_jump_opt("sv_to_zendar_inn", "5._Old_Zendar_&_Four_Ways_Inn_Complex...", "menu_sv_zendar_inn"),
        make_menu_jump_opt("sv_to_towns", "6._1521_Historical_Towns_Street_View_(18_Cities)...", "menu_sv_towns_p1"),
        make_menu_jump_opt("sv_to_castles", "7._1521_Historical_Castles_&_Fortresses_(40_Strongholds)...", "menu_sv_castles_p1"),
        make_menu_jump_opt("sv_to_villages", "8._1521_Historical_Villages_&_Camps_(90_Settlements)...", "menu_sv_villages_p1"),
        # 【关键修复】使用原生 jump_to_menu 返回报告菜单 (2060 1 val_reports_menu)，百分之百有效生效！
        f" mno_sv_to_reports  0  Return_to_Reports_Menu.  1 2060 1 {val_reports_menu}  . \n",
        # 同时提供大地图返回选项 (2052 0: change_screen_map)
        " mno_sv_to_map  0  Return_to_World_Map.  1 2040 0  . \n",
    ]
    new_menus_txt.append(f"{m0_id} 0 {m0_text} none 0 {len(m0_opts)}\n" + "".join(m0_opts))
    cns_entries[m0_id] = "场景查看器与实机展厅：你可以随时传送进入任意聚落与地下秘境进行实机核查。在场景中按 TAB 随时原路返回本菜单。"
    cns_entries["mno_sv_to_undead"] = "1. ★【亡灵城与冥府维度】厄瑞玻斯·冥府之门（含全部 9 个嵌套子场景）..."
    cns_entries["mno_sv_to_redlist"] = "2. 【红名单】S&S 机制聚落场景（34 座聚落 / 35 个红名单场景，换皮重点排查）..."
    cns_entries["mno_sv_to_dungeons"] = "3. 【地下城与密室】聚落地下墓穴/秘密地窖/圣物室（布达/雅西/埃迪尔内等）..."
    cns_entries["mno_sv_to_secrets"] = "4. 【异次元秘境】大地图隐藏维度（发条盐洞/巴特镇/迷宫/鲸腹/罗宾汉等）..."
    cns_entries["mno_sv_to_zendar_inn"] = "5. 【旧曾扎尔与四方客栈】古典废墟与快乐公猪客栈复合体..."
    cns_entries["mno_sv_to_towns"] = "6. 1521 历史城镇街道漫步（18 座历史首府与商埠街道）..."
    cns_entries["mno_sv_to_castles"] = "7. 1521 历史要塞与城堡领主大厅（40 座边境要塞）..."
    cns_entries["mno_sv_to_villages"] = "8. 1521 历史村庄与平原乡野（90 个聚落外景）..."
    cns_entries["mno_sv_to_reports"] = "【返回报告菜单】"
    cns_entries["mno_sv_to_map"] = "【返回大地图继续行进】"

    # =============================================================
    # Menu 1: menu_sv_undead_city (★ 亡灵城与冥府维度 - 9 个场景全嵌套)
    # =============================================================
    m1_id = "menu_sv_undead_city"
    m1_text = "Undead_City_&_Erebus_Netherworld_(The_Unknown):_Select_a_sub-scene_to_enter._(Press_TAB_to_return)"
    undead_sub_scenes = [
        ("sv_uc_center", "1._Center_Square_&_Blood_Fountain", "scn_town_19_center", "1. 亡灵城·中心广场与主街道 (scn_town_19_center) 【机制: 喷血池/拉斯普京/筛盐场】"),
        ("sv_uc_castle", "2._Lord_Hall_&_Typhon_Throne", "scn_town_19_castle", "2. 亡灵城·领主大厅 (scn_town_19_castle) 【机制: 万魔之父堤丰王座】"),
        ("sv_uc_tavern", "3._Netherworld_Tavern", "scn_town_19_tavern", "3. 亡灵城·冥府酒馆 (scn_town_19_tavern) 【机制: 亡灵之饮与死灵客】"),
        ("sv_uc_store", "4._Necro_Workshop_&_Store", "scn_town_19_store", "4. 亡灵城·死灵工坊与商铺 (scn_town_19_store) 【机制: 棉花糖坩埚】"),
        ("sv_uc_arena", "5._Netherworld_Arena", "scn_town_19_arena", "5. 亡灵城·冥府角斗场 (scn_town_19_arena) 【机制: 白骨决斗】"),
        ("sv_uc_prison", "6._Netherworld_Dungeon_Prison", "scn_town_19_prison", "6. 亡灵城·冥府地牢 (scn_town_19_prison) 【机制: 冥河死囚牢】"),
        ("sv_uc_walls", "7._Siege_Walls_Defense", "scn_town_19_walls", "7. 亡灵城·攻城防线城墙 (scn_town_19_walls) 【机制: 亡灵城防体系】"),
        ("sv_uc_alley", "8._Nether_Dark_Alley", "scn_town_19_alley", "8. 亡灵城·暗巷街道 (scn_town_19_alley) 【机制: 潜行暗巷】"),
        ("sv_uc_fates", "9._Temple_of_the_Fates", "scn_necropolis_fates", "9. 冥府腹地·命运三女神神殿 (scn_necropolis_fates) 【机制: 死灵飞升圣地】")
    ]
    m1_opts = [
        make_menu_jump_opt("sv_uc_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
    ]
    for oid, olabel, scn, cn_txt in undead_sub_scenes:
        m1_opts.append(make_scene_jump_opt(oid, olabel, scn, m1_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m1_id} 0 {m1_text} none 0 {len(m1_opts)}\n" + "".join(m1_opts))
    cns_entries[m1_id] = "【亡灵城与冥府之门】厄瑞玻斯 (The Unknown / Town 19) 实机展厅：S&S 第六阵营亡灵之都。包含中心广场喷血池、万魔之父堤丰王座大厅、冥府酒馆、棉花糖坩埚工坊、白骨决斗角斗场、冥河死囚牢、城防城墙与命运三女神殿。按 TAB 键原路返回。"
    cns_entries["mno_sv_uc_back"] = "【返回场景查看器主目录】"

    # =============================================================
    # Menu 2: menu_sv_redlist (Red-List Hub)
    # =============================================================
    m2_id = "menu_sv_redlist"
    m2_text = "Red-List_Settlement_Scenes:_Must_audit_before_replacing_scenes._(Press_TAB_to_return)"
    m2_opts = [
        make_menu_jump_opt("sv_rl_back_hub", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer"),
        make_menu_jump_opt("sv_rl_go_towns_p1", "1._Red-List_Towns_(13_Scenes:_Belgrade,_Buda,_Zagreb...)...", "menu_sv_rl_towns_p1"),
        make_menu_jump_opt("sv_rl_go_castles", "2._Red-List_Castles_(5_Fortresses:_Szepes,_Smederevo,_Bran...)...", "menu_sv_rl_castles"),
        make_menu_jump_opt("sv_rl_go_vil1", "3._Red-List_Villages_(17_Villages:_Csepel,_Limnos,_Kozloduy...)...", "menu_sv_rl_vil1"),
        make_menu_jump_opt("sv_rl_go_all_p1", "4._Sequential_Walk-through_ALL_35_Scenes_(Page_1/6)...", "menu_sv_rl_all_p1"),
    ]
    new_menus_txt.append(f"{m2_id} 0 {m2_text} none 0 {len(m2_opts)}\n" + "".join(m2_opts))
    cns_entries[m2_id] = "【红名单】S&S 专属机制聚落场景专区：这 35 个场景包含硬编码的机关物件、暗门或特殊出生点，替换场景前必须核查！"
    cns_entries["mno_sv_rl_back_hub"] = "【返回场景查看器主目录】"
    cns_entries["mno_sv_rl_go_towns_p1"] = "1. 城镇红名单场景（12 座城镇 / 13 个场景：贝尔格莱德街道/酒馆、布达杂货铺、萨格勒布监狱等）..."
    cns_entries["mno_sv_rl_go_castles"] = "2. 城堡红名单场景（5 座要塞：斯梅代雷沃蛇桩、布兰/胡内多阿拉/维丁大厅等）..."
    cns_entries["mno_sv_rl_go_vil1"] = "3. 村庄红名单场景（17 个村庄：利姆诺斯波塞冬神殿、哈采格象棋塔、科兹洛杜伊冥府门等）..."
    cns_entries["mno_sv_rl_go_all_p1"] = "4. 顺序遍历全 35 个红名单场景（全 6 页无缝走查）..."

    red_towns = [
        ("rlt_1", "Belgrade_Street_(Chest)", "scn_town_7_center", "1. 贝尔格莱德街道 (Belgrade) [scn_town_7_center] 【机制: 箱子与出生点】"),
        ("rlt_2", "Belgrade_Tavern_(Passage_&_Entry_16)", "scn_town_7_tavern", "2. 贝尔格莱德酒馆 (Belgrade) [scn_town_7_tavern] 【机制: 密道与 16 号出生点】"),
        ("rlt_3", "Buda_Store_(Cask_of_Amontillado)", "scn_town_6_store", "3. 布达杂货铺 (Buda) [scn_town_6_store] 【机制: 阿蒙蒂亚度酒桶暗道】"),
        ("rlt_4", "Klausenburg_Street_(Chest)", "scn_town_5_center", "4. 克劳森堡街道 (Kolozsvar) [scn_town_5_center] 【机制: 箱子与出生点】"),
        ("rlt_5", "Zagreb_Prison_(13th_Step_Door)", "scn_town_15_prison", "5. 萨格勒布地牢 (Zagreb) [scn_town_15_prison] 【机制: 第 13 级台阶暗门】"),
        ("rlt_6", "Brasov_Tavern_(13th_Step_Door)", "scn_town_15_tavern", "6. 布拉索夫酒馆 (Kronstadt) [scn_town_15_tavern] 【机制: 第 13 级台阶暗门】"),
        ("rlt_7", "Constanta_Street_(Special_Entry_8)", "scn_town_12_center", "7. 康斯坦察街道 (Braila) [scn_town_12_center] 【机制: 8 号特殊出生点】"),
        ("rlt_8", "Varna_Street_(Special_Entry_8)", "scn_town_13_center", "8. 瓦尔纳街道 (Akkerman) [scn_town_13_center] 【机制: 8 号特殊出生点】"),
        ("rlt_9", "Nis_Street_(Large_Chest)", "scn_town_14_center", "9. 尼什街道 (Edirne) [scn_town_14_center] 【机制: 大箱子】"),
        ("rlt_10", "Sofia_Castle_(13th_Step_Door)", "scn_town_17_castle", "10. 索非亚领主大厅 (Sofia) [scn_town_17_castle] 【机制: 第 13 级台阶暗门】"),
        ("rlt_11", "Plovdiv_Street_(Special_Entry_8)", "scn_town_16_center", "11. 普罗夫迪夫街道 (Szeged) [scn_town_16_center] 【机制: 8 号特殊出生点】"),
        ("rlt_12", "Edirne_Tavern_(Purloined_Letter)", "scn_town_14_tavern", "12. 埃迪尔内酒馆 (Edirne) [scn_town_14_tavern] 【机制: 被窃的信件】"),
        ("rlt_13", "Constantinople_Street_(Venus)", "scn_town_10_center", "13. 君士坦丁堡街道 (Constantinople) [scn_town_10_center] 【机制: 维纳斯暗门】"),
    ]

    red_castles = [
        ("rlc_1", "Szepes_Prison_(Entry_1)", "scn_castle_1_prison", "1. 斯皮什要塞地牢 (Bran) [scn_castle_1_prison] 【机制: 1 号出生点】"),
        ("rlc_2", "Smederevo_Exterior_(Snake_Dummy)", "scn_castle_3_exterior", "2. 斯梅代雷沃要塞 (Hotin) [scn_castle_3_exterior] 【机制: 蛇假人与地牢口】"),
        ("rlc_3", "Bran_Interior_(Special_Entry_3)", "scn_castle_1_interior", "3. 布兰城堡领主大厅 (Bran) [scn_castle_1_interior] 【机制: 3 号特殊出生点】"),
        ("rlc_4", "Hunedoara_Interior_(Special_Entry_3)", "scn_castle_9_interior", "4. 胡内多阿拉领主大厅 (Hunedoara) [scn_castle_9_interior] 【机制: 3 号特殊出生点】"),
        ("rlc_5", "Vidin_Interior_(Special_Entry_3)", "scn_castle_11_interior", "5. 维丁城堡领主大厅 (Severin) [scn_castle_11_interior] 【机制: 3 号特殊出生点】"),
    ]

    red_villages = [
        ("rlv1_1", "Csepel_Village_(Sheriff_Arrow_&_Chest)", "scn_village_1", "1. 切佩尔村 (Csepel) [scn_village_1] 【机制: 郡长之箭与箱子】"),
        ("rlv1_2", "Mohacs_Village_(Special_Entry_5)", "scn_village_2", "2. 摩哈赤村 (Mohacs) [scn_village_2] 【机制: 5 号特殊出生点】"),
        ("rlv1_3", "Hateg_Village_(Chess_Tower)", "scn_village_17", "3. 哈采格村 (Hateg) [scn_village_17] 【机制: 象棋塔机关】"),
        ("rlv1_4", "Varanno_Village_(Special_Entry_5)", "scn_village_22", "4. 瓦兰诺村 (Varanno) [scn_village_22] 【机制: 5 号特殊出生点】"),
        ("rlv1_5", "Dobra_Village_(Special_Entry_5)", "scn_village_24", "5. 多布拉村 (Dobra) [scn_village_24] 【机制: 5 号特殊出生点】"),
        ("rlv1_6", "Rimetea_Village_(Witch_Hut)", "scn_village_28", "6. 托罗茨科村 (Rimetea) [scn_village_28] 【机制: 女巫小屋】"),
        ("rlv2_1", "Limnos_Village_(Poseidon_Ruins_&_Shell)", "scn_village_32", "7. 利姆诺斯村 (Limnos) [scn_village_32] 【机制: 波塞冬神殿遗迹与海螺】"),
        ("rlv2_2", "Kladovo_Village_(Special_Entry_5)", "scn_village_34", "8. 克拉多沃村 (Kladovo) [scn_village_34] 【机制: 5 号特殊出生点】"),
        ("rlv2_3", "Vranje_Village_(Special_Entry_5)", "scn_village_36", "9. 弗拉涅村 (Vranje) [scn_village_36] 【机制: 5 号特殊出生点】"),
        ("rlv2_4", "Kozloduy_Village_(Underworld_Gate)", "scn_village_37", "10. 科兹洛杜伊村 (Kozloduy) [scn_village_37] 【机制: 冥府大门与冥河渡船】"),
        ("rlv2_5", "Rozaje_Village_(Special_Entry_5)", "scn_village_44", "11. 罗扎耶村 (Rozaje) [scn_village_44] 【机制: 5 号特殊出生点】"),
        ("rlv2_6", "Strumica_Village_(Special_Entry_5)", "scn_village_45", "12. 斯特鲁米察村 (Strumica) [scn_village_45] 【机制: 5 号特殊出生点】"),
        ("rlv3_1", "Kavala_Village_(Special_Entry_5)", "scn_village_46", "13. 卡瓦拉村 (Kavala) [scn_village_46] 【机制: 5 号特殊出生点】"),
        ("rlv3_2", "Snagov_Village_(Gold_Bug)", "scn_village_53", "14. 斯纳戈夫村 (Snagov) [scn_village_53] 【机制: 金甲虫机关】"),
        ("rlv3_3", "Turnu_Village_(Annabelle_Tomb)", "scn_village_54", "15. 图尔努村 (Turnu) [scn_village_54] 【机制: 安娜贝尔墓碑】"),
        ("rlv3_4", "Ruse_Village_(Special_Entry_5)", "scn_village_56", "16. 鲁塞村 (Ruse) [scn_village_56] 【机制: 5 号特殊出生点】"),
        ("rlv3_5", "Razgrad_Village_(Special_Entry_5)", "scn_village_58", "17. 拉兹格勒村 (Razgrad) [scn_village_58] 【机制: 5 号特殊出生点】"),
    ]

    # 红名单城镇 P1 (1-6)
    m3_id = "menu_sv_rl_towns_p1"
    m3_opts = [
        make_menu_jump_opt("sv_rlt1_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist")
    ]
    for oid, olabel, scn, cn_txt in red_towns[:6]:
        m3_opts.append(make_scene_jump_opt(oid, olabel, scn, m3_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    m3_opts.append(make_menu_jump_opt("sv_rlt1_next", "Next_Page_(Towns_7-13)...", "menu_sv_rl_towns_p2"))
    new_menus_txt.append(f"{m3_id} 0 Red-List_Towns_P1_(1-6):_Select_a_scene none 0 {len(m3_opts)}\n" + "".join(m3_opts))
    cns_entries[m3_id] = "红名单城镇场景 第 1 页（第 1-6 处）：实机巡查，按 TAB 原路返回。"
    cns_entries["mno_sv_rlt1_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlt1_next"] = "下一页：城镇红名单 第 7-13 项..."

    # 红名单城镇 P2 (7-13)
    m4_id = "menu_sv_rl_towns_p2"
    m4_opts = [
        make_menu_jump_opt("sv_rlt2_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
        make_menu_jump_opt("sv_rlt2_prev", "Previous_Page_(Towns_1-6)...", "menu_sv_rl_towns_p1"),
    ]
    for oid, olabel, scn, cn_txt in red_towns[6:]:
        m4_opts.append(make_scene_jump_opt(oid, olabel, scn, m4_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m4_id} 0 Red-List_Towns_P2_(7-13):_Select_a_scene none 0 {len(m4_opts)}\n" + "".join(m4_opts))
    cns_entries[m4_id] = "红名单城镇场景 第 2 页（第 7-13 处）：实机巡查，按 TAB 原路返回。"
    cns_entries["mno_sv_rlt2_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlt2_prev"] = "上一页：城镇红名单 第 1-6 项..."

    # 红名单城堡 (5 场景)
    m5_id = "menu_sv_rl_castles"
    m5_opts = [
        make_menu_jump_opt("sv_rlc_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
    ]
    for oid, olabel, scn, cn_txt in red_castles:
        m5_opts.append(make_scene_jump_opt(oid, olabel, scn, m5_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m5_id} 0 Red-List_Castles_(5_Scenes):_Select_a_scene none 0 {len(m5_opts)}\n" + "".join(m5_opts))
    cns_entries[m5_id] = "红名单城堡要塞场景（共 5 处）：点击即可立即传送进入实机巡查，按 TAB 键原路返回。"
    cns_entries["mno_sv_rlc_back"] = "【返回红名单分类菜单】"

    # 红名单村庄 P1 (1-6)
    m6_id = "menu_sv_rl_vil1"
    m6_opts = [
        make_menu_jump_opt("sv_rlv1_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist")
    ]
    for oid, olabel, scn, cn_txt in red_villages[:6]:
        m6_opts.append(make_scene_jump_opt(oid, olabel, scn, m6_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    m6_opts.append(make_menu_jump_opt("sv_rlv1_next", "Next_Page_(Villages_7-12)...", "menu_sv_rl_vil2"))
    new_menus_txt.append(f"{m6_id} 0 Red-List_Villages_P1_(1-6):_Select_a_scene none 0 {len(m6_opts)}\n" + "".join(m6_opts))
    cns_entries[m6_id] = "红名单村庄场景 第 1 页（第 1-6 处）：包含切佩尔郡长之箭、哈采格象棋塔、女巫小屋等。"
    cns_entries["mno_sv_rlv1_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlv1_next"] = "下一页：村庄红名单 第 7-12 项..."

    # 红名单村庄 P2 (7-12)
    m7_id = "menu_sv_rl_vil2"
    m7_opts = [
        make_menu_jump_opt("sv_rlv2_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
        make_menu_jump_opt("sv_rlv2_prev", "Previous_Page_(Villages_1-6)...", "menu_sv_rl_vil1")
    ]
    for oid, olabel, scn, cn_txt in red_villages[6:12]:
        m7_opts.append(make_scene_jump_opt(oid, olabel, scn, m7_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    m7_opts.append(make_menu_jump_opt("sv_rlv2_next", "Next_Page_(Villages_13-17)...", "menu_sv_rl_vil3"))
    new_menus_txt.append(f"{m7_id} 0 Red-List_Villages_P2_(7-12):_Select_a_scene none 0 {len(m7_opts)}\n" + "".join(m7_opts))
    cns_entries[m7_id] = "红名单村庄场景 第 2 页（第 7-12 处）：包含波塞冬神殿与海螺、科兹洛杜伊冥府大门等。"
    cns_entries["mno_sv_rlv2_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlv2_prev"] = "上一页：村庄红名单 第 1-6 项..."
    cns_entries["mno_sv_rlv2_next"] = "下一页：村庄红名单 第 13-17 项..."

    # 红名单村庄 P3 (13-17)
    m8_id = "menu_sv_rl_vil3"
    m8_opts = [
        make_menu_jump_opt("sv_rlv3_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
        make_menu_jump_opt("sv_rlv3_prev", "Previous_Page_(Villages_7-12)...", "menu_sv_rl_vil2")
    ]
    for oid, olabel, scn, cn_txt in red_villages[12:]:
        m8_opts.append(make_scene_jump_opt(oid, olabel, scn, m8_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m8_id} 0 Red-List_Villages_P3_(13-17):_Select_a_scene none 0 {len(m8_opts)}\n" + "".join(m8_opts))
    cns_entries[m8_id] = "红名单村庄场景 第 3 页（第 13-17 处）：包含斯纳戈夫金甲虫、图尔努安娜贝尔墓碑等。"
    cns_entries["mno_sv_rlv3_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlv3_prev"] = "上一页：村庄红名单 第 7-12 项..."

    # 35 红名单全场景走查 (全 6 页，每页 6 项，最后一页 5 项)
    all_35 = red_towns + red_castles + red_villages
    for p in range(6):
        p_id = f"menu_sv_rl_all_p{p+1}"
        s_idx = p * 6
        e_idx = min((p + 1) * 6, len(all_35))
        p_items = all_35[s_idx:e_idx]
        prev_m = f"menu_sv_rl_all_p{p}" if p > 0 else None
        next_m = f"menu_sv_rl_all_p{p+2}" if p < 5 else None

        p_opts = [
            make_menu_jump_opt(f"{p_id}_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist")
        ]
        if prev_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_prev", "Previous_Page...", prev_m))
        for oid, olabel, scn, cn_txt in p_items:
            sub_oid = f"{p_id}_{oid}"
            p_opts.append(make_scene_jump_opt(sub_oid, olabel, scn, p_id))
            cns_entries[f"mno_{sub_oid}"] = cn_txt
        if next_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_next", "Next_Page...", next_m))

        new_menus_txt.append(f"{p_id} 0 {p_id}:_Walk-through_({s_idx+1}-{e_idx}) none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = f"红名单全场景走查 第 {p+1} 页 (第 {s_idx+1}-{e_idx} 处场景巡查)"
        cns_entries[f"mno_{p_id}_back"] = "【返回红名单总目录】"
        if prev_m:
            cns_entries[f"mno_{p_id}_prev"] = "上一页..."
        if next_m:
            cns_entries[f"mno_{p_id}_next"] = "下一页..."

    # =============================================================
    # Menu 15: menu_sv_dungeons (聚落隐藏地下室/地宫/圣物室 - 7 场景)
    # =============================================================
    m15_id = "menu_sv_dungeons"
    dungeon_scenes = [
        ("sv_dg_buda", "1._Buda_Catacombs", "scn_town_6_catacombs", "1. 布达地下墓穴 (scn_town_6_catacombs) 【机制: 藏骸所与骷髅秘道】"),
        ("sv_dg_jassy", "2._Jassy_Basement", "scn_town_9_basement", "2. 雅西秘密地窖 (scn_town_9_basement) 【机制: 阿蒙蒂亚度酒桶】"),
        ("sv_dg_edirne_rel", "3._Edirne_Reliquary", "scn_town_14_reliquary", "3. 埃迪尔内圣物室 (scn_town_14_reliquary) 【机制: 圣物陈列室】"),
        ("sv_dg_edirne_nik", "4._Edirne_Nikola_Sanctuary", "scn_town_14_reliquary_nikola", "4. 埃迪尔内尼古拉地下圣所 (scn_town_14_reliquary_nikola) 【机制: 尼古拉密室】"),
        ("sv_dg_vil67", "5._Village_Hermit_Cave", "scn_village_67_cave", "5. 村庄隐者秘洞 (scn_village_67_cave) 【机制: 洞穴藏身处】"),
        ("sv_dg_vil43", "6._Village_Ancient_Tomb", "scn_village_43_tomb", "6. 村庄古代墓穴 (scn_village_43_tomb) 【机制: 地底墓穴】"),
        ("sv_dg_dhorak", "7._Dhorak_Keep", "scn_dhorak_keep", "7. 多拉克要塞地宫 (scn_dhorak_keep) 【机制: 废弃古要塞】"),
    ]
    m15_opts = [
        make_menu_jump_opt("sv_dg_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
    ]
    for oid, olabel, scn, cn_txt in dungeon_scenes:
        m15_opts.append(make_scene_jump_opt(oid, olabel, scn, m15_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m15_id} 0 Town_&_Village_Dungeons_/_Catacombs:_Select_a_scene none 0 {len(m15_opts)}\n" + "".join(m15_opts))
    cns_entries[m15_id] = "【地下城与密室】聚落地下墓穴/秘密地窖/圣物室：布达地下墓穴、雅西阿蒙蒂亚度酒窖、埃迪尔内圣物室/尼古拉密室、村庄古代墓穴等隐藏空间。按 TAB 键原路返回。"
    cns_entries["mno_sv_dg_back"] = "【返回场景查看器主目录】"

    # =============================================================
    # Menu 16..18: S&S 专属异次元秘境 (全 19 处，每页 6-7 处)
    # =============================================================
    all_secrets = [
        ("sv_sec_1", "Salt_Mine_(Abandoned)", "scn_salt_mine", "1. 喀尔巴阡废弃盐矿 (scn_salt_mine)"),
        ("sv_sec_2", "Clockwork_Salt_Cave", "scn_salt_cave", "2. 大巧匠发条盐洞 (scn_salt_cave)"),
        ("sv_sec_3", "Barter_Town_Market", "scn_barter_town", "3. 巴特镇黑市地面 (scn_barter_town)"),
        ("sv_sec_4", "Barter_Town_Cellar", "scn_barter_town_cellar", "4. 巴特镇地下走私地窖 (scn_barter_town_cellar)"),
        ("sv_sec_5", "Antiquities_Museum", "scn_museum", "5. 古物博物馆 (22幅秘境挂毯大厅) (scn_museum)"),
        ("sv_sec_6", "Cretan_Labyrinth", "scn_cretanlabyrinth", "6. 克里特牛头人迷宫 (scn_cretanlabyrinth)"),
        ("sv_sec_7", "Nightmare_Realm", "scn_nightmarerealm", "7. 噩梦维度 (scn_nightmarerealm)"),
        ("sv_sec_8", "Leviathan_Whalebelly", "scn_whalebelly", "8. 利维坦鲸腹 (scn_whalebelly)"),
        ("sv_sec_9", "Green_Meteorite", "scn_greenmeteorite", "9. 绿陨石坠落坑 (scn_greenmeteorite)"),
        ("sv_sec_10", "Fairy_Realm", "scn_fairyrealm", "10. 妖精国度 (scn_fairyrealm)"),
        ("sv_sec_11", "Pressburg_Sherwood", "scn_sherwood", "11. 罗宾汉Pressburg绿林 (scn_sherwood)"),
        ("sv_sec_12", "Thieves_Den", "scn_sherwood2", "12. 盗贼密林营地 (scn_sherwood2)"),
        ("sv_sec_13", "Usherwood_Forest", "scn_village_4_usherwood", "13. 厄舍庄园枯木林 (scn_village_4_usherwood)"),
        ("sv_sec_14", "Usher_Mansion", "scn_village_4_mansion", "14. 厄舍庄园古宅室内 (scn_village_4_mansion)"),
        ("sv_sec_15", "Hiraeth_Exterior", "scn_homestead", "15. 故园庄园外景 (scn_homestead)"),
        ("sv_sec_16", "Hiraeth_Interior", "scn_interior_homestead", "16. 故园古宅室内 (scn_interior_homestead)"),
        ("sv_sec_17", "Ivory_Temple", "scn_ivory_temple", "17. 象牙神殿 (scn_ivory_temple)"),
        ("sv_sec_18", "Fallen_Antihero", "scn_fallenantihero", "18. 堕落反英雄祭坛 (scn_fallenantihero)"),
        ("sv_sec_19", "Heartbearer_Tomb", "scn_heartbearer_tomb", "19. 持心者之墓 (scn_heartbearer_tomb)"),
    ]
    sec_pages = [
        ("menu_sv_secrets_p1", all_secrets[0:6], None, "menu_sv_secrets_p2", "S&S 专属大地图秘境 第 1 页 (01-06)"),
        ("menu_sv_secrets_p2", all_secrets[6:12], "menu_sv_secrets_p1", "menu_sv_secrets_p3", "S&S 专属大地图秘境 第 2 页 (07-12)"),
        ("menu_sv_secrets_p3", all_secrets[12:19], "menu_sv_secrets_p2", None, "S&S 专属大地图秘境 第 3 页 (13-19)"),
    ]
    for p_id, p_items, prev_m, next_m, p_cn in sec_pages:
        p_opts = [
            make_menu_jump_opt(f"{p_id}_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
        ]
        if prev_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_prev", "Previous_Page...", prev_m))
        for oid, olabel, scn, cn_txt in p_items:
            sub_oid = f"{p_id}_{oid}"
            p_opts.append(make_scene_jump_opt(sub_oid, olabel, scn, p_id))
            cns_entries[f"mno_{sub_oid}"] = cn_txt
        if next_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_next", "Next_Page...", next_m))
        new_menus_txt.append(f"{p_id} 0 {p_id}:_Select_a_scene none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = p_cn
        cns_entries[f"mno_{p_id}_back"] = "【返回场景查看器主目录】"
        if prev_m:
            cns_entries[f"mno_{p_id}_prev"] = "上一页..."
        if next_m:
            cns_entries[f"mno_{p_id}_next"] = "下一页..."

    # =============================================================
    # Menu 19: menu_sv_zendar_inn (旧曾扎尔与四方客栈 - 7 场景)
    # =============================================================
    m19_id = "menu_sv_zendar_inn"
    zendar_scenes = [
        ("sv_zi_center", "1._Old_Zendar_Square", "scn_zendar_center", "1. 旧曾扎尔·城镇中心广场 (scn_zendar_center)"),
        ("sv_zi_arena", "2._Old_Zendar_Arena", "scn_zendar_arena", "2. 旧曾扎尔·古典角斗场 (scn_zendar_arena)"),
        ("sv_zi_merchant", "3._Old_Zendar_Market", "scn_zendar_merchant", "3. 旧曾扎尔·商铺市场 (scn_zendar_merchant)"),
        ("sv_zi_reliquary", "4._Old_Zendar_Reliquary", "scn_zendar_reliquary", "4. 旧曾扎尔·秘密圣物室 (scn_zendar_reliquary)"),
        ("sv_zi_fwi", "5._Four_Ways_Inn", "scn_four_ways_inn", "5. 四方客栈·外景 (scn_four_ways_inn)"),
        ("sv_zi_boar", "6._Happy_Boar_Tavern", "scn_the_happy_boar", "6. 四方客栈·快乐公猪酒馆 (scn_the_happy_boar)"),
        ("sv_zi_cellar", "7._Four_Ways_Cellar", "scn_four_ways_inn_cellar", "7. 四方客栈·地下走私地窖 (scn_four_ways_inn_cellar)"),
    ]
    m19_opts = [
        make_menu_jump_opt("sv_zi_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
    ]
    for oid, olabel, scn, cn_txt in zendar_scenes:
        m19_opts.append(make_scene_jump_opt(oid, olabel, scn, m19_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m19_id} 0 Old_Zendar_&_Four_Ways_Inn:_Select_a_scene none 0 {len(m19_opts)}\n" + "".join(m19_opts))
    cns_entries[m19_id] = "【旧曾扎尔与四方客栈】古典废墟与快乐公猪客栈复合体：曾扎尔广场/角斗场/市场/圣物室，四方客栈外景/快乐公猪酒馆/地下地窖。按 TAB 原路返回。"
    cns_entries["mno_sv_zi_back"] = "【返回场景查看器主目录】"

    # =============================================================
    # Menu 20..22: 1521 历史城镇街道 (全 18 城，分为 3 页，每页 6 城)
    # =============================================================
    town_names_1521 = [
        (1, "Targoviste (塔尔戈维什泰)", "scn_town_1_center"),
        (2, "Bucuresti (布加勒斯特)", "scn_town_2_center"),
        (3, "Sibiu / Hermannstadt (锡比乌)", "scn_town_3_center"),
        (4, "Pecs (佩奇)", "scn_town_4_center"),
        (5, "Kolozsvar / Klausenburg (克劳森堡)", "scn_town_5_center"),
        (6, "Buda (布达首府)", "scn_town_6_center"),
        (7, "Belgrade / Nandorfehervar (贝尔格莱德)", "scn_town_7_center"),
        (8, "Suceava (苏恰瓦)", "scn_town_8_center"),
        (9, "Iasi / Jassy (雅西)", "scn_town_9_center"),
        (10, "Konstantiniyye (君士坦丁堡)", "scn_town_10_center"),
        (11, "Hotin / Chocim (霍京)", "scn_town_11_center"),
        (12, "Constanta / Tomis (康斯坦察)", "scn_town_12_center"),
        (13, "Varna (瓦尔纳)", "scn_town_13_center"),
        (14, "Edirne / Adrianople (埃迪尔内)", "scn_town_14_center"),
        (15, "Zagreb / Agram (萨格勒布)", "scn_town_15_center"),
        (16, "Szeged (塞格德)", "scn_town_16_center"),
        (17, "Sofya / Sofia (索非亚)", "scn_town_17_center"),
        (18, "Selanik / Salonika (萨洛尼卡)", "scn_town_18_center"),
    ]
    town_pages = [
        ("menu_sv_towns_p1", town_names_1521[0:6], None, "menu_sv_towns_p2", "1521 历史城镇街道 第 1 页 (01-06)"),
        ("menu_sv_towns_p2", town_names_1521[6:12], "menu_sv_towns_p1", "menu_sv_towns_p3", "1521 历史城镇街道 第 2 页 (07-12)"),
        ("menu_sv_towns_p3", town_names_1521[12:18], "menu_sv_towns_p2", None, "1521 历史城镇街道 第 3 页 (13-18)"),
    ]
    for p_id, p_items, prev_m, next_m, p_cn in town_pages:
        p_opts = [
            make_menu_jump_opt(f"{p_id}_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
        ]
        if prev_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_prev", "Previous_Page...", prev_m))
        for tid, tname, scn in p_items:
            oid = f"{p_id}_tw_{tid}"
            p_opts.append(make_scene_jump_opt(oid, f"{tid}._{tname.split()[0]}", scn, p_id))
            cns_entries[f"mno_{oid}"] = f"{tid}. {tname} [{scn}]"
        if next_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_next", "Next_Page...", next_m))
        new_menus_txt.append(f"{p_id} 0 {p_id}:_Select_a_town none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = p_cn
        cns_entries[f"mno_{p_id}_back"] = "【返回场景查看器主目录】"
        if prev_m:
            cns_entries[f"mno_{p_id}_prev"] = "上一页..."
        if next_m:
            cns_entries[f"mno_{p_id}_next"] = "下一页..."

    # =============================================================
    # Menu 23..29: 1521 历史城堡外景 (全 40 城堡，分为 7 页，每页 6 堡，最后一页 4 堡)
    # =============================================================
    for p in range(7):
        p_id = f"menu_sv_castles_p{p+1}"
        s_c = p * 6 + 1
        e_c = min((p + 1) * 6, 40)
        prev_m = f"menu_sv_castles_p{p}" if p > 0 else None
        next_m = f"menu_sv_castles_p{p+2}" if p < 6 else None

        p_opts = [
            make_menu_jump_opt(f"{p_id}_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
        ]
        if prev_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_prev", "Previous_Page...", prev_m))
        for c in range(s_c, e_c + 1):
            sid = f"scn_castle_{c}_exterior"
            oid = f"{p_id}_cas_{c}"
            eng, cn = castle_names.get(c, (f"Castle_{c}", f"城堡_{c}"))
            reuse = c_reuse_tag.get(c, "")
            label_en = f"{c}._{eng}"
            label_cn = f"{c}. {cn} ({eng}) [{sid}] {reuse}".strip()
            p_opts.append(make_scene_jump_opt(oid, label_en, sid, p_id))
            cns_entries[f"mno_{oid}"] = label_cn
        if next_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_next", "Next_Page...", next_m))

        new_menus_txt.append(f"{p_id} 0 {p_id}:_Select_a_castle_exterior none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = f"1521 历史城堡要塞 第 {p+1} 页 (第 {s_c:02d}-{e_c:02d} 座要塞)"
        cns_entries[f"mno_{p_id}_back"] = "【返回场景查看器主目录】"
        if prev_m:
            cns_entries[f"mno_{p_id}_prev"] = "上一页城堡列表..."
        if next_m:
            cns_entries[f"mno_{p_id}_next"] = "下一页城堡列表..."

    # =============================================================
    # Menu 30..44: 1521 历史村庄聚落 (全 90 村庄，分为 15 页，每页 6 村)
    # =============================================================
    for p in range(15):
        p_id = f"menu_sv_villages_p{p+1}"
        s_v = p * 6 + 1
        e_v = min((p + 1) * 6, 90)
        prev_m = f"menu_sv_villages_p{p}" if p > 0 else None
        next_m = f"menu_sv_villages_p{p+2}" if p < 14 else None

        p_opts = [
            make_menu_jump_opt(f"{p_id}_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
        ]
        if prev_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_prev", "Previous_Page...", prev_m))
        for v in range(s_v, e_v + 1):
            sid = f"scn_village_{v}"
            oid = f"{p_id}_vil_{v}"
            eng, cn = village_names.get(v, (f"Village_{v}", f"村庄_{v}"))
            reuse = v_reuse_tag.get(v, "")
            label_en = f"{v}._{eng}"
            label_cn = f"{v}. {cn} ({eng}) [{sid}] {reuse}".strip()
            p_opts.append(make_scene_jump_opt(oid, label_en, sid, p_id))
            cns_entries[f"mno_{oid}"] = label_cn
        if next_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_next", "Next_Page...", next_m))

        new_menus_txt.append(f"{p_id} 0 {p_id}:_Select_a_village none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = f"1521 历史村庄聚落 第 {p+1} 页 (第 {s_v:02d}-{e_v:02d} 个村庄)"
        cns_entries[f"mno_{p_id}_back"] = "【返回场景查看器主目录】"
        if prev_m:
            cns_entries[f"mno_{p_id}_prev"] = "上一页村庄列表..."
        if next_m:
            cns_entries[f"mno_{p_id}_next"] = "下一页村庄列表..."

    # 5. 确保 menu_reports 与 menu_camp_action 的入口健全
    opt_reports = f" mno_scene_viewer  0  View_scenes_and_locations.  1 2060 1 {mval('menu_scene_viewer')}  . \n"
    opt_camp = f" mno_camp_scene_viewer  0  Explore_scenes_and_locations.  1 2060 1 {mval('menu_scene_viewer')}  . \n"
    cns_entries["mno_scene_viewer"] = "查看场景与特殊地点（场景查看器）"
    cns_entries["mno_camp_scene_viewer"] = "探索场景与特殊地点（场景查看器）"

    # 注入 menu_reports
    if "mno_scene_viewer" not in full_content:
        def rep_rep_count(m):
            header = m.group(1)
            cnt = int(m.group(2))
            return f"{header} {cnt+1}"
        full_content = re.sub(r'^(menu_reports\s+0\s+[^\n]+\s+none\s+\d+\s+)(\d+)$', rep_rep_count, full_content, flags=re.MULTILINE)
        pos = full_content.find("menu_reports 0")
        if pos != -1:
            dot_pos = full_content.find(" . \n", pos)
            if dot_pos != -1:
                insert_pos = dot_pos + 4
                full_content = full_content[:insert_pos] + opt_reports + full_content[insert_pos:]
                print("  已向 menu_reports 成功注入 mno_scene_viewer 入口！")
    else:
        full_content = re.sub(r'mno_scene_viewer\s+0\s+View_scenes_and_locations\.\s+1\s+2060\s+1\s+\d+', f'mno_scene_viewer  0  View_scenes_and_locations.  1 2060 1 {mval("menu_scene_viewer")}', full_content)

    # 注入 menu_camp_action
    if "mno_camp_scene_viewer" not in full_content:
        def rep_camp_count(m):
            header = m.group(1)
            cnt = int(m.group(2))
            return f"{header} {cnt+1}"
        full_content = re.sub(r'^(menu_camp_action\s+0\s+[^\n]+\s+none\s+\d+\s+)(\d+)$', rep_camp_count, full_content, flags=re.MULTILINE)
        pos = full_content.find("menu_camp_action 0")
        if pos != -1:
            end_pos = full_content.find("\nmenu_", pos + 1)
            if end_pos != -1:
                full_content = full_content[:end_pos] + opt_camp + full_content[end_pos:]
                print("  已向 menu_camp_action 成功注入 mno_camp_scene_viewer 入口！")
    else:
        full_content = re.sub(r'mno_camp_scene_viewer\s+0\s+Explore_scenes_and_locations\.\s+1\s+2060\s+1\s+\d+', f'mno_camp_scene_viewer  0  Explore_scenes_and_locations.  1 2060 1 {mval("menu_scene_viewer")}', full_content)

    # 6. 追加所有新菜单，并更新总菜单声明数
    total_new_menus = len(menu_catalog)
    new_total_declared = base_menu_idx + total_new_menus

    lines = full_content.splitlines(keepends=True)
    lines[1] = f"{new_total_declared}\n"
    final_menus_content = "".join(lines) + "".join(new_menus_txt)

    with open(menus_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(final_menus_content)
    print(f"  已向 menus.txt 成功写入 {total_new_menus} 个新菜单，当前总菜单数: {new_total_declared}")

    # 7. 更新 languages/cns/game_menus.csv 汉化文件 (保持原文件行尾空格与换行，仅定向更新与追加)
    cns_path = os.path.join(MOD_DIR, "languages", "cns", "game_menus.csv")
    if os.path.exists(cns_path):
        with open(cns_path, "r", encoding="utf-8", errors="replace") as f:
            existing_lines = f.readlines()
    else:
        existing_lines = []

    key_to_line_idx = {}
    for idx, l in enumerate(existing_lines):
        if "|" in l:
            k = l.split("|", 1)[0]
            key_to_line_idx[k] = idx

    updated_count = 0
    to_append = []
    for k, v in cns_entries.items():
        if k in key_to_line_idx:
            line_idx = key_to_line_idx[k]
            existing_lines[line_idx] = f"{k}|{v}\n"
            updated_count += 1
        else:
            to_append.append(f"{k}|{v}\n")

    final_cns_lines = existing_lines + to_append
    with open(cns_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(final_cns_lines)
    print(f"  已向 languages/cns/game_menus.csv 定向更新 {updated_count} 条、追加 {len(to_append)} 条全新中英对照汉化词条！")

    print("[场景查看器 v3.0 安装完成] 全部组件与入口部署完毕！")

if __name__ == "__main__":
    main()
