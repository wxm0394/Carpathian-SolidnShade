#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade (1521) — 场景查看器 (Scene Viewer & Showroom) 安装器 v2.0
=============================================================================
全面升级特性：
  1. 【修复退出到主界面 Bug】：返回按钮采用 2040 (change_screen_return)，绝不再误触 2055 (change_screen_quit) 退出存档。
  2. 【彻底解决返回按钮被遮挡截断】：每个子菜单均将 [返回上级菜单] 置于选项第一行 (顶部)，且每页最多展示 9-10 个场景，杜绝 Warband 界面竖向裁切。
  3. 【亡灵城与冥府之门全嵌套展厅】：收录 The Unknown (厄瑞玻斯 / Town 19) 全套 8 个子场景 (主街喷血池/万魔王座/酒馆/坩埚工坊/角斗场/地牢/城墙/暗巷) + 命运三女神殿。
  4. 【聚落地下墓穴/密室/地宫专区】：布达地下墓穴、雅西地窖、埃迪尔内圣物室/尼古拉密室、村庄洞穴/古墓、多拉克地宫等。
  5. 【旧曾扎尔与四方客栈复合体】：曾扎尔广场/角斗场/市场/圣物室、四方客栈外景/快乐公猪酒馆/地下走私地窖。
  6. 【S&S 专属异次元秘境】：发条盐洞、巴特镇、牛头人迷宫、噩梦维度、利维坦鲸腹、绿陨石、妖精国度、罗宾汉Pressburg密林、厄舍古宅、故园庄园、象牙神殿等。
  7. 【红名单 35 机制场景精准分类与顺序走查】。
  8. 【1521 城镇/城堡/村庄大地图场景全覆盖漫游】。
  9. TAB 键原路返回所在子菜单，全量中文对照写入 languages/cns/game_menus.csv。
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
    print(f"[开始构建场景查看器 v2.0] 目标模组路径: {MOD_DIR}")
    
    # 1. 读取 scenes.txt 建立 scene_id -> index 字典
    scenes_path = os.path.join(MOD_DIR, "scenes.txt")
    with open(scenes_path, "r", encoding="utf-8", errors="replace") as f:
        scenes = [l.strip().split()[0] for l in f if l.strip().startswith("scn_")]
    scene_to_idx = {s: i for i, s in enumerate(scenes)}
    print(f"  已载入 {len(scenes)} 个场景索引")

    # 2. 读取 menus.txt，如果已安装旧版查看器，则从 menu_scene_viewer 处干净截断
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

    # 3. 规划全部 31 个新菜单 ID
    menu_catalog = [
        "menu_scene_viewer",       # 0: 主展厅 Hub
        "menu_sv_undead_city",     # 1: ★ 亡灵城与冥府维度 (9 场景嵌套)
        "menu_sv_redlist",         # 2: 红名单 Hub
        "menu_sv_rl_towns_p1",     # 3: 红名单城镇 P1 (7 场景)
        "menu_sv_rl_towns_p2",     # 4: 红名单城镇 P2 (6 场景)
        "menu_sv_rl_castles",      # 5: 红名单城堡 (5 场景)
        "menu_sv_rl_vil1",         # 6: 红名单村庄 P1 (9 场景)
        "menu_sv_rl_vil2",         # 7: 红名单村庄 P2 (8 场景)
        "menu_sv_rl_all_p1",       # 8: 全红名单走查 P1 (1-9)
        "menu_sv_rl_all_p2",       # 9: 全红名单走查 P2 (10-18)
        "menu_sv_rl_all_p3",       # 10: 全红名单走查 P3 (19-27)
        "menu_sv_rl_all_p4",       # 11: 全红名单走查 P4 (28-35)
        "menu_sv_dungeons",        # 12: 聚落地下墓穴/密室/地宫 (7 场景)
        "menu_sv_secrets_1",       # 13: S&S 异次元秘境 P1 (8 处)
        "menu_sv_secrets_2",       # 14: S&S 异次元秘境 P2 (11 处)
        "menu_sv_zendar_inn",      # 15: 旧曾扎尔与四方客栈 (7 场景)
        "menu_sv_towns_p1",        # 16: 1521 城镇街道 P1 (1-9)
        "menu_sv_towns_p2",        # 17: 1521 城镇街道 P2 (10-18)
        "menu_sv_castles_p1",      # 18: 1521 城堡 P1 (1-10)
        "menu_sv_castles_p2",      # 19: 1521 城堡 P2 (11-20)
        "menu_sv_castles_p3",      # 20: 1521 城堡 P3 (21-30)
        "menu_sv_castles_p4",      # 21: 1521 城堡 P4 (31-40)
        "menu_sv_villages_p1",     # 22: 1521 村庄 P1 (1-10)
        "menu_sv_villages_p2",     # 23: 1521 村庄 P2 (11-20)
        "menu_sv_villages_p3",     # 24: 1521 村庄 P3 (21-30)
        "menu_sv_villages_p4",     # 25: 1521 村庄 P4 (31-40)
        "menu_sv_villages_p5",     # 26: 1521 村庄 P5 (41-50)
        "menu_sv_villages_p6",     # 27: 1521 村庄 P6 (51-60)
        "menu_sv_villages_p7",     # 28: 1521 村庄 P7 (61-70)
        "menu_sv_villages_p8",     # 29: 1521 村庄 P8 (71-80)
        "menu_sv_villages_p9",     # 30: 1521 村庄 P9 (81-90)
    ]
    menu_id_to_idx = {mid: base_menu_idx + i for i, mid in enumerate(menu_catalog)}

    def mval(mid):
        return tag_val(TAG_MENU, menu_id_to_idx[mid])

    # 4. 辅助函数：构造菜单跳转选项与场景进入选项
    def make_menu_jump_opt(opt_id, opt_text, target_menu_id):
        return f" mno_{opt_id}  0  {opt_text}  1 2060 1 {mval(target_menu_id)}  . \n"

    def make_scene_jump_opt(opt_id, opt_text, scene_id, return_menu_id):
        if scene_id not in scene_to_idx:
            raise ValueError(f"场景 {scene_id} 未在 scenes.txt 中找到！")
        s_idx = scene_to_idx[scene_id]
        s_val = tag_val(TAG_SCENE, s_idx)
        mst_val = tag_val(TAG_MST, 0) # mst_town_default
        ret_val = mval(return_menu_id)
        # (set_passage_menu, return_menu), (set_jump_mission, mst_town_default), (jump_to_scene, scene), (change_screen_mission)
        return f" mno_{opt_id}  0  {opt_text}  4 1304 1 {ret_val} 1911 1 {mst_val} 1910 1 {s_val} 2048 0  . \n"

    new_menus_txt = []
    cns_entries = {}

    # =============================================================
    # Menu 0: menu_scene_viewer (Main Hub)
    # =============================================================
    m0_id = "menu_scene_viewer"
    m0_text = "Scene_Viewer_Showroom:_Enter_any_settlement_or_hidden_realm._(Press_TAB_to_return)"
    m0_opts = [
        make_menu_jump_opt("sv_to_undead", "1._Undead_City_&_Erebus_Netherworld_(The_Unknown)...", "menu_sv_undead_city"),
        make_menu_jump_opt("sv_to_redlist", "2._[RED_LIST]_Mechanism_Settlements_(35_Scenes_Must_Audit)...", "menu_sv_redlist"),
        make_menu_jump_opt("sv_to_dungeons", "3._Town_&_Village_Catacombs_/_Secret_Basements_/_Reliquaries...", "menu_sv_dungeons"),
        make_menu_jump_opt("sv_to_secrets", "4._S&S_Mythic_Realms_&_Secret_Dimensions_(19_Locations)...", "menu_sv_secrets_1"),
        make_menu_jump_opt("sv_to_zendar_inn", "5._Old_Zendar_&_Four_Ways_Inn_Complex...", "menu_sv_zendar_inn"),
        make_menu_jump_opt("sv_to_towns", "6._1521_Historical_Towns_Street_View_(18_Cities)...", "menu_sv_towns_p1"),
        make_menu_jump_opt("sv_to_castles", "7._1521_Historical_Castles_&_Fortresses_(40_Strongholds)...", "menu_sv_castles_p1"),
        make_menu_jump_opt("sv_to_villages", "8._1521_Historical_Villages_&_Camps_(90_Settlements)...", "menu_sv_villages_p1"),
        # 【关键修复】使用 2040 (change_screen_return) 正常返回报告/营地/大地图，绝不使用 2055 (change_screen_quit)
        " mno_sv_main_back  0  Back_to_Reports_/_Camp_Menu.  1 2040 0  . \n"
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
    cns_entries["mno_sv_main_back"] = "返回报告菜单 / 营地界面。"

    # =============================================================
    # Menu 1: menu_sv_undead_city (★ 亡灵城与冥府维度 - 9 个场景全嵌套)
    # =============================================================
    m1_id = "menu_sv_undead_city"
    m1_text = "Undead_City_&_Erebus_Netherworld_(The_Unknown):_Select_a_sub-scene_to_enter._(Press_TAB_to_return)"
    undead_sub_scenes = [
        ("sv_uc_center", "1._Center_Square_&_Blood_Fountain", "scn_town_19_center", "亡灵城·中心广场与主街道 (scn_town_19_center) 【机制: 喷血池/拉斯普京/筛盐场】"),
        ("sv_uc_castle", "2._Lord_Hall_&_Typhon_Throne", "scn_town_19_castle", "亡灵城·领主大厅 (scn_town_19_castle) 【机制: 万魔之父堤丰王座】"),
        ("sv_uc_tavern", "3._Netherworld_Tavern", "scn_town_19_tavern", "亡灵城·冥府酒馆 (scn_town_19_tavern) 【机制: 亡灵之饮与死灵客】"),
        ("sv_uc_store", "4._Necro_Workshop_&_Store", "scn_town_19_store", "亡灵城·死灵工坊与商铺 (scn_town_19_store) 【机制: 棉花糖坩埚】"),
        ("sv_uc_arena", "5._Netherworld_Arena", "scn_town_19_arena", "亡灵城·冥府角斗场 (scn_town_19_arena) 【机制: 白骨决斗】"),
        ("sv_uc_prison", "6._Netherworld_Dungeon_Prison", "scn_town_19_prison", "亡灵城·冥府地牢 (scn_town_19_prison) 【机制: 冥河死囚牢】"),
        ("sv_uc_walls", "7._Siege_Walls_Defense", "scn_town_19_walls", "亡灵城·攻城防线城墙 (scn_town_19_walls) 【机制: 亡灵城防体系】"),
        ("sv_uc_alley", "8._Nether_Dark_Alley", "scn_town_19_alley", "亡灵城·暗巷街道 (scn_town_19_alley) 【机制: 潜行暗巷】"),
        ("sv_uc_fates", "9._Temple_of_the_Fates", "scn_necropolis_fates", "冥府腹地·命运三女神神殿 (scn_necropolis_fates) 【机制: 死灵飞升圣地】")
    ]
    m1_opts = [
        # 顶部始终是返回上级菜单按钮
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
        make_menu_jump_opt("sv_rl_go_vil1", "3._Red-List_Villages_Part_1_(9_Villages:_Csepel,_Mohacs,_Limnos...)...", "menu_sv_rl_vil1"),
        make_menu_jump_opt("sv_rl_go_vil2", "4._Red-List_Villages_Part_2_(8_Villages:_Kozloduy_Underworld,_Snagov...)...", "menu_sv_rl_vil2"),
        make_menu_jump_opt("sv_rl_go_all_p1", "5._Sequential_Walk-through_ALL_35_Scenes_(Page_1/4)...", "menu_sv_rl_all_p1"),
    ]
    new_menus_txt.append(f"{m2_id} 0 {m2_text} none 0 {len(m2_opts)}\n" + "".join(m2_opts))
    cns_entries[m2_id] = "【红名单】S&S 专属机制聚落场景专区：这 35 个场景包含硬编码的机关物件、暗门或特殊出生点，替换场景前必须核查！"
    cns_entries["mno_sv_rl_back_hub"] = "【返回场景查看器主目录】"
    cns_entries["mno_sv_rl_go_towns_p1"] = "1. 城镇红名单场景（12 座城镇 / 13 个场景：贝尔格莱德街道/酒馆、布达杂货铺、萨格勒布监狱等）..."
    cns_entries["mno_sv_rl_go_castles"] = "2. 城堡红名单场景（5 座要塞：斯梅代雷沃蛇桩、布兰/胡内多阿拉/维丁大厅等）..."
    cns_entries["mno_sv_rl_go_vil1"] = "3. 村庄红名单场景 第一部分（9 个村庄：利姆诺斯波塞冬神殿、哈采格象棋塔、切佩尔等）..."
    cns_entries["mno_sv_rl_go_vil2"] = "4. 村庄红名单场景 第二部分（8 个村庄：科兹洛杜伊冥府大门、斯纳戈夫金甲虫、图尔努等）..."
    cns_entries["mno_sv_rl_go_all_p1"] = "5. 顺序遍历全 35 个红名单场景（全 4 页无缝走查）..."

    # 35 红名单场景数据源
    red_towns = [
        ("rlt_1", "Belgrade_Street_(Chest)", "scn_town_7_center", "贝尔格莱德街道 (Belgrade) 【机制: 箱子与出生点】"),
        ("rlt_2", "Belgrade_Tavern_(Passage_&_Entry_16)", "scn_town_7_tavern", "贝尔格莱德酒馆 (Belgrade) 【机制: 密道与 16 号出生点】"),
        ("rlt_3", "Buda_Store_(Cask_of_Amontillado)", "scn_town_6_store", "布达杂货铺 (Buda) 【机制: 阿蒙蒂亚度酒桶暗道】"),
        ("rlt_4", "Klausenburg_Street_(Chest)", "scn_town_5_center", "克劳森堡街道 (Kolozsvar) 【机制: 箱子与出生点】"),
        ("rlt_5", "Zagreb_Prison_(13th_Step_Door)", "scn_town_15_prison", "萨格勒布地牢 (Zagreb) 【机制: 第 13 级台阶暗门】"),
        ("rlt_6", "Brasov_Tavern_(13th_Step_Door)", "scn_town_15_tavern", "布拉索夫酒馆 (Kronstadt) 【机制: 第 13 级台阶暗门】"),
        ("rlt_7", "Constanta_Street_(Special_Entry_8)", "scn_town_12_center", "康斯坦察街道 (Braila) 【机制: 8 号特殊出生点】"),
        ("rlt_8", "Varna_Street_(Special_Entry_8)", "scn_town_13_center", "瓦尔纳街道 (Akkerman) 【机制: 8 号特殊出生点】"),
        ("rlt_9", "Nis_Street_(Large_Chest)", "scn_town_14_center", "尼什街道 (Edirne) 【机制: 大箱子】"),
        ("rlt_10", "Sofia_Castle_(13th_Step_Door)", "scn_town_17_castle", "索非亚领主大厅 (Sofia) 【机制: 第 13 级台阶暗门】"),
        ("rlt_11", "Plovdiv_Street_(Special_Entry_8)", "scn_town_16_center", "普罗夫迪夫街道 (Szeged) 【机制: 8 号特殊出生点】"),
        ("rlt_12", "Edirne_Tavern_(Purloined_Letter)", "scn_town_14_tavern", "埃迪尔内酒馆 (Edirne) 【机制: 被窃的信件】"),
        ("rlt_13", "Constantinople_Street_(Venus)", "scn_town_10_center", "君士坦丁堡街道 (Constantinople) 【机制: 维纳斯暗门】"),
    ]

    red_castles = [
        ("rlc_1", "Szepes_Prison_(Entry_1)", "scn_castle_1_prison", "斯皮什要塞地牢 (Bran) 【机制: 1 号出生点】"),
        ("rlc_2", "Smederevo_Exterior_(Snake_Dummy)", "scn_castle_3_exterior", "斯梅代雷沃要塞 (Hotin) 【机制: 蛇假人与地牢口】"),
        ("rlc_3", "Bran_Interior_(Special_Entry_3)", "scn_castle_1_interior", "布兰城堡领主大厅 (Bran) 【机制: 3 号特殊出生点】"),
        ("rlc_4", "Hunedoara_Interior_(Special_Entry_3)", "scn_castle_9_interior", "胡内多阿拉城堡领主大厅 (Hunedoara) 【机制: 3 号特殊出生点】"),
        ("rlc_5", "Vidin_Interior_(Special_Entry_3)", "scn_castle_11_interior", "维丁城堡领主大厅 (Severin) 【机制: 3 号特殊出生点】"),
    ]

    red_villages = [
        ("rlv1_1", "Csepel_Village_(Sheriff_Arrow_&_Chest)", "scn_village_1", "切佩尔村 (Csepel) 【机制: 郡长之箭与箱子】"),
        ("rlv1_2", "Mohacs_Village_(Special_Entry_5)", "scn_village_2", "摩哈赤村 (Mohacs) 【机制: 5 号特殊出生点】"),
        ("rlv1_3", "Hateg_Village_(Chess_Tower)", "scn_village_17", "哈采格村 (Hateg) 【机制: 象棋塔机关】"),
        ("rlv1_4", "Varanno_Village_(Special_Entry_5)", "scn_village_22", "瓦兰诺村 (Varanno) 【机制: 5 号特殊出生点】"),
        ("rlv1_5", "Dobra_Village_(Special_Entry_5)", "scn_village_24", "多布拉村 (Dobra) 【机制: 5 号特殊出生点】"),
        ("rlv1_6", "Rimetea_Village_(Witch_Hut)", "scn_village_28", "托罗茨科村 (Rimetea) 【机制: 女巫小屋】"),
        ("rlv1_7", "Limnos_Village_(Poseidon_Ruins_&_Shell)", "scn_village_32", "利姆诺斯村 (Limnos) 【机制: 波塞冬神殿遗迹与海螺】"),
        ("rlv1_8", "Kladovo_Village_(Special_Entry_5)", "scn_village_34", "克拉多沃村 (Kladovo) 【机制: 5 号特殊出生点】"),
        ("rlv1_9", "Vranje_Village_(Special_Entry_5)", "scn_village_36", "弗拉涅村 (Vranje) 【机制: 5 号特殊出生点】"),
        ("rlv2_1", "Kozloduy_Village_(Underworld_Gate)", "scn_village_37", "科兹洛杜伊村 (Kozloduy) 【机制: 冥府大门与冥河渡船】"),
        ("rlv2_2", "Rozaje_Village_(Special_Entry_5)", "scn_village_44", "罗扎耶村 (Rozaje) 【机制: 5 号特殊出生点】"),
        ("rlv2_3", "Strumica_Village_(Special_Entry_5)", "scn_village_45", "斯特鲁米察村 (Strumica) 【机制: 5 号特殊出生点】"),
        ("rlv2_4", "Kavala_Village_(Special_Entry_5)", "scn_village_46", "卡瓦拉村 (Kavala) 【机制: 5 号特殊出生点】"),
        ("rlv2_5", "Snagov_Village_(Gold_Bug)", "scn_village_53", "斯纳戈夫村 (Snagov) 【机制: 金甲虫机关】"),
        ("rlv2_6", "Turnu_Village_(Annabelle_Tomb)", "scn_village_54", "图尔努村 (Turnu) 【机制: 安娜贝尔墓碑】"),
        ("rlv2_7", "Ruse_Village_(Special_Entry_5)", "scn_village_56", "鲁塞村 (Ruse) 【机制: 5 号特殊出生点】"),
        ("rlv2_8", "Razgrad_Village_(Special_Entry_5)", "scn_village_58", "拉兹格勒村 (Razgrad) 【机制: 5 号特殊出生点】"),
    ]

    # Menu 3: menu_sv_rl_towns_p1 (7 场景)
    m3_id = "menu_sv_rl_towns_p1"
    m3_opts = [
        make_menu_jump_opt("sv_rlt1_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
    ]
    for oid, olabel, scn, cn_txt in red_towns[:7]:
        m3_opts.append(make_scene_jump_opt(oid, olabel, scn, m3_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    m3_opts.append(make_menu_jump_opt("sv_rlt1_next", "Next_Page_(Towns_8-13)...", "menu_sv_rl_towns_p2"))
    new_menus_txt.append(f"{m3_id} 0 Red-List_Towns_P1_(Scenes_1-7):_Select_a_scene_to_enter none 0 {len(m3_opts)}\n" + "".join(m3_opts))
    cns_entries[m3_id] = "红名单城镇场景 第 1 页（共 7 处）：点击即可立即传送进入实机巡查，按 TAB 键原路返回。"
    cns_entries["mno_sv_rlt1_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlt1_next"] = "下一页：城镇红名单 第 8-13 项..."

    # Menu 4: menu_sv_rl_towns_p2 (6 场景)
    m4_id = "menu_sv_rl_towns_p2"
    m4_opts = [
        make_menu_jump_opt("sv_rlt2_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
        make_menu_jump_opt("sv_rlt2_prev", "Previous_Page_(Towns_1-7)...", "menu_sv_rl_towns_p1"),
    ]
    for oid, olabel, scn, cn_txt in red_towns[7:]:
        m4_opts.append(make_scene_jump_opt(oid, olabel, scn, m4_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m4_id} 0 Red-List_Towns_P2_(Scenes_8-13):_Select_a_scene_to_enter none 0 {len(m4_opts)}\n" + "".join(m4_opts))
    cns_entries[m4_id] = "红名单城镇场景 第 2 页（共 6 处）：点击即可立即传送进入实机巡查，按 TAB 键原路返回。"
    cns_entries["mno_sv_rlt2_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlt2_prev"] = "上一页：城镇红名单 第 1-7 项..."

    # Menu 5: menu_sv_rl_castles (5 场景)
    m5_id = "menu_sv_rl_castles"
    m5_opts = [
        make_menu_jump_opt("sv_rlc_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
    ]
    for oid, olabel, scn, cn_txt in red_castles:
        m5_opts.append(make_scene_jump_opt(oid, olabel, scn, m5_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m5_id} 0 Red-List_Castles_(5_Scenes):_Select_a_scene_to_enter none 0 {len(m5_opts)}\n" + "".join(m5_opts))
    cns_entries[m5_id] = "红名单城堡要塞场景（共 5 处）：点击即可立即传送进入实机巡查，按 TAB 键原路返回。"
    cns_entries["mno_sv_rlc_back"] = "【返回红名单分类菜单】"

    # Menu 6: menu_sv_rl_vil1 (9 场景)
    m6_id = "menu_sv_rl_vil1"
    m6_opts = [
        make_menu_jump_opt("sv_rlv1_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
    ]
    for oid, olabel, scn, cn_txt in red_villages[:9]:
        m6_opts.append(make_scene_jump_opt(oid, olabel, scn, m6_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    m6_opts.append(make_menu_jump_opt("sv_rlv1_next", "Next_Page_(Villages_10-17)...", "menu_sv_rl_vil2"))
    new_menus_txt.append(f"{m6_id} 0 Red-List_Villages_Part_1_(9_Villages):_Select_a_scene none 0 {len(m6_opts)}\n" + "".join(m6_opts))
    cns_entries[m6_id] = "红名单村庄场景 第一部分（9 处）：包含波塞冬神殿、象棋塔、警长之箭等特殊机关。"
    cns_entries["mno_sv_rlv1_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlv1_next"] = "下一页：村庄红名单 第二部分..."

    # Menu 7: menu_sv_rl_vil2 (8 场景)
    m7_id = "menu_sv_rl_vil2"
    m7_opts = [
        make_menu_jump_opt("sv_rlv2_back", "[Back_to_Red-List_Hub]", "menu_sv_redlist"),
        make_menu_jump_opt("sv_rlv2_prev", "Previous_Page_(Villages_1-9)...", "menu_sv_rl_vil1"),
    ]
    for oid, olabel, scn, cn_txt in red_villages[9:]:
        m7_opts.append(make_scene_jump_opt(oid, olabel, scn, m7_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m7_id} 0 Red-List_Villages_Part_2_(8_Villages):_Select_a_scene none 0 {len(m7_opts)}\n" + "".join(m7_opts))
    cns_entries[m7_id] = "红名单村庄场景 第二部分（8 处）：包含冥府大门与冥河渡船、金甲虫、安娜贝尔墓碑等。"
    cns_entries["mno_sv_rlv2_back"] = "【返回红名单分类菜单】"
    cns_entries["mno_sv_rlv2_prev"] = "上一页：村庄红名单 第一部分..."

    # 35 红名单全场景顺序平铺走查 (分成 4 页，每页 8-9 项，完全无遮挡)
    all_35 = red_towns + red_castles + red_villages
    rl_pages = [
        ("menu_sv_rl_all_p1", all_35[0:9], None, "menu_sv_rl_all_p2", "红名单全场景走查 第 1 页 (01-09: 城镇街景与酒馆)"),
        ("menu_sv_rl_all_p2", all_35[9:18], "menu_sv_rl_all_p1", "menu_sv_rl_all_p3", "红名单全场景走查 第 2 页 (10-18: 城镇与全部城堡)"),
        ("menu_sv_rl_all_p3", all_35[18:27], "menu_sv_rl_all_p2", "menu_sv_rl_all_p4", "红名单全场景走查 第 3 页 (19-27: 村庄特殊机关 P1)"),
        ("menu_sv_rl_all_p4", all_35[27:35], "menu_sv_rl_all_p3", None, "红名单全场景走查 第 4 页 (28-35: 村庄特殊机关 P2)"),
    ]
    for p_id, p_items, prev_m, next_m, p_cn in rl_pages:
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
        new_menus_txt.append(f"{p_id} 0 {p_id}:_Sequential_Walk-through none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = p_cn
        cns_entries[f"mno_{p_id}_back"] = "【返回红名单总目录】"
        if prev_m:
            cns_entries[f"mno_{p_id}_prev"] = "上一页..."
        if next_m:
            cns_entries[f"mno_{p_id}_next"] = "下一页..."

    # =============================================================
    # Menu 12: menu_sv_dungeons (聚落隐藏地下室/地宫/圣物室 - 7 场景)
    # =============================================================
    m12_id = "menu_sv_dungeons"
    dungeon_scenes = [
        ("sv_dg_buda", "1._Buda_Catacombs_(Ossuary_Secret_Tunnel)", "scn_town_6_catacombs", "1. 布达地下墓穴 (scn_town_6_catacombs) 【机制: 藏骸所与骷髅秘道】"),
        ("sv_dg_jassy", "2._Jassy_Basement_(Cask_of_Amontillado)", "scn_town_9_basement", "2. 雅西秘密地窖 (scn_town_9_basement) 【机制: 阿蒙蒂亚度酒桶】"),
        ("sv_dg_edirne_rel", "3._Edirne_Reliquary_(Holy_Relic_Room)", "scn_town_14_reliquary", "3. 埃迪尔内圣物室 (scn_town_14_reliquary) 【机制: 圣物陈列室】"),
        ("sv_dg_edirne_nik", "4._Edirne_Nikola_Underground_Sanctuary", "scn_town_14_reliquary_nikola", "4. 埃迪尔内尼古拉地下圣所 (scn_town_14_reliquary_nikola) 【机制: 尼古拉密室】"),
        ("sv_dg_vil67", "5._Village_Hermit_Cave", "scn_village_67_cave", "5. 村庄隐者秘洞 (scn_village_67_cave) 【机制: 洞穴藏身处】"),
        ("sv_dg_vil43", "6._Village_Ancient_Tomb", "scn_village_43_tomb", "6. 村庄古代墓穴 (scn_village_43_tomb) 【机制: 地底墓穴】"),
        ("sv_dg_dhorak", "7._Dhorak_Keep_Underground", "scn_dhorak_keep", "7. 多拉克要塞地宫 (scn_dhorak_keep) 【机制: 废弃古要塞】"),
    ]
    m12_opts = [
        make_menu_jump_opt("sv_dg_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
    ]
    for oid, olabel, scn, cn_txt in dungeon_scenes:
        m12_opts.append(make_scene_jump_opt(oid, olabel, scn, m12_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m12_id} 0 Town_&_Village_Dungeons_/_Catacombs:_Select_a_scene none 0 {len(m12_opts)}\n" + "".join(m12_opts))
    cns_entries[m12_id] = "【地下城与密室】聚落地下墓穴/秘密地窖/圣物室：布达地下墓穴、雅西阿蒙蒂亚度酒窖、埃迪尔内圣物室/尼古拉密室、村庄古代墓穴等隐藏空间。按 TAB 键原路返回。"
    cns_entries["mno_sv_dg_back"] = "【返回场景查看器主目录】"

    # =============================================================
    # Menu 13 & 14: menu_sv_secrets_1 & 2 (S&S 专属异次元秘境 - 19 处)
    # =============================================================
    secrets_p1 = [
        ("sv_sec1_1", "1._Salt_Mine_(Abandoned)", "scn_salt_mine", "1. 喀尔巴阡废弃盐矿 (scn_salt_mine)"),
        ("sv_sec1_2", "2._Clockwork_Salt_Cave", "scn_salt_cave", "2. 大巧匠发条盐洞 (scn_salt_cave)"),
        ("sv_sec1_3", "3._Barter_Town_Market", "scn_barter_town", "3. 巴特镇黑市地面 (scn_barter_town)"),
        ("sv_sec1_4", "4._Barter_Town_Smuggling_Cellar", "scn_barter_town_cellar", "4. 巴特镇地下走私地窖 (scn_barter_town_cellar)"),
        ("sv_sec1_5", "5._Antiquities_Museum", "scn_museum", "5. 古物博物馆 (22幅秘境挂毯大厅) (scn_museum)"),
        ("sv_sec1_6", "6._Cretan_Minotaur_Labyrinth", "scn_cretanlabyrinth", "6. 克里特牛头人迷宫 (scn_cretanlabyrinth)"),
        ("sv_sec1_7", "7._Nightmare_Realm", "scn_nightmarerealm", "7. 噩梦维度 (scn_nightmarerealm)"),
        ("sv_sec1_8", "8._Leviathan_Whalebelly", "scn_whalebelly", "8. 利维坦鲸腹 (scn_whalebelly)"),
    ]
    m13_id = "menu_sv_secrets_1"
    m13_opts = [
        make_menu_jump_opt("sv_sec1_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
    ]
    for oid, olabel, scn, cn_txt in secrets_p1:
        m13_opts.append(make_scene_jump_opt(oid, olabel, scn, m13_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    m13_opts.append(make_menu_jump_opt("sv_sec1_next", "Next_Page_(Secrets_9-19)...", "menu_sv_secrets_2"))
    new_menus_txt.append(f"{m13_id} 0 S&S_Mythic_Realms_Part_1:_Select_a_scene none 0 {len(m13_opts)}\n" + "".join(m13_opts))
    cns_entries[m13_id] = "S&S 专属大地图秘境与隐藏维度 第一部分（8 处）：盐矿、发条盐洞、巴特镇、迷宫、噩梦维度、鲸腹等。"
    cns_entries["mno_sv_sec1_back"] = "【返回场景查看器主目录】"
    cns_entries["mno_sv_sec1_next"] = "下一页：S&S 秘境维度 第 9-19 处..."

    secrets_p2 = [
        ("sv_sec2_1", "9._Green_Meteorite_Crater", "scn_greenmeteorite", "9. 绿陨石坠落坑 (scn_greenmeteorite)"),
        ("sv_sec2_2", "10._Fairy_Realm", "scn_fairyrealm", "10. 妖精国度 (scn_fairyrealm)"),
        ("sv_sec2_3", "11._Pressburg_Sherwood_Forest", "scn_sherwood", "11. 罗宾汉Pressburg绿林 (scn_sherwood)"),
        ("sv_sec2_4", "12._Thieves_Den_Camp", "scn_sherwood2", "12. 盗贼密林营地 (scn_sherwood2)"),
        ("sv_sec2_5", "13._Usherwood_Dead_Forest", "scn_village_4_usherwood", "13. 厄舍庄园枯木林 (scn_village_4_usherwood)"),
        ("sv_sec2_6", "14._Usher_Mansion_Interior", "scn_village_4_mansion", "14. 厄舍庄园古宅室内 (scn_village_4_mansion)"),
        ("sv_sec2_7", "15._Hiraeth_Homestead_Exterior", "scn_homestead", "15. 故园庄园外景 (scn_homestead)"),
        ("sv_sec2_8", "16._Hiraeth_Homestead_Interior", "scn_interior_homestead", "16. 故园古宅室内 (scn_interior_homestead)"),
        ("sv_sec2_9", "17._Ivory_Temple", "scn_ivory_temple", "17. 象牙神殿 (scn_ivory_temple)"),
        ("sv_sec2_10", "18._Fallen_Antihero_Altar", "scn_fallenantihero", "18. 堕落反英雄祭坛 (scn_fallenantihero)"),
        ("sv_sec2_11", "19._Heartbearer_Tomb", "scn_heartbearer_tomb", "19. 持心者之墓 (scn_heartbearer_tomb)"),
    ]
    m14_id = "menu_sv_secrets_2"
    m14_opts = [
        make_menu_jump_opt("sv_sec2_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer"),
        make_menu_jump_opt("sv_sec2_prev", "Previous_Page_(Secrets_1-8)...", "menu_sv_secrets_1")
    ]
    for oid, olabel, scn, cn_txt in secrets_p2:
        m14_opts.append(make_scene_jump_opt(oid, olabel, scn, m14_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m14_id} 0 S&S_Mythic_Realms_Part_2:_Select_a_scene none 0 {len(m14_opts)}\n" + "".join(m14_opts))
    cns_entries[m14_id] = "S&S 专属大地图秘境与隐藏维度 第二部分（11 处）：绿陨石、妖精国度、罗宾汉绿林、厄舍古宅、故园、象牙神殿等。"
    cns_entries["mno_sv_sec2_back"] = "【返回场景查看器主目录】"
    cns_entries["mno_sv_sec2_prev"] = "上一页：S&S 秘境维度 第 1-8 处..."

    # =============================================================
    # Menu 15: menu_sv_zendar_inn (旧曾扎尔与四方客栈 - 7 场景)
    # =============================================================
    m15_id = "menu_sv_zendar_inn"
    zendar_scenes = [
        ("sv_zi_center", "1._Old_Zendar_Center_Square", "scn_zendar_center", "1. 旧曾扎尔·城镇中心广场 (scn_zendar_center)"),
        ("sv_zi_arena", "2._Old_Zendar_Arena", "scn_zendar_arena", "2. 旧曾扎尔·古典角斗场 (scn_zendar_arena)"),
        ("sv_zi_merchant", "3._Old_Zendar_Merchant_Market", "scn_zendar_merchant", "3. 旧曾扎尔·商铺市场 (scn_zendar_merchant)"),
        ("sv_zi_reliquary", "4._Old_Zendar_Reliquary", "scn_zendar_reliquary", "4. 旧曾扎尔·秘密圣物室 (scn_zendar_reliquary)"),
        ("sv_zi_fwi", "5._Four_Ways_Inn_Exterior", "scn_four_ways_inn", "5. 四方客栈·外景 (scn_four_ways_inn)"),
        ("sv_zi_boar", "6._The_Happy_Boar_Tavern", "scn_the_happy_boar", "6. 四方客栈·快乐公猪酒馆 (scn_the_happy_boar)"),
        ("sv_zi_cellar", "7._Four_Ways_Inn_Smugglers_Cellar", "scn_four_ways_inn_cellar", "7. 四方客栈·地下走私地窖 (scn_four_ways_inn_cellar)"),
    ]
    m15_opts = [
        make_menu_jump_opt("sv_zi_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
    ]
    for oid, olabel, scn, cn_txt in zendar_scenes:
        m15_opts.append(make_scene_jump_opt(oid, olabel, scn, m15_id))
        cns_entries[f"mno_{oid}"] = cn_txt
    new_menus_txt.append(f"{m15_id} 0 Old_Zendar_&_Four_Ways_Inn:_Select_a_scene none 0 {len(m15_opts)}\n" + "".join(m15_opts))
    cns_entries[m15_id] = "【旧曾扎尔与四方客栈】古典废墟与快乐公猪客栈复合体：曾扎尔广场/角斗场/市场/圣物室，四方客栈外景/快乐公猪酒馆/地下地窖。按 TAB 原路返回。"
    cns_entries["mno_sv_zi_back"] = "【返回场景查看器主目录】"

    # =============================================================
    # Menu 16 & 17: 1521 历史城镇街道 (全 18 城，分为 2 页，每页 9 城)
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
    # P1: 1-9
    m16_id = "menu_sv_towns_p1"
    m16_opts = [
        make_menu_jump_opt("sv_tw1_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
    ]
    for tid, tname, scn in town_names_1521[:9]:
        oid = f"sv_tw_{tid}"
        m16_opts.append(make_scene_jump_opt(oid, f"{tid}._{tname.split()[0]}", scn, m16_id))
        cns_entries[f"mno_{oid}"] = f"{tid}. {tname}"
    m16_opts.append(make_menu_jump_opt("sv_tw1_next", "Next_Page_(Towns_10-18)...", "menu_sv_towns_p2"))
    new_menus_txt.append(f"{m16_id} 0 1521_Historical_Towns_P1_(1-9):_Select_a_town_street none 0 {len(m16_opts)}\n" + "".join(m16_opts))
    cns_entries[m16_id] = "1521 历史城镇街道展厅 第 1 页（第 1-9 座城市街道外景）：实机漫步巡查。"
    cns_entries["mno_sv_tw1_back"] = "【返回场景查看器主目录】"
    cns_entries["mno_sv_tw1_next"] = "下一页：城镇街道 第 10-18 座..."

    # P2: 10-18
    m17_id = "menu_sv_towns_p2"
    m17_opts = [
        make_menu_jump_opt("sv_tw2_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer"),
        make_menu_jump_opt("sv_tw2_prev", "Previous_Page_(Towns_1-9)...", "menu_sv_towns_p1"),
    ]
    for tid, tname, scn in town_names_1521[9:]:
        oid = f"sv_tw_{tid}"
        m17_opts.append(make_scene_jump_opt(oid, f"{tid}._{tname.split()[0]}", scn, m17_id))
        cns_entries[f"mno_{oid}"] = f"{tid}. {tname}"
    new_menus_txt.append(f"{m17_id} 0 1521_Historical_Towns_P2_(10-18):_Select_a_town_street none 0 {len(m17_opts)}\n" + "".join(m17_opts))
    cns_entries[m17_id] = "1521 历史城镇街道展厅 第 2 页（第 10-18 座城市街道外景）：实机漫步巡查。"
    cns_entries["mno_sv_tw2_back"] = "【返回场景查看器主目录】"
    cns_entries["mno_sv_tw2_prev"] = "上一页：城镇街道 第 1-9 座..."

    # =============================================================
    # Menu 18..21: 1521 历史城堡外景 (全 40 城堡，分为 4 页，每页 10 堡)
    # =============================================================
    castle_pages = [
        ("menu_sv_castles_p1", 1, 10, None, "menu_sv_castles_p2", "1521 历史城堡要塞 第 1 页 (01-10)"),
        ("menu_sv_castles_p2", 11, 20, "menu_sv_castles_p1", "menu_sv_castles_p3", "1521 历史城堡要塞 第 2 页 (11-20)"),
        ("menu_sv_castles_p3", 21, 30, "menu_sv_castles_p2", "menu_sv_castles_p4", "1521 历史城堡要塞 第 3 页 (21-30)"),
        ("menu_sv_castles_p4", 31, 40, "menu_sv_castles_p3", None, "1521 历史城堡要塞 第 4 页 (31-40)"),
    ]
    for p_id, start_c, end_c, prev_m, next_m, p_cn in castle_pages:
        p_opts = [
            make_menu_jump_opt(f"{p_id}_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
        ]
        if prev_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_prev", "Previous_Page...", prev_m))
        for c in range(start_c, end_c + 1):
            sid = f"scn_castle_{c}_exterior"
            oid = f"sv_cas_{c}"
            p_opts.append(make_scene_jump_opt(oid, f"{c}._Castle_{c}_Exterior", sid, p_id))
            cns_entries[f"mno_{oid}"] = f"{c}. 城堡要塞外景 {sid}"
        if next_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_next", "Next_Page...", next_m))
        new_menus_txt.append(f"{p_id} 0 {p_id}:_Select_a_castle_exterior none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = p_cn
        cns_entries[f"mno_{p_id}_back"] = "【返回场景查看器主目录】"
        if prev_m:
            cns_entries[f"mno_{p_id}_prev"] = "上一页城堡列表..."
        if next_m:
            cns_entries[f"mno_{p_id}_next"] = "下一页城堡列表..."

    # =============================================================
    # Menu 22..30: 1521 历史村庄聚落 (全 90 村庄，分为 9 页，每页 10 村)
    # =============================================================
    for p in range(9):
        p_id = f"menu_sv_villages_p{p+1}"
        start_v = p * 10 + 1
        end_v = (p + 1) * 10
        prev_m = f"menu_sv_villages_p{p}" if p > 0 else None
        next_m = f"menu_sv_villages_p{p+2}" if p < 8 else None
        
        p_opts = [
            make_menu_jump_opt(f"{p_id}_back", "[Back_to_Scene_Viewer_Hub]", "menu_scene_viewer")
        ]
        if prev_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_prev", "Previous_Page...", prev_m))
        for v in range(start_v, end_v + 1):
            sid = f"scn_village_{v}"
            oid = f"sv_vil_{v}"
            p_opts.append(make_scene_jump_opt(oid, f"{v}._Village_{v}", sid, p_id))
            cns_entries[f"mno_{oid}"] = f"{v}. 村庄场景 {sid}"
        if next_m:
            p_opts.append(make_menu_jump_opt(f"{p_id}_next", "Next_Page...", next_m))
            
        new_menus_txt.append(f"{p_id} 0 {p_id}:_Select_a_village none 0 {len(p_opts)}\n" + "".join(p_opts))
        cns_entries[p_id] = f"1521 历史村庄聚落 第 {p+1} 页（第 {start_v}-{end_v} 个村庄场景巡查）"
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

    # 如果还没注入过 mno_scene_viewer
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
        # 修正原有的 menu_val
        full_content = re.sub(r'mno_scene_viewer\s+0\s+View_scenes_and_locations\.\s+1\s+2060\s+1\s+\d+', f'mno_scene_viewer  0  View_scenes_and_locations.  1 2060 1 {mval("menu_scene_viewer")}', full_content)

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

    print("[场景查看器 v2.0 安装完成] 全部组件与入口部署完毕！")

if __name__ == "__main__":
    main()
