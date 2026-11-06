#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade — 场景查看器 (Scene Viewer & Showroom) 安装器
=====================================================================
效法 1866_Ultimate_WB 在 reports 报告菜单与 camp_action 营地动作菜单中建立场景查看器：
  1. 【红名单专区】：包含全部 34 座聚落 / 35 个不能裸覆盖的 S&S 机制场景，支持按城镇、城堡、村庄以及全列表顺序逐一实机核查 (TAB 键随时原路返回菜单)。
  2. 【S&S 秘境专区】：废弃盐矿、大巧匠盐洞、巴特镇黑市与地窖、古物博物馆、童话迷宫、噩梦维度、鲸腹、命运三女神、妖精国度、罗宾汉森林、象牙神殿、故园等 24 处独立秘境。
  3. 【1521 历史城镇/城堡/村庄】：全 18 城镇、40 城堡、90 村庄大地图场景任意传送预览。
  4. 自动同步更新 languages/cns/game_menus.csv 纯正双语汉化。
"""

import os
import sys

MOD_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

TAG_SCENE = 10
TAG_MST = 11
TAG_MENU = 12

def tag_val(tag, idx):
    return (tag << 56) | (idx & 0xFFFFFFFFFFFFFF)

def main():
    print(f"[开始构建场景查看器] 目标模组路径: {MOD_DIR}")
    
    # 1. 读取 scenes.txt 建立 scene_id -> index 字典
    scenes_path = os.path.join(MOD_DIR, "scenes.txt")
    with open(scenes_path, "r", encoding="utf-8", errors="replace") as f:
        scenes = [l.strip().split()[0] for l in f if l.strip().startswith("scn_")]
    scene_to_idx = {s: i for i, s in enumerate(scenes)}
    print(f"  已载入 {len(scenes)} 个场景索引")

    # 2. 读取 menus.txt
    menus_path = os.path.join(MOD_DIR, "menus.txt")
    with open(menus_path, "r", encoding="utf-8", errors="replace") as f:
        menu_lines = f.readlines()

    declared_menus = int(menu_lines[1].strip())
    existing_menus = []
    for l in menu_lines:
        if l.startswith("menu_"):
            existing_menus.append(l.split()[0])
    
    # 如果已经安装过，先提示或回滚
    if "menu_scene_viewer" in existing_menus:
        print("  检测到 menu_scene_viewer 已存在，将执行增量覆盖更新...")
        # 截断到 menu_scene_viewer 之前
        cutoff = -1
        for i, l in enumerate(menu_lines):
            if l.startswith("menu_scene_viewer "):
                cutoff = i
                break
        if cutoff != -1:
            menu_lines = menu_lines[:cutoff]
            # 重新统计原有菜单数
            existing_menus = [l.split()[0] for l in menu_lines if l.startswith("menu_")]
            declared_menus = len(existing_menus)
    
    base_menu_idx = len(existing_menus)
    print(f"  当前基础菜单数: {base_menu_idx}")

    # 3. 定义全部新菜单与页面结构
    # 我们先规划所有新菜单的 id 顺序，方便预先计算 menu_val
    menu_catalog = [
        "menu_scene_viewer",       # base + 0: 主展厅 Hub
        "menu_sv_redlist",         # base + 1: 红名单 Hub
        "menu_sv_rl_towns",        # base + 2: 红名单城镇 (13 场景)
        "menu_sv_rl_castles",      # base + 3: 红名单城堡 (5 场景)
        "menu_sv_rl_vil1",         # base + 4: 红名单村庄 Part 1 (9 场景)
        "menu_sv_rl_vil2",         # base + 5: 红名单村庄 Part 2 (8 场景)
        "menu_sv_rl_all_p1",       # base + 6: 全部红名单顺序走查 P1 (1-18)
        "menu_sv_rl_all_p2",       # base + 7: 全部红名单顺序走查 P2 (19-35)
        "menu_sv_secrets_1",       # base + 8: S&S 秘境 Part 1 (12 处)
        "menu_sv_secrets_2",       # base + 9: S&S 秘境 Part 2 (12 处)
        "menu_sv_towns_list",      # base + 10: 1521 城镇街道 (18 座城)
        "menu_sv_castles_p1",      # base + 11: 1521 城堡 P1 (1-20)
        "menu_sv_castles_p2",      # base + 12: 1521 城堡 P2 (21-40)
        "menu_sv_villages_p1",     # base + 13: 1521 村庄 P1 (1-18)
        "menu_sv_villages_p2",     # base + 14: 1521 村庄 P2 (19-36)
        "menu_sv_villages_p3",     # base + 15: 1521 村庄 P3 (37-54)
        "menu_sv_villages_p4",     # base + 16: 1521 村庄 P4 (55-72)
        "menu_sv_villages_p5",     # base + 17: 1521 村庄 P5 (73-90)
    ]
    menu_id_to_idx = {mid: base_menu_idx + i for i, mid in enumerate(menu_catalog)}

    def mval(mid):
        return tag_val(TAG_MENU, menu_id_to_idx[mid])

    # 红名单 35 个场景数据
    redlist_data = [
        # 13 城镇
        ("scn_town_2_center", "贝尔格莱德街道_(Belgrade_Center)", "Belgrade_Street_(Chest)", "隐藏小木箱"),
        ("scn_town_2_tavern", "贝尔格莱德酒馆_(Belgrade_Tavern)", "Belgrade_Tavern_(Passage_&_Entry_16)", "暗门与出生点16"),
        ("scn_town_3_store", "布达杂货铺_(Buda_Store)", "Buda_Store_(Cask_of_Amontillado)", "阿芒提拉多酒桶 spr_caskofamontillado"),
        ("scn_town_5_center", "克卢日街道_(Klausenburg_Center)", "Klausenburg_Street_(Chest)", "隐藏小木箱"),
        ("scn_town_6_prison", "萨格勒布监狱_(Zagreb_Prison)", "Zagreb_Prison_(13th_Step_Door)", "暗门通往第13阶梯 spr_thirteen"),
        ("scn_town_9_tavern", "布拉索夫酒馆_(Brasov_Tavern)", "Brasov_Tavern_(13th_Step_Door)", "暗门通往第13阶梯 spr_thirteen"),
        ("scn_town_11_center", "康斯坦察街道_(Constanta_Center)", "Constanta_Street_(Special_Entry_8)", "特殊出生点8"),
        ("scn_town_12_center", "瓦尔纳街道_(Varna_Center)", "Varna_Street_(Special_Entry_8)", "特殊出生点8"),
        ("scn_town_13_center", "尼什街道_(Nis_Center)", "Nis_Street_(Large_Chest)", "隐藏大宝箱"),
        ("scn_town_14_castle", "索菲亚城堡大厅_(Sofia_Castle)", "Sofia_Castle_(13th_Step_Door)", "暗门通往第13阶梯 spr_thirteen"),
        ("scn_town_15_center", "普罗夫迪夫街道_(Plovdiv_Center)", "Plovdiv_Street_(Special_Entry_8)", "特殊出生点8"),
        ("scn_town_17_tavern", "埃迪尔内酒馆_(Edirne_Tavern)", "Edirne_Tavern_(Purloined_Letter)", "失窃信件 spr_purloinedletter"),
        ("scn_town_18_center", "君士坦丁堡街道_(Constantinople_Center)", "Constantinople_Street_(Venus)", "米洛的维纳斯 spr_VenusDeMilo"),
        # 5 城堡
        ("scn_castle_12_prison", "斯皮什监狱_(Szepes_Prison)", "Szepes_Prison_(Entry_1)", "特殊出生点1"),
        ("scn_castle_15_exterior", "斯梅代雷沃要塞外景_(Smederevo_Exterior)", "Smederevo_Exterior_(Snake_Dummy)", "蛇模型木人桩 spr_snakedummy"),
        ("scn_castle_24_interior", "布兰城堡大厅_(Bran_Hall)", "Bran_Interior_(Special_Entry_3)", "特殊出生点3"),
        ("scn_castle_25_interior", "胡内多阿拉城堡大厅_(Hunedoara_Hall)", "Hunedoara_Interior_(Special_Entry_3)", "特殊出生点3"),
        ("scn_castle_36_interior", "维丁城堡大厅_(Vidin_Hall)", "Vidin_Interior_(Special_Entry_3)", "特殊出生点3"),
        # 17 村庄
        ("scn_village_4", "切佩尔村庄_(Csepel)", "Csepel_Village_(Sheriff_Arrow_&_Chest)", "警长的箭 + 隐藏小木箱"),
        ("scn_village_5", "摩哈赤村庄_(Mohacs)", "Mohacs_Village_(Special_Entry_5)", "特殊出生点5"),
        ("scn_village_20", "哈采格村庄_(Hateg)", "Hateg_Village_(Chess_Tower)", "国际象棋塔 spr_ChessTower"),
        ("scn_village_25", "瓦劳诺村庄_(Varanno)", "Varanno_Village_(Special_Entry_5)", "特殊出生点5"),
        ("scn_village_27", "多布拉村庄_(Dobra)", "Dobra_Village_(Special_Entry_5)", "特殊出生点5"),
        ("scn_village_31", "里梅泰亚村庄_(Rimetea)", "Rimetea_Village_(Witch_Hut)", "女巫小屋 spr_hut"),
        ("scn_village_35", "利姆诺斯爱琴海岛村_(Limnos)", "Limnos_Village_(Poseidon_Ruins_&_Shell)", "海神波塞冬神殿遗迹与怪异贝壳"),
        ("scn_village_41", "罗日尼亚瓦村庄_(Roznava)", "Roznava_Village_(Special_Entries_6,7)", "特殊出生点6, 7"),
        ("scn_village_43", "加拉茨村庄_(Galati)", "Galati_Village_(Passage_Exit)", "暗门出口"),
        ("scn_village_48", "科兹洛杜伊多瑙河村_(Kozloduy)", "Kozloduy_Village_(Underworld_Gate_&_Boat)", "冥府大门与冥河渡船"),
        ("scn_village_56", "斯纳戈夫村庄_(Snagov)", "Snagov_Village_(Gold_Bug)", "金甲虫 spr_goldbug"),
        ("scn_village_61", "久尔久村庄_(Giurgiu)", "Giurgiu_Village_(Special_Entry_5)", "特殊出生点5"),
        ("scn_village_66", "图尔努村庄_(Turnu)", "Turnu_Village_(Annabelle_Lee_Tomb_&_Chest)", "安娜贝尔墓碑 + 隐藏小木箱"),
        ("scn_village_67", "卡拉法特村庄_(Calafat)", "Calafat_Village_(Passage_Exit)", "暗门出口"),
        ("scn_village_75", "锡利斯特拉村庄_(Silistra)", "Silistra_Village_(Special_Entry_5)", "特殊出生点5"),
        ("scn_village_78", "曼加利亚黑海村庄_(Mangalia)", "Mangalia_Village_(Chest)", "隐藏小木箱"),
        ("scn_village_88", "布勒伊拉多瑙河村_(Braila)", "Braila_Village_(Chest)", "隐藏小木箱"),
    ]

    # S&S 秘境数据
    secret_scenes_data = [
        ("scn_salt_mine", "废弃盐矿大地图入口_(Salt_Mine)", "Salt_Mine_Entrance"),
        ("scn_salt_cave", "发条大巧匠深层盐洞_(Clockwork_Salt_Cave)", "Clockwork_Salt_Cave"),
        ("scn_barter_town", "巴特镇以物易物黑市_(Barter_Town)", "Barter_Town_Market"),
        ("scn_barter_town_cellar", "巴特镇地窖酒馆_(Barter_Town_Cellar)", "Barter_Town_Cellar"),
        ("scn_museum", "古物奇珍陈列博物馆_(Ancient_Museum)", "Ancient_Museum"),
        ("scn_cretanlabyrinth", "克里特童话迷宫_(Cretan_Labyrinth)", "Cretan_Labyrinth"),
        ("scn_nightmarerealm", "噩梦立方体维度_(Nightmare_Realm)", "Nightmare_Realm"),
        ("scn_whalebelly", "利维坦巨鲸腹内决战场_(Whalebelly)", "Whalebelly_Battlefield"),
        ("scn_necropolis_fates", "命运三女神死灵地牢_(Necropolis_Fates)", "Necropolis_Fates_Dungeon"),
        ("scn_fairyrealm", "妖精国度与换子秘境_(Fairy_Realm)", "Fairy_Realm"),
        ("scn_sherwood", "波佐尼多瑙河罗宾汉森林_(Sherwood_Forest)", "Sherwood_Forest"),
        ("scn_sherwood2", "火烧诺丁汉警长大厦_(Sheriff_Residence_Burning)", "Sheriff_Residence_Burning"),
        ("scn_ivory_temple", "象牙神殿_(Ivory_Temple)", "Ivory_Temple"),
        ("scn_homestead", "故园庄园外景_(Hiraeth_Homestead)", "Hiraeth_Homestead_Exterior"),
        ("scn_interior_homestead", "故园庄园室内居所_(Homestead_Interior)", "Hiraeth_Homestead_Interior"),
        ("scn_heartbearer_tomb", "持心者之墓_(Heartbearer_Tomb)", "Heartbearer_Tomb"),
        ("scn_fallenantihero", "陨落的反英雄秘穴_(Fallen_Antihero_Lair)", "Fallen_Antihero_Lair"),
        ("scn_zendar_center", "旧曾扎尔市中心广场_(Old_Zendar_Center)", "Old_Zendar_Center"),
        ("scn_zendar_arena", "曾扎尔格斗竞技场_(Zendar_Arena)", "Zendar_Arena"),
        ("scn_zendar_reliquary", "曾扎尔圣物陈列室_(Zendar_Reliquary)", "Zendar_Reliquary"),
        ("scn_the_happy_boar", "曾扎尔快乐公猪酒馆_(The_Happy_Boar)", "The_Happy_Boar_Tavern"),
        ("scn_four_ways_inn", "四路客栈大地图外景_(Four_Ways_Inn)", "Four_Ways_Inn_Exterior"),
        ("scn_four_ways_inn_cellar", "四路客栈私酿酒窖_(Four_Ways_Inn_Cellar)", "Four_Ways_Inn_Cellar"),
        ("scn_training_ground_ranged_melee_1", "五大酷刑场一号试验地_(Torture_Field_1)", "Torture_Field_1"),
    ]

    # 18 城镇中心场景
    town_scenes_data = [
        ("scn_town_1_center", "特尔戈维什特街道_(Targoviste)"),
        ("scn_town_2_center", "布加勒斯特/贝尔格莱德街道_(Bucharest/Belgrade)"),
        ("scn_town_3_center", "锡比乌街道_(Sibiu)"),
        ("scn_town_4_center", "佩奇街道_(Pecs)"),
        ("scn_town_5_center", "克卢日街道_(Kolozsvar)"),
        ("scn_town_6_center", "布达街道_(Buda)"),
        ("scn_town_7_center", "贝尔格莱德要塞街道_(Belgrade_Fortress)"),
        ("scn_town_8_center", "苏恰瓦街道_(Suceava)"),
        ("scn_town_9_center", "雅西街道_(Jassy)"),
        ("scn_town_10_center", "君士坦丁堡大都市街道_(Constantinople)"),
        ("scn_town_11_center", "霍京街道_(Hotin)"),
        ("scn_town_12_center", "布勒伊拉街道_(Braila)"),
        ("scn_town_13_center", "阿克曼街道_(Akkerman)"),
        ("scn_town_14_center", "埃迪尔内街道_(Edirne)"),
        ("scn_town_15_center", "萨格勒布街道_(Zagreb)"),
        ("scn_town_16_center", "塞格德街道_(Szeged)"),
        ("scn_town_17_center", "索菲亚街道_(Sofia)"),
        ("scn_town_18_center", "萨洛尼卡港口街道_(Salonika)"),
    ]

    mst_town_default_val = tag_val(TAG_MST, 0) # 792633534417207296

    def make_scene_jump_option(opt_id, opt_text, scn_id, ret_menu_id):
        s_idx = scene_to_idx[scn_id]
        s_val = tag_val(TAG_SCENE, s_idx)
        m_val = mval(ret_menu_id)
        # 4 1304 1 <this_menu> 1911 1 <mst> 1910 1 <scene> 2048 0
        return f" mno_{opt_id}  0  {opt_text}  4 1304 1 {m_val} 1911 1 {mst_town_default_val} 1910 1 {s_val} 2048 0  . \n"

    def make_menu_jump_option(opt_id, opt_text, target_menu_id):
        tm_val = mval(target_menu_id)
        return f" mno_{opt_id}  0  {opt_text}  1 2060 1 {tm_val}  . \n"

    new_menus_txt = []
    cns_entries = {}

    # -------------------------------------------------------------
    # Menu 0: menu_scene_viewer (Hub)
    # -------------------------------------------------------------
    m0_id = "menu_scene_viewer"
    m0_text = "Scene_Viewer_&_World_Showroom:_Explore_all_settlement_scenes,_hidden_S&S_realms,_historical_towns,_castles_and_villages._Press_TAB_in_any_scene_to_instantly_return_to_this_menu."
    m0_opts = [
        make_menu_jump_option("sv_to_redlist", "1._[RED_LIST]_S&S_Mechanism_Settlements_(35_Scenes_Must_Audit)...", "menu_sv_redlist"),
        make_menu_jump_option("sv_to_secrets", "2._S&S_Mythic_Realms_&_Secret_Dimensions_(24_Locations)...", "menu_sv_secrets_1"),
        make_menu_jump_option("sv_to_towns", "3._1521_Historical_Towns_Street_View_(18_Cities)...", "menu_sv_towns_list"),
        make_menu_jump_option("sv_to_castles", "4._1521_Historical_Castles_&_Fortresses_(40_Strongholds)...", "menu_sv_castles_p1"),
        make_menu_jump_option("sv_to_villages", "5._1521_Historical_Villages_&_Camps_(90_Settlements)...", "menu_sv_villages_p1"),
        " mno_sv_main_back  0  Back_to_Reports_/_Camp_Menu.  1 2055 0  . \n"
    ]
    new_menus_txt.append(f"{m0_id} 0 {m0_text} none 0 {len(m0_opts)}\n" + "".join(m0_opts))
    cns_entries[m0_id] = "场景查看器与实机展厅：你可以随时传送进入任意聚落与地下秘境进行实机核查。在场景中按 TAB 随时原路返回本菜单。"
    cns_entries["mno_sv_to_redlist"] = "1. 【红名单】S&S 机制聚落场景（34 座聚落 / 35 个红名单场景，换皮重点排查）..."
    cns_entries["mno_sv_to_secrets"] = "2. S&S 专属大地图秘境与隐藏维度（盐矿/大巧匠/巴特镇/迷宫/鲸腹/罗宾汉等 24 处）..."
    cns_entries["mno_sv_to_towns"] = "3. 1521 历史城镇街道漫步（18 座历史首府与商埠街道）..."
    cns_entries["mno_sv_to_castles"] = "4. 1521 历史要塞与城堡领主大厅（40 座边境要塞）..."
    cns_entries["mno_sv_to_villages"] = "5. 1521 历史村庄与平原乡野（90 个聚落外景）..."
    cns_entries["mno_sv_main_back"] = "返回报告菜单 / 营地界面。"

    # -------------------------------------------------------------
    # Menu 1: menu_sv_redlist (Red-List Hub)
    # -------------------------------------------------------------
    m1_id = "menu_sv_redlist"
    m1_text = "[RED_LIST_SCENES]_S&S_Exclusive_Mechanism_Settlements:^These_35_scenes_(34_settlements)_contain_hardcoded_props,_passages,_secret_doors,_or_spawn_points.^Do_NOT_replace_them_without_migrating_props!^Select_a_category_to_inspect_each_scene_in-game:"
    m1_opts = [
        make_menu_jump_option("sv_rl_go_towns", "1._Red-List_Towns_(12_Towns_/_13_Scenes:_Belgrade,_Buda,_Zagreb...)...", "menu_sv_rl_towns"),
        make_menu_jump_option("sv_rl_go_castles", "2._Red-List_Castles_(5_Fortresses:_Szepes,_Smederevo,_Bran...)...", "menu_sv_rl_castles"),
        make_menu_jump_option("sv_rl_go_vil1", "3._Red-List_Villages_Part_1_(9_Villages:_Csepel,_Mohacs,_Limnos...)...", "menu_sv_rl_vil1"),
        make_menu_jump_option("sv_rl_go_vil2", "4._Red-List_Villages_Part_2_(8_Villages:_Kozloduy_Underworld,_Snagov...)...", "menu_sv_rl_vil2"),
        make_menu_jump_option("sv_rl_go_all_p1", "5._Sequential_Walk-through_ALL_35_Scenes_(Page_1:_1-18)...", "menu_sv_rl_all_p1"),
        make_menu_jump_option("sv_rl_go_all_p2", "6._Sequential_Walk-through_ALL_35_Scenes_(Page_2:_19-35)...", "menu_sv_rl_all_p2"),
        make_menu_jump_option("sv_rl_back_hub", "Back_to_Scene_Viewer_Hub.", "menu_scene_viewer")
    ]
    new_menus_txt.append(f"{m1_id} 0 {m1_text} none 0 {len(m1_opts)}\n" + "".join(m1_opts))
    cns_entries[m1_id] = "【红名单】S&S 专属机制聚落场景专区：这 35 个场景包含硬编码的机关物件、暗门或特殊出生点，替换场景前必须核查！"
    cns_entries["mno_sv_rl_go_towns"] = "1. 城镇红名单场景（12 座城镇 / 13 个场景：贝尔格莱德街道/酒馆、布达杂货铺、萨格勒布监狱等）..."
    cns_entries["mno_sv_rl_go_castles"] = "2. 城堡红名单场景（5 座要塞：斯梅代雷沃蛇桩、布兰/胡内多阿拉/维丁大厅等）..."
    cns_entries["mno_sv_rl_go_vil1"] = "3. 村庄红名单场景 第一部分（9 个村庄：利姆诺斯波塞冬神殿、哈采格象棋塔、切佩尔等）..."
    cns_entries["mno_sv_rl_go_vil2"] = "4. 村庄红名单场景 第二部分（8 个村庄：科兹洛杜伊冥府大门、斯纳戈夫金甲虫、图尔努等）..."
    cns_entries["mno_sv_rl_go_all_p1"] = "5. 顺序遍历全 35 个红名单场景（第 1-18 项：城镇与城堡）..."
    cns_entries["mno_sv_rl_go_all_p2"] = "6. 顺序遍历全 35 个红名单场景（第 19-35 项：全部村庄）..."
    cns_entries["mno_sv_rl_back_hub"] = "返回场景查看器主目录。"

    # -------------------------------------------------------------
    # Menu 2: menu_sv_rl_towns (13 Scenes)
    # -------------------------------------------------------------
    m2_id = "menu_sv_rl_towns"
    m2_text = "Red-List_Towns_(13_Scenes):_Select_a_scene_to_enter_and_inspect_in-game._(Press_TAB_to_return)"
    m2_opts = []
    for idx, (sid, name_cn, name_en, note) in enumerate(redlist_data[:13]):
        oid = f"sv_rlt_{idx+1}"
        m2_opts.append(make_scene_jump_option(oid, f"{idx+1}._{name_en}", sid, m2_id))
        cns_entries[f"mno_{oid}"] = f"{idx+1}. {name_cn} 【机制: {note}】"
    m2_opts.append(make_menu_jump_option("sv_rlt_back", "Back_to_Red-List_Menu.", "menu_sv_redlist"))
    cns_entries["mno_sv_rlt_back"] = "返回红名单专区分类菜单。"
    new_menus_txt.append(f"{m2_id} 0 {m2_text} none 0 {len(m2_opts)}\n" + "".join(m2_opts))
    cns_entries[m2_id] = "红名单城镇场景（共 13 处）：点击即可立即传送进入实机巡查，按 TAB 键原路返回。"

    # -------------------------------------------------------------
    # Menu 3: menu_sv_rl_castles (5 Scenes)
    # -------------------------------------------------------------
    m3_id = "menu_sv_rl_castles"
    m3_text = "Red-List_Castles_(5_Scenes):_Select_a_scene_to_enter_and_inspect_in-game._(Press_TAB_to_return)"
    m3_opts = []
    for idx, (sid, name_cn, name_en, note) in enumerate(redlist_data[13:18]):
        oid = f"sv_rlc_{idx+1}"
        m3_opts.append(make_scene_jump_option(oid, f"{idx+1}._{name_en}", sid, m3_id))
        cns_entries[f"mno_{oid}"] = f"{idx+1}. {name_cn} 【机制: {note}】"
    m3_opts.append(make_menu_jump_option("sv_rlc_back", "Back_to_Red-List_Menu.", "menu_sv_redlist"))
    cns_entries["mno_sv_rlc_back"] = "返回红名单专区分类菜单。"
    new_menus_txt.append(f"{m3_id} 0 {m3_text} none 0 {len(m3_opts)}\n" + "".join(m3_opts))
    cns_entries[m3_id] = "红名单城堡要塞场景（共 5 处）：点击即可立即传送进入实机巡查，按 TAB 键原路返回。"

    # -------------------------------------------------------------
    # Menu 4: menu_sv_rl_vil1 (9 Villages)
    # -------------------------------------------------------------
    m4_id = "menu_sv_rl_vil1"
    m4_text = "Red-List_Villages_Part_1_(9_Villages):_Select_a_scene_to_enter._(Press_TAB_to_return)"
    m4_opts = []
    for idx, (sid, name_cn, name_en, note) in enumerate(redlist_data[18:27]):
        oid = f"sv_rlv1_{idx+1}"
        m4_opts.append(make_scene_jump_option(oid, f"{idx+1}._{name_en}", sid, m4_id))
        cns_entries[f"mno_{oid}"] = f"{idx+1}. {name_cn} 【机制: {note}】"
    m4_opts.append(make_menu_jump_option("sv_rlv1_next", "Next_Page_(Villages_Part_2)...", "menu_sv_rl_vil2"))
    m4_opts.append(make_menu_jump_option("sv_rlv1_back", "Back_to_Red-List_Menu.", "menu_sv_redlist"))
    cns_entries["mno_sv_rlv1_next"] = "下一页：村庄红名单 第二部分..."
    cns_entries["mno_sv_rlv1_back"] = "返回红名单专区分类菜单。"
    new_menus_txt.append(f"{m4_id} 0 {m4_text} none 0 {len(m4_opts)}\n" + "".join(m4_opts))
    cns_entries[m4_id] = "红名单村庄场景 第一部分（9 处）：包含波塞冬神殿、象棋塔、警长之箭等特殊机关。"

    # -------------------------------------------------------------
    # Menu 5: menu_sv_rl_vil2 (8 Villages)
    # -------------------------------------------------------------
    m5_id = "menu_sv_rl_vil2"
    m5_text = "Red-List_Villages_Part_2_(8_Villages):_Select_a_scene_to_enter._(Press_TAB_to_return)"
    m5_opts = []
    for idx, (sid, name_cn, name_en, note) in enumerate(redlist_data[27:35]):
        oid = f"sv_rlv2_{idx+1}"
        m5_opts.append(make_scene_jump_option(oid, f"{idx+1}._{name_en}", sid, m5_id))
        cns_entries[f"mno_{oid}"] = f"{idx+1}. {name_cn} 【机制: {note}】"
    m5_opts.append(make_menu_jump_option("sv_rlv2_prev", "Previous_Page_(Villages_Part_1)...", "menu_sv_rl_vil1"))
    m5_opts.append(make_menu_jump_option("sv_rlv2_back", "Back_to_Red-List_Menu.", "menu_sv_redlist"))
    cns_entries["mno_sv_rlv2_prev"] = "上一页：村庄红名单 第一部分..."
    cns_entries["mno_sv_rlv2_back"] = "返回红名单专区分类菜单。"
    new_menus_txt.append(f"{m5_id} 0 {m5_text} none 0 {len(m5_opts)}\n" + "".join(m5_opts))
    cns_entries[m5_id] = "红名单村庄场景 第二部分（8 处）：包含冥府大门与冥河渡船、金甲虫、安娜贝尔墓碑等。"

    # -------------------------------------------------------------
    # Menu 6 & 7: menu_sv_rl_all_p1 & p2 (Sequential 35 Scenes)
    # -------------------------------------------------------------
    m6_id = "menu_sv_rl_all_p1"
    m6_text = "Red-List_Full_Catalog_Page_1_(Scenes_1-18):_Sequential_In-Game_Check"
    m6_opts = []
    for idx, (sid, name_cn, name_en, note) in enumerate(redlist_data[:18]):
        oid = f"sv_rla1_{idx+1}"
        m6_opts.append(make_scene_jump_option(oid, f"[{idx+1:02d}]_{name_en}", sid, m6_id))
        cns_entries[f"mno_{oid}"] = f"[{idx+1:02d}] {name_cn} ({note})"
    m6_opts.append(make_menu_jump_option("sv_rla1_next", "Next_Page_(Scenes_19-35)...", "menu_sv_rl_all_p2"))
    m6_opts.append(make_menu_jump_option("sv_rla1_back", "Back_to_Red-List_Hub.", "menu_sv_redlist"))
    cns_entries["mno_sv_rla1_next"] = "下一页：全部红名单场景 第 19-35 项..."
    cns_entries["mno_sv_rla1_back"] = "返回红名单总目录。"
    new_menus_txt.append(f"{m6_id} 0 {m6_text} none 0 {len(m6_opts)}\n" + "".join(m6_opts))
    cns_entries[m6_id] = "红名单全场景顺序走查 第 1 页（第 1-18 项：13 座城镇与 5 座要塞）"

    m7_id = "menu_sv_rl_all_p2"
    m7_text = "Red-List_Full_Catalog_Page_2_(Scenes_19-35):_Sequential_In-Game_Check"
    m7_opts = []
    for idx, (sid, name_cn, name_en, note) in enumerate(redlist_data[18:35]):
        cur_num = 19 + idx
        oid = f"sv_rla2_{cur_num}"
        m7_opts.append(make_scene_jump_option(oid, f"[{cur_num:02d}]_{name_en}", sid, m7_id))
        cns_entries[f"mno_{oid}"] = f"[{cur_num:02d}] {name_cn} ({note})"
    m7_opts.append(make_menu_jump_option("sv_rla2_prev", "Previous_Page_(Scenes_1-18)...", "menu_sv_rl_all_p1"))
    m7_opts.append(make_menu_jump_option("sv_rla2_back", "Back_to_Red-List_Hub.", "menu_sv_redlist"))
    cns_entries["mno_sv_rla2_prev"] = "上一页：全部红名单场景 第 1-18 项..."
    cns_entries["mno_sv_rla2_back"] = "返回红名单总目录。"
    new_menus_txt.append(f"{m7_id} 0 {m7_text} none 0 {len(m7_opts)}\n" + "".join(m7_opts))
    cns_entries[m7_id] = "红名单全场景顺序走查 第 2 页（第 19-35 项：全部 17 座村庄）"

    # -------------------------------------------------------------
    # Menu 8 & 9: menu_sv_secrets_1 & 2 (24 Secret Realms)
    # -------------------------------------------------------------
    m8_id = "menu_sv_secrets_1"
    m8_text = "S&S_Mythic_Realms_&_Secret_Dimensions_Part_1_(Locations_1-12):_Select_a_realm_to_enter."
    m8_opts = []
    for idx, (sid, name_cn, name_en) in enumerate(secret_scenes_data[:12]):
        oid = f"sv_sec1_{idx+1}"
        m8_opts.append(make_scene_jump_option(oid, f"{idx+1}._{name_en}", sid, m8_id))
        cns_entries[f"mno_{oid}"] = f"{idx+1}. {name_cn}"
    m8_opts.append(make_menu_jump_option("sv_sec1_next", "Next_Page_(Locations_13-24)...", "menu_sv_secrets_2"))
    m8_opts.append(make_menu_jump_option("sv_sec1_back", "Back_to_Scene_Viewer_Hub.", "menu_scene_viewer"))
    cns_entries["mno_sv_sec1_next"] = "下一页：S&S 秘境维度 第 13-24 处..."
    cns_entries["mno_sv_sec1_back"] = "返回场景查看器主目录。"
    new_menus_txt.append(f"{m8_id} 0 {m8_text} none 0 {len(m8_opts)}\n" + "".join(m8_opts))
    cns_entries[m8_id] = "S&S 专属大地图秘境与隐藏维度 第一部分（12 处）：盐矿、发条盐洞、巴特镇、童话迷宫、噩梦维度、鲸腹等。"

    m9_id = "menu_sv_secrets_2"
    m9_text = "S&S_Mythic_Realms_&_Secret_Dimensions_Part_2_(Locations_13-24):_Select_a_realm_to_enter."
    m9_opts = []
    for idx, (sid, name_cn, name_en) in enumerate(secret_scenes_data[12:24]):
        cur_num = 13 + idx
        oid = f"sv_sec2_{cur_num}"
        m9_opts.append(make_scene_jump_option(oid, f"{cur_num}._{name_en}", sid, m9_id))
        cns_entries[f"mno_{oid}"] = f"{cur_num}. {name_cn}"
    m9_opts.append(make_menu_jump_option("sv_sec2_prev", "Previous_Page_(Locations_1-12)...", "menu_sv_secrets_1"))
    m9_opts.append(make_menu_jump_option("sv_sec2_back", "Back_to_Scene_Viewer_Hub.", "menu_scene_viewer"))
    cns_entries["mno_sv_sec2_prev"] = "上一页：S&S 秘境维度 第 1-12 处..."
    cns_entries["mno_sv_sec2_back"] = "返回场景查看器主目录。"
    new_menus_txt.append(f"{m9_id} 0 {m9_text} none 0 {len(m9_opts)}\n" + "".join(m9_opts))
    cns_entries[m9_id] = "S&S 专属大地图秘境与隐藏维度 第二部分（12 处）：象牙神殿、故园庄园、持心者之墓、旧曾扎尔、快乐公猪酒馆等。"

    # -------------------------------------------------------------
    # Menu 10: menu_sv_towns_list (18 Towns)
    # -------------------------------------------------------------
    m10_id = "menu_sv_towns_list"
    m10_text = "1521_Historical_Towns_Street_View_(18_Cities):_Select_a_town_to_visit_the_streets."
    m10_opts = []
    for idx, (sid, name_cn) in enumerate(town_scenes_data):
        oid = f"sv_tw_{idx+1}"
        m10_opts.append(make_scene_jump_option(oid, f"{idx+1}._{sid}", sid, m10_id))
        cns_entries[f"mno_{oid}"] = f"{idx+1}. {name_cn}"
    m10_opts.append(make_menu_jump_option("sv_tw_back", "Back_to_Scene_Viewer_Hub.", "menu_scene_viewer"))
    cns_entries["mno_sv_tw_back"] = "返回场景查看器主目录。"
    new_menus_txt.append(f"{m10_id} 0 {m10_text} none 0 {len(m10_opts)}\n" + "".join(m10_opts))
    cns_entries[m10_id] = "1521 历史城镇街道展厅（全 18 座城市街道外景）：实机漫步巡查。"

    # -------------------------------------------------------------
    # Menu 11 & 12: menu_sv_castles_p1 & p2 (40 Castles)
    # -------------------------------------------------------------
    m11_id = "menu_sv_castles_p1"
    m11_text = "1521_Historical_Castles_Part_1_(Castles_1-20):_Select_a_castle_exterior_to_visit."
    m11_opts = []
    for idx in range(20):
        c_num = idx + 1
        sid = f"scn_castle_{c_num}_exterior"
        oid = f"sv_cas1_{c_num}"
        m11_opts.append(make_scene_jump_option(oid, f"{c_num}._{sid}", sid, m11_id))
        cns_entries[f"mno_{oid}"] = f"{c_num}. 城堡要塞外景 {sid}"
    m11_opts.append(make_menu_jump_option("sv_cas1_next", "Next_Page_(Castles_21-40)...", "menu_sv_castles_p2"))
    m11_opts.append(make_menu_jump_option("sv_cas1_back", "Back_to_Scene_Viewer_Hub.", "menu_scene_viewer"))
    cns_entries["mno_sv_cas1_next"] = "下一页：城堡要塞 第 21-40 座..."
    cns_entries["mno_sv_cas1_back"] = "返回场景查看器主目录。"
    new_menus_txt.append(f"{m11_id} 0 {m11_text} none 0 {len(m11_opts)}\n" + "".join(m11_opts))
    cns_entries[m11_id] = "1521 历史要塞与城堡 第一部分（第 1-20 座城堡外景巡查）"

    m12_id = "menu_sv_castles_p2"
    m12_text = "1521_Historical_Castles_Part_2_(Castles_21-40):_Select_a_castle_exterior_to_visit."
    m12_opts = []
    for idx in range(20, 40):
        c_num = idx + 1
        sid = f"scn_castle_{c_num}_exterior"
        oid = f"sv_cas2_{c_num}"
        m12_opts.append(make_scene_jump_option(oid, f"{c_num}._{sid}", sid, m12_id))
        cns_entries[f"mno_{oid}"] = f"{c_num}. 城堡要塞外景 {sid}"
    m12_opts.append(make_menu_jump_option("sv_cas2_prev", "Previous_Page_(Castles_1-20)...", "menu_sv_castles_p1"))
    m12_opts.append(make_menu_jump_option("sv_cas2_back", "Back_to_Scene_Viewer_Hub.", "menu_scene_viewer"))
    cns_entries["mno_sv_cas2_prev"] = "上一页：城堡要塞 第 1-20 座..."
    cns_entries["mno_sv_cas2_back"] = "返回场景查看器主目录。"
    new_menus_txt.append(f"{m12_id} 0 {m12_text} none 0 {len(m12_opts)}\n" + "".join(m12_opts))
    cns_entries[m12_id] = "1521 历史要塞与城堡 第二部分（第 21-40 座城堡外景巡查）"

    # -------------------------------------------------------------
    # Menu 13..17: menu_sv_villages_p1..p5 (90 Villages)
    # -------------------------------------------------------------
    for p in range(5):
        m_id = f"menu_sv_villages_p{p+1}"
        start_v = p * 18 + 1
        end_v = (p + 1) * 18
        m_text = f"1521_Historical_Villages_Part_{p+1}_(Villages_{start_v}-{end_v}):_Select_a_village_scene."
        m_opts = []
        for v in range(start_v, end_v + 1):
            sid = f"scn_village_{v}"
            oid = f"sv_vil_{v}"
            m_opts.append(make_scene_jump_option(oid, f"{v}._{sid}", sid, m_id))
            cns_entries[f"mno_{oid}"] = f"{v}. 村庄场景 {sid}"
        if p > 0:
            prev_id = f"menu_sv_villages_p{p}"
            m_opts.append(make_menu_jump_option(f"sv_vil_p{p+1}_prev", "Previous_Page...", prev_id))
            cns_entries[f"mno_sv_vil_p{p+1}_prev"] = "上一页村庄列表..."
        if p < 4:
            next_id = f"menu_sv_villages_p{p+2}"
            m_opts.append(make_menu_jump_option(f"sv_vil_p{p+1}_next", "Next_Page...", next_id))
            cns_entries[f"mno_sv_vil_p{p+1}_next"] = "下一页村庄列表..."
        m_opts.append(make_menu_jump_option(f"sv_vil_p{p+1}_back", "Back_to_Scene_Viewer_Hub.", "menu_scene_viewer"))
        cns_entries[f"mno_sv_vil_p{p+1}_back"] = "返回场景查看器主目录。"
        new_menus_txt.append(f"{m_id} 0 {m_text} none 0 {len(m_opts)}\n" + "".join(m_opts))
        cns_entries[m_id] = f"1521 历史村庄聚落 第 {p+1} 部分（第 {start_v}-{end_v} 个村庄场景巡查）"

    # 4. 在 menu_reports 与 menu_camp_action 注入入口选项
    # menu_reports 在 menu_reports 这一行将选项计数 +1，并在 mno_all_items 后面追加 mno_scene_viewer
    full_content = "".join(menu_lines)
    
    # 查找 menu_reports
    hub_val = mval("menu_scene_viewer")
    opt_reports = f" mno_scene_viewer  0  View_scenes_and_locations.  1 2060 1 {hub_val}  . \n"
    cns_entries["mno_scene_viewer"] = "查看场景与特殊地点（场景查看器）"

    opt_camp = f" mno_camp_scene_viewer  0  Explore_scenes_and_locations.  1 2060 1 {hub_val}  . \n"
    cns_entries["mno_camp_scene_viewer"] = "探索场景与特殊地点（场景查看器）"

    # 如果还没注入过 mno_scene_viewer
    if "mno_scene_viewer" not in full_content:
        # 更新 menu_reports 行
        import re
        def rep_count(m):
            header = m.group(1)
            cnt = int(m.group(2))
            return f"{header} {cnt+1}"
        full_content = re.sub(r'^(menu_reports\s+0\s+[^\n]+\s+none\s+\d+\s+[^\n]+\s+)(\d+)$', rep_count, full_content, flags=re.MULTILINE)
        
        # 在 mno_all_items 选项后插入
        pos = full_content.find("mno_all_items ")
        if pos != -1:
            dot_pos = full_content.find(" . \n", pos)
            if dot_pos != -1:
                insert_pos = dot_pos + 4
                full_content = full_content[:insert_pos] + opt_reports + full_content[insert_pos:]
                print("  已向 menu_reports 成功注入 mno_scene_viewer 入口！")

    # 如果还没注入过 mno_camp_scene_viewer
    if "mno_camp_scene_viewer" not in full_content:
        def rep_camp_count(m):
            header = m.group(1)
            cnt = int(m.group(2))
            return f"{header} {cnt+1}"
        full_content = re.sub(r'^(menu_camp_action\s+0\s+[^\n]+\s+none\s+\d+\s+)(\d+)$', rep_camp_count, full_content, flags=re.MULTILINE)
        
        # 在 menu_camp_action 末尾选项前插入
        pos = full_content.find("menu_camp_action 0")
        if pos != -1:
            end_pos = full_content.find("\nmenu_", pos + 1)
            if end_pos != -1:
                # 在最后一个选项前追加
                full_content = full_content[:end_pos] + opt_camp + full_content[end_pos:]
                print("  已向 menu_camp_action 成功注入 mno_camp_scene_viewer 入口！")

    # 5. 追加所有新菜单，并更新总菜单声明数
    total_new_menus = len(menu_catalog)
    new_total_declared = base_menu_idx + total_new_menus

    lines = full_content.splitlines(keepends=True)
    lines[1] = f"{new_total_declared}\n"
    final_menus_content = "".join(lines) + "".join(new_menus_txt)

    with open(menus_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(final_menus_content)
    print(f"  已向 menus.txt 成功写入 {total_new_menus} 个新菜单，当前总菜单数: {new_total_declared}")

    # 6. 更新 languages/cns/game_menus.csv 汉化文件 (采用追加模式，避免打乱原文件排序产生巨幅 diff)
    cns_path = os.path.join(MOD_DIR, "languages", "cns", "game_menus.csv")
    existing_keys = set()
    if os.path.exists(cns_path):
        with open(cns_path, "r", encoding="utf-8", errors="replace") as f:
            for l in f:
                if "|" in l:
                    k, _ = l.strip().split("|", 1)
                    existing_keys.add(k)
    
    to_append = []
    for k, v in cns_entries.items():
        if k not in existing_keys:
            to_append.append(f"{k}|{v}\n")
    
    if to_append:
        with open(cns_path, "a", encoding="utf-8", newline="\n") as f:
            f.writelines(to_append)
    print(f"  已向 languages/cns/game_menus.csv 追加写入 {len(to_append)} 条全新中英对照汉化词条！")

    print("[场景查看器安装完成] 全部组件与入口部署完毕！")

if __name__ == "__main__":
    main()
