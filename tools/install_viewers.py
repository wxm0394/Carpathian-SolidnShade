#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_viewers.py
Installs:
1. Dynamic Troop Tree Viewer (prsnt_faction_troop_tree + prsnt_troop_note)
2. Interactive Paginated Item Viewer (prsnt_all_items)
3. All supporting scripts, meshes, variables, quick strings, and menus
into Carpathian Solid & Shade module.
"""

import os, sys, shutil

MODULE_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"

# -------------------------------------------------------------
# Bitmask constants according to Warband specification
# -------------------------------------------------------------
TAG_REGISTER       = 1
TAG_VARIABLE       = 2
TAG_STRING         = 3
TAG_ITEM           = 4
TAG_TROOP          = 5
TAG_FACTION        = 6
TAG_QUEST          = 7
TAG_PARTY_TPL      = 8
TAG_PARTY          = 9
TAG_SCENE          = 10
TAG_MISSION_TPL    = 11
TAG_MENU           = 12
TAG_SCRIPT         = 13
TAG_PARTICLE_SYS   = 14
TAG_SCENE_PROP     = 15
TAG_SOUND          = 16
TAG_LOCAL_VARIABLE = 17
TAG_MAP_ICON       = 18
TAG_SKILL          = 19
TAG_MESH           = 20
TAG_PRESENTATION   = 21
TAG_QUICK_STRING   = 22
TAG_TRACK          = 23
TAG_TABLEAU        = 24
TAG_ANIMATION      = 25

OPMASK_REGISTER       = TAG_REGISTER       << 56
OPMASK_VARIABLE       = TAG_VARIABLE       << 56
OPMASK_LOCAL_VARIABLE = TAG_LOCAL_VARIABLE << 56
OPMASK_QUICK_STRING   = TAG_QUICK_STRING   << 56
OPMASK_STRING         = TAG_STRING         << 56
OPMASK_SCRIPT         = TAG_SCRIPT         << 56
OPMASK_MESH           = TAG_MESH           << 56
OPMASK_PRESENTATION   = TAG_PRESENTATION   << 56
OPMASK_TROOP          = TAG_TROOP          << 56

def reg(n):
    return OPMASK_REGISTER + n

def local_var(n):
    return OPMASK_LOCAL_VARIABLE + n

def global_var(n):
    return OPMASK_VARIABLE + n

def qstr(n):
    return OPMASK_QUICK_STRING + n

def str_id(n):
    return OPMASK_STRING + n

def script_id(n):
    return OPMASK_SCRIPT + n

def prsnt_id(n):
    return OPMASK_PRESENTATION + n

def mesh_id(n):
    return n # in presentation overlay calls, mesh parameter is a raw integer index!

def backup_file(filepath):
    bak = filepath + ".orig_pre_viewers"
    if not os.path.exists(bak):
        shutil.copy2(filepath, bak)
        print(f"Backed up {os.path.basename(filepath)} -> {os.path.basename(bak)}")

def main():
    print("=== Installing Troop Tree Viewer and Item Viewer ===")
    
    # -------------------------------------------------------------
    # 1. Update meshes.txt
    # -------------------------------------------------------------
    meshes_path = os.path.join(MODULE_DIR, "meshes.txt")
    backup_file(meshes_path)
    with open(meshes_path, "r", encoding="latin1") as f:
        mesh_lines = f.readlines()
    
    mesh_count = int(mesh_lines[0].strip())
    existing_meshes = {}
    for idx, line in enumerate(mesh_lines[1:]):
        parts = line.split()
        if parts:
            existing_meshes[parts[0]] = idx
    
    needed_meshes = [
        ("mesh_mp_inventory_choose", "mesh_mp_inventory_choose 0 mp_inventory_choose 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 1.000000 1.000000 1.000000\n"),
        ("mesh_note_window", "mesh_note_window 0 note_window 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 1.000000 1.000000 1.000000\n"),
    ]
    
    added_meshes = False
    for m_name, m_line in needed_meshes:
        if m_name not in existing_meshes:
            existing_meshes[m_name] = len(mesh_lines) - 1
            mesh_lines.append(m_line)
            mesh_count += 1
            added_meshes = True
    
    if added_meshes:
        mesh_lines[0] = f"{mesh_count}\n"
        with open(meshes_path, "w", encoding="latin1") as f:
            f.writelines(mesh_lines)
        print(f"Updated meshes.txt: total meshes = {mesh_count}")
    
    id_mesh_load_window = existing_meshes["mesh_load_window"]
    id_mesh_white_plane = existing_meshes["mesh_white_plane"]
    id_mesh_mp_inventory_choose = existing_meshes["mesh_mp_inventory_choose"]
    id_mesh_note_window = existing_meshes["mesh_note_window"]
    print(f"Mesh IDs: load_window={id_mesh_load_window}, white_plane={id_mesh_white_plane}, mp_inv_choose={id_mesh_mp_inventory_choose}")

    # -------------------------------------------------------------
    # 2. Update variables.txt
    # -------------------------------------------------------------
    vars_path = os.path.join(MODULE_DIR, "variables.txt")
    backup_file(vars_path)
    with open(vars_path, "r", encoding="latin1") as f:
        var_lines = [l.strip() for l in f.readlines() if l.strip()]
    
    var_dict = {v: i for i, v in enumerate(var_lines)}
    
    needed_vars = [
        "temp",
        "g_presentation_obj_1",
        "g_presentation_obj_2",
        "g_presentation_obj_21",
        "g_presentation_next_presentation",
        "g_faction_troop_tree_sel",
        "g_all_items_category",
        "g_all_items_page",
        "g_all_items_sel_item",
        "g_all_items_imod",
        "g_all_items_qty",
        "g_all_items_cat_selector",
        "g_all_items_prev_btn",
        "g_all_items_next_btn",
        "g_all_items_get_btn",
        "g_all_items_done_btn",
        "g_all_items_tooltip_slot",
        "g_all_items_quality_selector",
    ]
    
    var_added = False
    for v in needed_vars:
        if v not in var_dict:
            var_dict[v] = len(var_lines)
            var_lines.append(v)
            var_added = True
    
    if var_added:
        with open(vars_path, "w", encoding="latin1") as f:
            f.write("\n".join(var_lines) + "\n")
        print(f"Updated variables.txt: total variables = {len(var_lines)}")
    
    v_temp = global_var(var_dict["temp"])
    v_obj_1 = global_var(var_dict["g_presentation_obj_1"])
    v_obj_21 = global_var(var_dict["g_presentation_obj_21"])
    v_next_prsnt = global_var(var_dict["g_presentation_next_presentation"])
    v_tree_sel = global_var(var_dict["g_faction_troop_tree_sel"])
    v_cat = global_var(var_dict["g_all_items_category"])
    v_page = global_var(var_dict["g_all_items_page"])
    v_sel_item = global_var(var_dict["g_all_items_sel_item"])
    v_imod = global_var(var_dict["g_all_items_imod"])
    v_qty = global_var(var_dict["g_all_items_qty"])
    v_cat_sel = global_var(var_dict["g_all_items_cat_selector"])
    v_prev_btn = global_var(var_dict["g_all_items_prev_btn"])
    v_next_btn = global_var(var_dict["g_all_items_next_btn"])
    v_get_btn = global_var(var_dict["g_all_items_get_btn"])
    v_done_btn = global_var(var_dict["g_all_items_done_btn"])
    v_tooltip_slot = global_var(var_dict["g_all_items_tooltip_slot"])
    v_qual_sel = global_var(var_dict["g_all_items_quality_selector"])

    # -------------------------------------------------------------
    # 3. Update quick_strings.txt
    # -------------------------------------------------------------
    qs_path = os.path.join(MODULE_DIR, "quick_strings.txt")
    backup_file(qs_path)
    with open(qs_path, "r", encoding="latin1") as f:
        qs_lines = f.readlines()
    
    qs_count = int(qs_lines[0].strip())
    existing_qs = {}
    for i, line in enumerate(qs_lines[1:]):
        parts = line.split(maxsplit=1)
        if parts:
            existing_qs[parts[0]] = i
    
    needed_qs = [
        ("qstr_faction_troop_tree", "qstr_faction_troop_tree Faction_Troop_Tree"),
        ("qstr_view_troop_trees", "qstr_view_troop_trees View_Troop_Trees"),
        ("qstr_view_all_items", "qstr_view_all_items View_All_Items"),
        ("qstr_all_items_title", "qstr_all_items_title Item_Viewer"),
        ("qstr_done", "qstr_done Done"),
        ("qstr_prev_page", "qstr_prev_page <_Prev"),
        ("qstr_next_page", "qstr_next_page Next_>"),
        ("qstr_get_item", "qstr_get_item Get_Item"),
        ("qstr_added_item", "qstr_added_item Added_{s1}_to_player_inventory."),
        ("qstr_page_str", "qstr_page_str Page_{reg0}_/_{reg1}_({reg2}_items)"),
        ("qstr_tree_hungary", "qstr_tree_hungary Kingdom_of_Hungary"),
        ("qstr_tree_moldavia", "qstr_tree_moldavia Principality_of_Moldavia"),
        ("qstr_tree_ottoman", "qstr_tree_ottoman Ottoman_Empire"),
        ("qstr_tree_wallachia", "qstr_tree_wallachia Principality_of_Wallachia"),
        ("qstr_tree_croatia", "qstr_tree_croatia Kingdom_of_Croatia"),
        ("qstr_tree_undead", "qstr_tree_undead Undead_&_Zombies"),
        ("qstr_tree_burned", "qstr_tree_burned Burned_Zombies"),
        ("qstr_tree_putrid", "qstr_tree_putrid Putrid_Zombies"),
        ("qstr_tree_preserved", "qstr_tree_preserved Preserved_Zombies"),
        ("qstr_tree_demons", "qstr_tree_demons Demonic_Entities"),
        ("qstr_tree_brollachan", "qstr_tree_brollachan Brollachan_Spawn"),
        ("qstr_tree_golem", "qstr_tree_golem Golems_&_Constructs"),
        ("qstr_tree_outlaws", "qstr_tree_outlaws Outlaws_&_Bandits"),
        ("qstr_tree_commoners", "qstr_tree_commoners Commoners_&_Mercenaries"),
        ("qstr_tree_manhunters", "qstr_tree_manhunters Manhunters"),
        ("qstr_tree_women", "qstr_tree_women Refugees_&_Sword_Sisters"),
        ("qstr_cat_all", "qstr_cat_all All_Items"),
        ("qstr_cat_horses", "qstr_cat_horses Horses"),
        ("qstr_cat_1h", "qstr_cat_1h One-Handed_Weapons"),
        ("qstr_cat_2h", "qstr_cat_2h Two-Handed_Weapons"),
        ("qstr_cat_polearms", "qstr_cat_polearms Polearms"),
        ("qstr_cat_bows", "qstr_cat_bows Bows"),
        ("qstr_cat_arrows", "qstr_cat_arrows Arrows"),
        ("qstr_cat_crossbows", "qstr_cat_crossbows Crossbows"),
        ("qstr_cat_bolts", "qstr_cat_bolts Bolts"),
        ("qstr_cat_thrown", "qstr_cat_thrown Throwing_Weapons"),
        ("qstr_cat_shields", "qstr_cat_shields Shields"),
        ("qstr_cat_helmets", "qstr_cat_helmets Helmets"),
        ("qstr_cat_armor", "qstr_cat_armor Body_Armor"),
        ("qstr_cat_boots", "qstr_cat_boots Boots"),
        ("qstr_cat_gloves", "qstr_cat_gloves Gloves"),
        ("qstr_cat_firearms", "qstr_cat_firearms Firearms"),
        ("qstr_cat_goods", "qstr_cat_goods Goods_&_Books"),
        ("qstr_troop_note_name_lvl", "qstr_troop_note_name_lvl Name:_{s1}^Level:_{reg1}^HP:_{reg0}"),
        ("qstr_troop_note_attr", "qstr_troop_note_attr Attributes:^STR:_{reg1}^INT:_{reg2}^^Skills:^Power_Strike:_{reg3}^Power_Draw:_{reg4}^Power_Throw:_{reg5}^Horse_Archery:_{reg6}^^Proficiencies:^1_Hand:_{reg7}^2_Hand:_{reg8}^Polearms:_{reg9}"),
        ("qstr_troop_note_attr2", "qstr_troop_note_attr2 AGI:_{reg1}^CHA:_{reg2}^^Shield:_{reg3}^Athletics:_{reg4}^Riding:_{reg5}^^Archery:_{reg6}^Crossbow:_{reg7}^Throwing:_{reg8}"),
        ("qstr_troop_note_equip", "qstr_troop_note_equip Equipment:"),
    ]
    
    qs_added = False
    for q_id, q_val in needed_qs:
        if q_id not in existing_qs:
            existing_qs[q_id] = len(qs_lines) - 1
            qs_lines.append(q_val + "\n")
            qs_count += 1
            qs_added = True
            
    if qs_added:
        qs_lines[0] = f"{qs_count}\n"
        with open(qs_path, "w", encoding="latin1") as f:
            f.writelines(qs_lines)
        print(f"Updated quick_strings.txt: total strings = {qs_count}")

    # -------------------------------------------------------------
    # 4. Update scripts.txt
    # -------------------------------------------------------------
    scripts_path = os.path.join(MODULE_DIR, "scripts.txt")
    backup_file(scripts_path)
    with open(scripts_path, "r", encoding="latin1") as f:
        script_lines = f.readlines()
        
    script_count = int(script_lines[1].strip())
    existing_scripts = {}
    i = 2
    while i < len(script_lines):
        line = script_lines[i].strip()
        if line and not line.startswith(" ") and not line[0].isdigit():
            parts = line.split()
            existing_scripts[parts[0]] = len(existing_scripts)
        i += 1
        
    # Table of scripts to install
    # prsnt_lines:
    # (store_script_param, ":size_x", 1), (store_script_param, ":size_y", 2),
    # (store_script_param, ":pos_x", 3), (store_script_param, ":pos_y", 4),
    # (store_script_param, ":color", 5),
    # (create_mesh_overlay, reg1, id_mesh_white_plane),
    # (val_mul, ":size_x", 50), (val_mul, ":size_y", 50),
    # (position_set_x, pos0, ":size_x"), (position_set_y, pos0, ":size_y"), (overlay_set_size, reg1, pos0),
    # (position_set_x, pos0, ":pos_x"), (position_set_y, pos0, ":pos_y"), (overlay_set_position, reg1, pos0),
    # (overlay_set_color, reg1, ":color")
    
    id_tab_party = 2 # tab_game_party_window
    id_trp_temp_a = 825
    id_trp_temp_b = 826
    id_trp_temp_c = 827
    id_trp_player = 0
    
    # Calculate script indices
    idx_prsnt_lines = existing_scripts.get("prsnt_lines", len(existing_scripts))
    idx_prsnt_lines_to = existing_scripts.get("prsnt_lines_to", idx_prsnt_lines + 1)
    idx_upgrade_tree_troop_and_name = existing_scripts.get("prsnt_upgrade_tree_troop_and_name", idx_prsnt_lines_to + 1)
    idx_upgrade_tree_troop_cost = existing_scripts.get("prsnt_upgrade_tree_troop_cost", idx_upgrade_tree_troop_and_name + 1)
    idx_get_troop_max_hp = existing_scripts.get("get_troop_max_hp", idx_upgrade_tree_troop_cost + 1)
    idx_copy_inventory = existing_scripts.get("copy_inventory", idx_get_troop_max_hp + 1)
    idx_game_get_upgrade_cost = existing_scripts.get("game_get_upgrade_cost", idx_copy_inventory + 1)
    idx_prsnt_culture_troop_tree = existing_scripts.get("prsnt_culture_troop_tree", idx_game_get_upgrade_cost + 1)
    idx_all_items_populate = existing_scripts.get("all_items_populate_category", idx_prsnt_culture_troop_tree + 1)
    
    # Pre-calculated presentations indices
    prsnt_path = os.path.join(MODULE_DIR, "presentations.txt")
    backup_file(prsnt_path)
    with open(prsnt_path, "r", encoding="latin1") as f:
        prsnt_lines = f.readlines()
    prsnt_count = int(prsnt_lines[1].strip())
    existing_prsnts = {}
    for idx, line in enumerate(prsnt_lines[2:]):
        parts = line.split()
        if parts and parts[0].startswith("prsnt_"):
            existing_prsnts[parts[0]] = len(existing_prsnts)
            
    idx_prsnt_troop_tree = existing_prsnts.get("prsnt_faction_troop_tree", len(existing_prsnts))
    idx_prsnt_troop_note = existing_prsnts.get("prsnt_troop_note", idx_prsnt_troop_tree + 1)
    idx_prsnt_all_items = existing_prsnts.get("prsnt_all_items", idx_prsnt_troop_note + 1)
    
    print(f"Target presentation IDs: troop_tree={idx_prsnt_troop_tree}, troop_note={idx_prsnt_troop_note}, all_items={idx_prsnt_all_items}")
    
    # Scripts definition
    new_scripts = []
    
    # 1. prsnt_lines
    code_prsnt_lines = (
        f" 15 23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 23 2 {local_var(3)} 4 23 2 {local_var(4)} 5 "
        f"911 2 {reg(1)} {id_mesh_white_plane} "
        f"2107 2 {local_var(0)} 50 2107 2 {local_var(1)} 50 "
        f"729 2 0 {local_var(0)} 730 2 0 {local_var(1)} 925 2 {reg(1)} 0 "
        f"729 2 0 {local_var(2)} 730 2 0 {local_var(3)} 926 2 {reg(1)} 0 "
        f"921 2 {reg(1)} {local_var(4)}"
    )
    new_scripts.append(("prsnt_lines", code_prsnt_lines))
    
    # 2. prsnt_lines_to
    code_prsnt_lines_to = (
        f" 25 23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 23 2 {local_var(3)} 4 23 2 {local_var(4)} 5 "
        f"4 0 31 2 {local_var(0)} {local_var(2)} "
        f"2121 3 {local_var(5)} {local_var(1)} {local_var(3)} 2113 1 {local_var(5)} "
        f"2110 2 {local_var(1)} {local_var(3)} 1 6 {idx_prsnt_lines} 4 {local_var(5)} {local_var(0)} {local_var(1)} {local_var(4)} "
        f"5 0 31 2 {local_var(1)} {local_var(3)} "
        f"2121 3 {local_var(5)} {local_var(0)} {local_var(2)} 2113 1 {local_var(5)} "
        f"2110 2 {local_var(0)} {local_var(2)} 1 6 {idx_prsnt_lines} {local_var(5)} 5 {local_var(0)} {local_var(1)} {local_var(4)} "
        f"5 0 2120 3 {local_var(6)} {local_var(0)} {local_var(2)} 2108 2 {local_var(6)} 2 2106 2 {local_var(6)} 6 "
        f"1 6 {idx_prsnt_lines_to} {local_var(0)} {local_var(1)} {local_var(6)} {local_var(1)} {local_var(4)} "
        f"1 6 {idx_prsnt_lines_to} {local_var(6)} {local_var(1)} {local_var(6)} {local_var(3)} {local_var(4)} "
        f"1 6 {idx_prsnt_lines_to} {local_var(6)} {local_var(3)} {local_var(2)} {local_var(3)} {local_var(4)} 3 0"
    )
    new_scripts.append(("prsnt_lines_to", code_prsnt_lines_to))
    
    # 3. prsnt_upgrade_tree_troop_and_name
    code_troop_and_name = (
        f" 20 23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 "
        f"2322 2 1 {local_var(0)} "
        f"910 3 {reg(1)} {str_id(1)} 4112 " # tf_center_justify (16) | tf_vertical_align_center (4096) = 4112
        f"729 2 1 600 730 2 1 600 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1 "
        f"2106 2 {local_var(1)} 52 "
        f"2122 3 {local_var(3)} {local_var(0)} 2 "
        f"938 4 {reg(1)} -1 {id_tab_party} {local_var(3)} "
        f"729 2 1 375 730 2 1 500 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1"
    )
    new_scripts.append(("prsnt_upgrade_tree_troop_and_name", code_troop_and_name))
    
    # 4. prsnt_upgrade_tree_troop_cost
    code_troop_cost = (
        f" 11 23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 "
        f"1 2 {idx_game_get_upgrade_cost} {local_var(0)} "
        f"2320 2 2 {qstr(existing_qs['qstr_page_str'])} " # scratch
        f"910 3 {reg(1)} {str_id(0)} 4100 " # tf_left_align | tf_vertical_align_center
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1 "
        f"729 2 1 600 730 2 1 600 925 2 {reg(1)} 1"
    )
    new_scripts.append(("prsnt_upgrade_tree_troop_cost", code_troop_cost))
    
    # 5. get_troop_max_hp
    code_get_max_hp = (
        f" 7 21 1 {local_var(0)} "
        f"2170 3 {local_var(1)} 36 {local_var(0)} " # skl_ironflesh = 36
        f"2172 3 {local_var(2)} {local_var(0)} 0 " # ca_strength = 0
        f"2107 2 {local_var(1)} 2 2105 2 {local_var(1)} {local_var(2)} 2105 2 {local_var(1)} 35 "
        f"2133 2 {reg(0)} {local_var(1)}"
    )
    new_scripts.append(("get_troop_max_hp", code_get_max_hp))
    
    # 6. copy_inventory
    code_copy_inv = (
        f" 13 21 1 {local_var(0)} 22 1 {local_var(1)} "
        f"1532 1 {local_var(1)} "
        f"1540 2 {local_var(2)} {local_var(0)} "
        f"6 3 {local_var(3)} 0 {local_var(2)} "
        f"1541 3 {local_var(4)} {local_var(0)} {local_var(3)} "
        f"1543 3 {local_var(1)} {local_var(3)} {local_var(4)} "
        f"1542 3 {local_var(5)} {local_var(0)} {local_var(3)} "
        f"1544 3 {local_var(1)} {local_var(3)} {local_var(5)} "
        f"1537 3 {local_var(6)} {local_var(0)} {local_var(3)} "
        f"32 2 {local_var(6)} 0 "
        f"1534 3 {local_var(1)} {local_var(3)} {local_var(6)} "
        f"3 0"
    )
    new_scripts.append(("copy_inventory", code_copy_inv))
    
    # 7. game_get_upgrade_cost
    code_upgrade_cost = (
        f" 24 21 1 {local_var(0)} 2171 2 {local_var(1)} {local_var(0)} "
        f"4 0 33 3 {local_var(1)} 0 6 2133 2 {reg(0)} 10 "
        f"5 0 33 3 {local_var(1)} 6 11 2133 2 {reg(0)} 20 "
        f"5 0 33 3 {local_var(1)} 11 16 2133 2 {reg(0)} 40 "
        f"5 0 33 3 {local_var(1)} 16 21 2133 2 {reg(0)} 80 "
        f"5 0 33 3 {local_var(1)} 21 26 2133 2 {reg(0)} 120 "
        f"5 0 2133 2 {reg(0)} 160 3 0"
    )
    new_scripts.append(("game_get_upgrade_cost", code_upgrade_cost))
    
    # 8. prsnt_culture_troop_tree
    # Parameter 1 is either culture or direct root troop
    code_culture_tree = (
        f" 182 21 1 {local_var(0)} "
        # Clear scratch arrays
        f"6 3 {local_var(1)} 0 61 "
        f"500 3 {id_trp_temp_a} {local_var(1)} 0 "
        f"500 3 {id_trp_temp_b} {local_var(1)} 0 "
        f"500 3 {id_trp_temp_c} {local_var(1)} 0 "
        f"2120 3 {local_var(2)} {local_var(1)} 100 "
        f"500 3 {id_trp_temp_b} {local_var(2)} -1 "
        f"500 3 {id_trp_temp_c} {local_var(2)} -1 "
        f"3 0 "
        # Determine root troop: if param >= 100 or is negative, direct troop; else culture slot
        f"4 0 30 2 {local_var(0)} 21 2133 2 {local_var(3)} {local_var(0)} "
        f"5 0 520 3 {local_var(3)} {local_var(0)} 41 " # slot_faction_tier_1_troop = 41
        f"3 0 "
        # lowest troop tiers init
        f"500 3 {id_trp_temp_a} 0 1 "
        f"500 3 {id_trp_temp_a} 1 1 "
        f"500 3 {id_trp_temp_b} 1 {local_var(3)} "
        f"2133 2 {local_var(4)} 0 2133 2 {local_var(5)} 0 "
        # Loop tiers 1..10
        f"6 3 {local_var(6)} 1 10 "
        f"31 2 {local_var(5)} 0 2133 2 {local_var(5)} 1 "
        f"2121 3 {local_var(7)} {local_var(6)} 1 "
        f"2122 3 {local_var(8)} {local_var(7)} 10 "
        f"2122 3 {local_var(9)} {local_var(6)} 10 "
        f"2133 2 {local_var(10)} 0 "
        f"520 3 {local_var(11)} {id_trp_temp_a} {local_var(8)} "
        f"32 2 {local_var(11)} 0 2105 2 {local_var(11)} 1 "
        f"6 3 {local_var(12)} 1 {local_var(11)} "
        f"2120 3 {local_var(13)} {local_var(12)} {local_var(8)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(13)} "
        f"32 2 {local_var(3)} 0 "
        # upgrade 0
        f"1561 3 {local_var(14)} {local_var(3)} 0 "
        f"4 0 32 2 {local_var(14)} 0 2133 2 {local_var(5)} 0 "
        f"2105 2 {local_var(10)} 1 "
        f"500 3 {id_trp_temp_a} {local_var(9)} {local_var(10)} "
        f"2120 3 {local_var(1)} {local_var(9)} {local_var(10)} "
        f"500 3 {id_trp_temp_a} {local_var(1)} {local_var(12)} "
        f"500 3 {id_trp_temp_b} {local_var(1)} {local_var(14)} 3 0 "
        # upgrade 1
        f"1561 3 {local_var(14)} {local_var(3)} 1 "
        f"4 0 32 2 {local_var(14)} 0 2133 2 {local_var(5)} 0 "
        f"2105 2 {local_var(10)} 1 "
        f"500 3 {id_trp_temp_a} {local_var(9)} {local_var(10)} "
        f"2120 3 {local_var(1)} {local_var(9)} {local_var(10)} "
        f"500 3 {id_trp_temp_a} {local_var(1)} {local_var(12)} "
        f"500 3 {id_trp_temp_b} {local_var(1)} {local_var(14)} 3 0 "
        f"3 0 "
        f"31 2 {local_var(5)} 0 2105 2 {local_var(4)} 1 "
        f"3 0 "
        # Y positions calculation
        f"2122 3 {local_var(15)} {local_var(4)} 10 2105 2 {local_var(4)} 1 "
        f"520 3 {local_var(10)} {id_trp_temp_a} {local_var(15)} 2105 2 {local_var(10)} 1 "
        f"6 3 {local_var(12)} 1 {local_var(10)} "
        f"2120 3 {local_var(1)} {local_var(15)} {local_var(12)} "
        f"2122 3 {local_var(16)} {local_var(12)} 140 " # troop_tree_space_y = 140
        f"2121 3 {local_var(17)} 585 {local_var(16)} " # 550 + 35 = 585
        f"500 3 {id_trp_temp_c} {local_var(1)} {local_var(17)} "
        f"3 0 "
        # Backwards propagation for tree positions
        f"7 3 {local_var(6)} 1 {local_var(4)} "
        f"2122 3 {local_var(9)} {local_var(6)} 10 "
        f"2121 3 {local_var(7)} {local_var(6)} 1 "
        f"2122 3 {local_var(8)} {local_var(7)} 10 "
        f"520 3 {local_var(11)} {id_trp_temp_a} {local_var(8)} "
        f"32 2 {local_var(11)} 0 2105 2 {local_var(11)} 1 "
        f"6 3 {local_var(12)} 1 {local_var(11)} "
        f"2120 3 {local_var(13)} {local_var(12)} {local_var(8)} "
        f"2133 2 {local_var(18)} 0 2133 2 {local_var(10)} 0 "
        f"6 3 {local_var(16)} 1 10 "
        f"2120 3 {local_var(1)} {local_var(16)} {local_var(9)} "
        f"540 3 {id_trp_temp_a} {local_var(1)} {local_var(12)} "
        f"520 3 {local_var(17)} {id_trp_temp_c} {local_var(1)} "
        f"2105 2 {local_var(18)} {local_var(17)} 2105 2 {local_var(10)} 1 "
        f"3 0 "
        f"32 2 {local_var(10)} 0 2108 2 {local_var(18)} {local_var(10)} "
        f"500 3 {id_trp_temp_c} {local_var(13)} {local_var(18)} "
        f"3 0 "
        f"3 0 "
        # Draw Troops, Nodes & Lines
        f"2105 2 {local_var(15)} 11 500 3 {id_trp_temp_c} 100 0 2133 2 {local_var(10)} 100 "
        f"6 3 {local_var(1)} 0 {local_var(15)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(1)} "
        f"32 2 {local_var(3)} 0 "
        f"2123 3 {local_var(6)} {local_var(1)} 10 "
        f"2122 3 {local_var(19)} {local_var(6)} 170 2105 2 {local_var(19)} 60 " # space_x=170, left=60
        f"520 3 {local_var(20)} {id_trp_temp_c} {local_var(1)} "
        f"2105 2 {local_var(10)} 1 "
        f"1 4 {idx_upgrade_tree_troop_and_name} {local_var(3)} {local_var(19)} {local_var(20)} "
        f"500 3 {id_trp_temp_c} {local_var(10)} {reg(1)} "
        f"500 3 {id_trp_temp_b} {local_var(10)} {local_var(3)} "
        f"2119 3 {local_var(21)} {local_var(1)} 10 "
        f"32 2 {local_var(21)} 0 "
        # draw lines to child nodes
        f"2121 3 {local_var(22)} {local_var(1)} {local_var(21)} 2105 2 {local_var(22)} 10 "
        f"2120 3 {local_var(23)} {local_var(22)} 10 "
        f"6 3 {local_var(24)} {local_var(22)} {local_var(23)} "
        f"540 3 {id_trp_temp_a} {local_var(24)} {local_var(21)} "
        f"2123 3 {local_var(7)} {local_var(24)} 10 "
        f"2122 3 {local_var(25)} {local_var(7)} 170 2105 2 {local_var(25)} 60 "
        f"520 3 {local_var(26)} {id_trp_temp_c} {local_var(24)} "
        f"2120 3 {local_var(27)} {local_var(19)} 10 2106 2 {local_var(25)} 65 "
        f"1 6 {idx_prsnt_lines_to} {local_var(27)} {local_var(20)} {local_var(25)} {local_var(26)} 0 "
        f"3 0 "
        f"3 0 "
        f"500 3 {id_trp_temp_c} 100 {local_var(10)}"
    )
    new_scripts.append(("prsnt_culture_troop_tree", code_culture_tree))
    
    # 9. all_items_populate_category
    # Inputs: param1 = category (0=All, 1=Horses, 2=1H, 3=2H, 4=Polearms, 5=Bows, 6=Crossbows,
    #                          7=Arrows, 8=Bolts, 9=Thrown, 10=Shields, 11=Helmets, 12=Armor,
    #                          13=Boots, 14=Gloves, 15=Firearms, 16=Goods)
    code_populate_items = (
        f" 49 21 1 {local_var(0)} "
        f"2133 2 {local_var(1)} 0 " # count = 0
        f"6 3 {local_var(2)} 1 902 " # loop all 901 items
        f"1570 2 {local_var(3)} {local_var(2)} " # item_get_type
        f"2133 2 {local_var(4)} 0 " # include = 0
        f"4 0 31 2 {local_var(0)} 0 2133 2 {local_var(4)} 1 " # All
        f"5 0 31 2 {local_var(0)} 1 31 2 {local_var(3)} 0 2133 2 {local_var(4)} 1 " # Horses
        f"5 0 31 2 {local_var(0)} 2 31 2 {local_var(3)} 1 2133 2 {local_var(4)} 1 " # 1H
        f"5 0 31 2 {local_var(0)} 3 31 2 {local_var(3)} 2 2133 2 {local_var(4)} 1 " # 2H
        f"5 0 31 2 {local_var(0)} 4 31 2 {local_var(3)} 3 2133 2 {local_var(4)} 1 " # Polearm
        f"5 0 31 2 {local_var(0)} 5 31 2 {local_var(3)} 7 2133 2 {local_var(4)} 1 " # Bows
        f"5 0 31 2 {local_var(0)} 6 31 2 {local_var(3)} 8 2133 2 {local_var(4)} 1 " # Xbows
        f"5 0 31 2 {local_var(0)} 7 31 2 {local_var(3)} 4 2133 2 {local_var(4)} 1 " # Arrows
        f"5 0 31 2 {local_var(0)} 8 31 2 {local_var(3)} 5 2133 2 {local_var(4)} 1 " # Bolts
        f"5 0 31 2 {local_var(0)} 9 31 2 {local_var(3)} 9 2133 2 {local_var(4)} 1 " # Thrown
        f"5 0 31 2 {local_var(0)} 10 31 2 {local_var(3)} 6 2133 2 {local_var(4)} 1 " # Shields
        f"5 0 31 2 {local_var(0)} 11 31 2 {local_var(3)} 11 2133 2 {local_var(4)} 1 " # Helmets
        f"5 0 31 2 {local_var(0)} 12 31 2 {local_var(3)} 12 2133 2 {local_var(4)} 1 " # Armor
        f"5 0 31 2 {local_var(0)} 13 31 2 {local_var(3)} 13 2133 2 {local_var(4)} 1 " # Boots
        f"5 0 31 2 {local_var(0)} 14 31 2 {local_var(3)} 14 2133 2 {local_var(4)} 1 " # Gloves
        f"5 0 31 2 {local_var(0)} 15 " # Firearms
        f"4 0 1073741855 2 {local_var(3)} 15 1073741855 2 {local_var(3)} 16 31 2 {local_var(3)} 17 2133 2 {local_var(4)} 1 3 0 "
        f"5 0 31 2 {local_var(0)} 16 " # Goods & Books
        f"4 0 1073741855 2 {local_var(3)} 10 31 2 {local_var(3)} 19 2133 2 {local_var(4)} 1 3 0 "
        f"3 0 "
        f"4 0 31 2 {local_var(4)} 1 "
        f"2120 3 {local_var(5)} {local_var(1)} 2 " # slot starts at 2
        f"500 3 {id_trp_temp_c} {local_var(5)} {local_var(2)} "
        f"2105 2 {local_var(1)} 1 "
        f"3 0 "
        f"3 0 "
        f"500 3 {id_trp_temp_c} 0 {local_var(1)} " # slot 0 = total count
        f"2133 2 {reg(0)} {local_var(1)}"
    )
    new_scripts.append(("all_items_populate_category", code_populate_items))
    
    # Append scripts to script_lines
    scripts_to_append = []
    for s_name, s_code in new_scripts:
        if s_name not in existing_scripts:
            scripts_to_append.append(f"{s_name} -1\n{s_code} \n")
            script_count += 1
            existing_scripts[s_name] = script_count - 1
            
    if scripts_to_append:
        script_lines[1] = f"{script_count}\n"
        script_lines.extend(scripts_to_append)
        with open(scripts_path, "w", encoding="latin1") as f:
            f.writelines(script_lines)
        print(f"Updated scripts.txt: added {len(scripts_to_append)} scripts, total = {script_count}")

    # -------------------------------------------------------------
    # 5. Update presentations.txt
    # -------------------------------------------------------------
    prsnt_blocks = []
    
    # 1) prsnt_faction_troop_tree
    # Triggers: -60.000000 (load), -62.000000 (event), -61.000000 (run)
    # Root troops array for tree dropdown:
    # 0: 184 (Swadian/Hungary), 1: 198 (Vaegir/Moldavia), 2: 212 (Khergit/Ottoman),
    # 3: 222 (Nord/Wallachia), 4: 235 (Rhodok/Croatia), 5: 80 (Undead), 6: 84 (Burned),
    # 7: 88 (Putrid), 8: 92 (Preserved), 9: 97 (Demon), 10: 104 (Brollachan),
    # 11: 108 (Golem), 12: 248 (Looter), 13: 22 (Farmer), 14: 256 (Manhunter), 15: 266 (Peasant Woman)
    
    code_prsnt_troop_tree_load = (
        f"-60.000000 65 "
        f"902 1 999999 2124 1 1000 "
        # Done button
        f"940 2 {v_obj_21} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 885 730 2 1 30 926 2 {v_obj_21} 1 "
        # Title
        f"729 2 1 500 730 2 1 650 729 2 3 2000 730 2 3 2000 "
        f"910 3 {reg(0)} {qstr(existing_qs['qstr_faction_troop_tree'])} 16 " # tf_center_justify
        f"921 2 {reg(0)} 16711680 926 2 {reg(0)} 1 925 2 {reg(0)} 3 "
        # Combo box
        f"948 1 {v_obj_1} "
        f"729 2 1 500 730 2 1 600 926 2 {v_obj_1} 1 "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_hungary'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_moldavia'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_ottoman'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_wallachia'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_croatia'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_undead'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_burned'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_putrid'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_preserved'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_demons'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_brollachan'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_golem'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_outlaws'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_commoners'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_manhunters'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_women'])} "
        f"2112 3 {v_tree_sel} 0 15 "
        f"927 2 {v_obj_1} {v_tree_sel} "
        # Select root troop
        f"4 0 31 2 {v_tree_sel} 0 2133 2 {local_var(0)} 184 "
        f"5 0 31 2 {v_tree_sel} 1 2133 2 {local_var(0)} 198 "
        f"5 0 31 2 {v_tree_sel} 2 2133 2 {local_var(0)} 212 "
        f"5 0 31 2 {v_tree_sel} 3 2133 2 {local_var(0)} 222 "
        f"5 0 31 2 {v_tree_sel} 4 2133 2 {local_var(0)} 235 "
        f"5 0 31 2 {v_tree_sel} 5 2133 2 {local_var(0)} 80 "
        f"5 0 31 2 {v_tree_sel} 6 2133 2 {local_var(0)} 84 "
        f"5 0 31 2 {v_tree_sel} 7 2133 2 {local_var(0)} 88 "
        f"5 0 31 2 {v_tree_sel} 8 2133 2 {local_var(0)} 92 "
        f"5 0 31 2 {v_tree_sel} 9 2133 2 {local_var(0)} 97 "
        f"5 0 31 2 {v_tree_sel} 10 2133 2 {local_var(0)} 104 "
        f"5 0 31 2 {v_tree_sel} 11 2133 2 {local_var(0)} 108 "
        f"5 0 31 2 {v_tree_sel} 12 2133 2 {local_var(0)} 248 "
        f"5 0 31 2 {v_tree_sel} 13 2133 2 {local_var(0)} 22 "
        f"5 0 31 2 {v_tree_sel} 14 2133 2 {local_var(0)} 256 "
        f"5 0 2133 2 {local_var(0)} 266 3 0 "
        f"1 2 {idx_prsnt_culture_troop_tree} {local_var(0)}"
    )
    
    code_prsnt_troop_tree_event = (
        f"-62.000000 24 "
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} 2124 1 1000 "
        f"4 0 31 2 {local_var(0)} {v_obj_1} 2133 2 {v_tree_sel} {local_var(1)} 900 1 {idx_prsnt_troop_tree} "
        f"5 0 31 2 {local_var(0)} {v_obj_21} 902 1 0 "
        f"5 0 "
        f"520 3 {local_var(2)} {id_trp_temp_c} 100 2105 2 {local_var(2)} 1 2133 2 {local_var(3)} 0 "
        f"6 3 {local_var(4)} 101 {local_var(2)} "
        f"2147483680 2 {local_var(3)} 0 " # le 0
        f"540 3 {id_trp_temp_c} {local_var(4)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(4)} "
        f"3 0 "
        f"32 2 {local_var(3)} 0 2133 2 {v_temp} {local_var(3)} 2133 2 {v_next_prsnt} {idx_prsnt_troop_tree} 900 1 {idx_prsnt_troop_note} "
        f"3 0"
    )
    
    code_prsnt_troop_tree_run = (
        f"-61.000000 7 "
        f"4 0 1073741895 1 1 71 1 225 902 1 0 2060 1 4 3 0" # Esc (1) or Right Click (225) -> return to mnu_reports (index 4)
    )
    
    prsnt_blocks.append(f"prsnt_faction_troop_tree 0 {id_mesh_load_window} 3\n{code_prsnt_troop_tree_load} \n{code_prsnt_troop_tree_event} \n{code_prsnt_troop_tree_run} \n")
    
    # 2) prsnt_troop_note
    code_troop_note_load = (
        f"-60.000000 87 "
        f"902 1 999999 2124 1 1000 "
        f"1 3 {idx_copy_inventory} {v_temp} {id_trp_temp_a} "
        # Move equipped items to regular slots for display
        f"6 3 {local_var(0)} 0 10 "
        f"1541 3 {local_var(1)} {id_trp_temp_a} {local_var(0)} "
        f"32 2 {local_var(1)} -1 1530 2 {id_trp_temp_a} {local_var(1)} 1543 3 {id_trp_temp_a} {local_var(0)} -1 3 0 "
        # Done button
        f"940 2 {v_obj_1} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 900 730 2 1 25 926 2 {v_obj_1} 1 "
        # 3D Model
        f"2122 3 {local_var(2)} {v_temp} 2 "
        f"939 4 {reg(0)} -1 {id_tab_party} {local_var(2)} "
        f"729 2 1 750 730 2 1 1000 925 2 {reg(0)} 1 "
        f"729 2 1 750 730 2 1 350 926 2 {reg(0)} 1 "
        # Name, level, hp
        f"2322 2 1 {v_temp} "
        f"2171 2 {local_var(3)} {v_temp} 2133 2 {reg(1)} {local_var(3)} "
        f"1 2 {idx_get_troop_max_hp} {v_temp} "
        f"910 3 {reg(0)} {qstr(existing_qs['qstr_troop_note_name_lvl'])} 2048 " # tf_double_space
        f"729 2 1 500 730 2 1 500 926 2 {reg(0)} 1 "
        # Stats 1
        f"2172 3 {reg(1)} {v_temp} 0 " # STR
        f"2172 3 {reg(2)} {v_temp} 2 " # INT
        f"2170 3 {reg(3)} 22 {v_temp} " # Power Strike
        f"2170 3 {reg(4)} 24 {v_temp} " # Power Draw
        f"2170 3 {reg(5)} 23 {v_temp} " # Power Throw
        f"2170 3 {reg(6)} 27 {v_temp} " # Horse Archery
        f"2176 3 {reg(7)} {v_temp} 0 " # 1H
        f"2176 3 {reg(8)} {v_temp} 1 " # 2H
        f"2176 3 {reg(9)} {v_temp} 2 " # Polearms
        f"910 3 {reg(0)} {qstr(existing_qs['qstr_troop_note_attr'])} 2048 "
        f"729 2 1 500 730 2 1 100 926 2 {reg(0)} 1 "
        # Stats 2
        f"2172 3 {reg(1)} {v_temp} 1 " # AGI
        f"2172 3 {reg(2)} {v_temp} 3 " # CHA
        f"2170 3 {reg(3)} 21 {v_temp} " # Shield
        f"2170 3 {reg(4)} 20 {v_temp} " # Athletics
        f"2170 3 {reg(5)} 19 {v_temp} " # Riding
        f"2176 3 {reg(6)} {v_temp} 3 " # Archery
        f"2176 3 {reg(7)} {v_temp} 4 " # Crossbow
        f"2176 3 {reg(8)} {v_temp} 5 " # Throwing
        f"910 3 {reg(0)} {qstr(existing_qs['qstr_troop_note_attr2'])} 2048 "
        f"729 2 1 710 730 2 1 100 926 2 {reg(0)} 1 "
        # Equipment inventory grid
        f"910 3 {reg(1)} {qstr(existing_qs['qstr_troop_note_equip'])} 4096 "
        f"729 2 1 50 730 2 1 590 926 2 {reg(1)} 1 "
        f"2133 2 {local_var(4)} 50 2133 2 {local_var(5)} 520 2133 2 {local_var(6)} 10 "
        f"6 3 {local_var(7)} 0 6 " # 6 rows
        f"6 3 {local_var(8)} 0 4 " # 4 cols
        f"911 2 {reg(1)} {id_mesh_mp_inventory_choose} "
        f"729 2 1 640 730 2 1 640 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(4)} 730 2 1 {local_var(5)} 926 2 {reg(1)} 1 "
        f"500 3 {id_trp_temp_a} {local_var(6)} {reg(1)} "
        f"1541 3 {local_var(9)} {id_trp_temp_a} {local_var(6)} "
        f"4 0 32 2 {local_var(9)} -1 "
        f"944 2 {reg(2)} {local_var(9)} "
        f"729 2 1 800 730 2 1 800 925 2 {reg(2)} 1 "
        f"2120 3 {local_var(10)} {local_var(4)} 40 2120 3 {local_var(11)} {local_var(5)} 40 "
        f"729 2 1 {local_var(10)} 730 2 1 {local_var(11)} 926 2 {reg(2)} 1 "
        f"500 3 {id_trp_temp_b} {local_var(6)} {local_var(9)} 3 0 "
        f"2105 2 {local_var(4)} 80 2105 2 {local_var(6)} 1 3 0 "
        f"2133 2 {local_var(4)} 50 2106 2 {local_var(5)} 80 3 0"
    )
    
    code_troop_note_hover = (
        f"-63.000000 24 "
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        f"4 0 31 2 {local_var(1)} 0 " # mouse enter
        f"6 3 {local_var(2)} 10 34 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(2)} "
        f"4 0 32 2 {local_var(3)} 0 "
        f"972 4 {local_var(3)} 0 0 100 " # show_item_details_with_modifier
        f"2133 2 {v_tooltip_slot} {local_var(2)} "
        f"3 0 3 0 "
        f"5 0 " # mouse exit
        f"6 3 {local_var(2)} 10 34 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"4 0 31 2 {v_tooltip_slot} {local_var(2)} 971 0 3 0 " # close_item_details
        f"3 0 3 0"
    )
    
    code_troop_note_event = (
        f"-62.000000 8 "
        f"2071 1 {local_var(0)} "
        f"4 0 31 2 {local_var(0)} {v_obj_1} "
        f"4 0 32 2 {v_next_prsnt} 0 900 1 {v_next_prsnt} 5 0 902 1 0 3 0 "
        f"3 0"
    )
    
    code_troop_note_run = (
        f"-61.000000 8 "
        f"4 0 1073741895 1 1 71 1 225 "
        f"4 0 32 2 {v_next_prsnt} 0 900 1 {v_next_prsnt} 5 0 902 1 0 3 0 "
        f"3 0"
    )
    
    prsnt_blocks.append(f"prsnt_troop_note 0 {id_mesh_load_window} 4\n{code_troop_note_load} \n{code_troop_note_hover} \n{code_troop_note_event} \n{code_troop_note_run} \n")
    
    # 3) prsnt_all_items
    code_all_items_load = (
        f"-60.000000 85 "
        f"902 1 999999 2124 1 1000 "
        # Populate items for category
        f"1 2 {idx_all_items_populate} {v_cat} "
        f"520 3 {local_var(0)} {id_trp_temp_c} 0 " # total items
        # calculate max pages
        f"2120 3 {local_var(1)} {local_var(0)} 55 2108 2 {local_var(1)} 56 "
        f"2111 2 {local_var(1)} 1 " # at least 1 page
        f"2121 3 {local_var(2)} {local_var(1)} 1 "
        f"2112 3 {v_page} 0 {local_var(2)} " # clamp page
        # Background
        f"911 2 {reg(1)} {id_mesh_load_window} 729 2 1 0 730 2 1 0 926 2 {reg(1)} 1 "
        # Title
        f"910 3 {reg(1)} {qstr(existing_qs['qstr_all_items_title'])} 16 "
        f"729 2 1 500 730 2 1 670 926 2 {reg(1)} 1 "
        # Category Selector
        f"916 1 {v_cat_sel} " # combo button
        f"729 2 1 140 730 2 1 665 926 2 {v_cat_sel} 1 "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_all'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_horses'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_1h'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_2h'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_polearms'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_bows'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_crossbows'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_arrows'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_bolts'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_thrown'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_shields'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_helmets'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_armor'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_boots'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_gloves'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_firearms'])} "
        f"931 2 {v_cat_sel} {qstr(existing_qs['qstr_cat_goods'])} "
        f"927 2 {v_cat_sel} {v_cat} "
        # Prev / Next / Page Info
        f"940 2 {v_prev_btn} {qstr(existing_qs['qstr_prev_page'])} "
        f"729 2 1 370 730 2 1 660 926 2 {v_prev_btn} 1 "
        f"2120 3 {reg(0)} {v_page} 1 2133 2 {reg(1)} {local_var(1)} 2133 2 {reg(2)} {local_var(0)} "
        f"910 3 {reg(3)} {qstr(existing_qs['qstr_page_str'])} 16 "
        f"729 2 1 520 730 2 1 665 926 2 {reg(3)} 1 "
        f"940 2 {v_next_btn} {qstr(existing_qs['qstr_next_page'])} "
        f"729 2 1 670 730 2 1 660 926 2 {v_next_btn} 1 "
        # Done button
        f"940 2 {v_done_btn} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 890 730 2 1 660 926 2 {v_done_btn} 1 "
        # 56 grid slots: 8 cols x 7 rows
        f"2133 2 {local_var(3)} 40 2133 2 {local_var(4)} 560 2133 2 {local_var(5)} 1 "
        f"6 3 {local_var(6)} 0 7 " # 7 rows
        f"6 3 {local_var(7)} 0 8 " # 8 cols
        f"2122 3 {local_var(8)} {v_page} 56 2105 2 {local_var(8)} {local_var(5)} 2105 2 {local_var(8)} 1 " # index in array
        f"520 3 {local_var(9)} {id_trp_temp_c} {local_var(8)} " # item id
        f"913 3 {reg(1)} {id_mesh_mp_inventory_choose} {id_mesh_mp_inventory_choose} "
        f"729 2 1 640 730 2 1 640 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(3)} 730 2 1 {local_var(4)} 926 2 {reg(1)} 1 "
        f"500 3 {id_trp_temp_a} {local_var(5)} {reg(1)} "
        f"500 3 {id_trp_temp_b} {local_var(5)} {local_var(9)} "
        f"4 0 32 2 {local_var(9)} 0 "
        f"944 2 {reg(2)} {local_var(9)} "
        f"729 2 1 800 730 2 1 800 925 2 {reg(2)} 1 "
        f"2120 3 {local_var(10)} {local_var(3)} 40 2120 3 {local_var(11)} {local_var(4)} 40 "
        f"729 2 1 {local_var(10)} 730 2 1 {local_var(11)} 926 2 {reg(2)} 1 "
        f"3 0 "
        f"2105 2 {local_var(3)} 80 2105 2 {local_var(5)} 1 3 0 "
        f"2133 2 {local_var(3)} 40 2106 2 {local_var(4)} 80 3 0 "
        # Right Preview Box
        f"4 0 2147483680 2 {v_sel_item} 0 " # if sel <= 0, pick first
        f"520 3 {v_sel_item} {id_trp_temp_b} 1 3 0 "
        f"911 2 {reg(1)} {id_mesh_mp_inventory_choose} "
        f"729 2 1 1800 730 2 1 1800 925 2 {reg(1)} 1 "
        f"729 2 1 730 730 2 1 360 926 2 {reg(1)} 1 "
        f"4 0 32 2 {v_sel_item} 0 "
        f"944 2 {reg(2)} {v_sel_item} "
        f"729 2 1 2400 730 2 1 2400 925 2 {reg(2)} 1 "
        f"729 2 1 840 730 2 1 470 926 2 {reg(2)} 1 "
        f"2325 2 1 {v_sel_item} " # item name
        f"910 3 {reg(3)} {str_id(1)} 16 "
        f"729 2 1 840 730 2 1 320 926 2 {reg(3)} 1 "
        # Get button
        f"940 2 {v_get_btn} {qstr(existing_qs['qstr_get_item'])} "
        f"729 2 1 780 730 2 1 240 926 2 {v_get_btn} 1 3 0"
    )
    
    code_all_items_hover = (
        f"-63.000000 24 "
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        f"4 0 31 2 {local_var(1)} 0 " # mouse enter
        f"6 3 {local_var(2)} 1 57 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(2)} "
        f"4 0 32 2 {local_var(3)} 0 "
        f"972 4 {local_var(3)} {v_imod} 0 100 "
        f"2133 2 {v_tooltip_slot} {local_var(2)} "
        f"3 0 3 0 "
        f"5 0 " # mouse exit
        f"6 3 {local_var(2)} 1 57 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"4 0 31 2 {v_tooltip_slot} {local_var(2)} 971 0 3 0 "
        f"3 0 3 0"
    )
    
    code_all_items_event = (
        f"-62.000000 37 "
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        # Category change
        f"4 0 31 2 {local_var(0)} {v_cat_sel} "
        f"2133 2 {v_cat} {local_var(1)} 2133 2 {v_page} 0 2133 2 {v_sel_item} 0 900 1 {idx_prsnt_all_items} "
        # Prev page
        f"5 0 31 2 {local_var(0)} {v_prev_btn} "
        f"2106 2 {v_page} 1 2111 2 {v_page} 0 900 1 {idx_prsnt_all_items} "
        # Next page
        f"5 0 31 2 {local_var(0)} {v_next_btn} "
        f"2105 2 {v_page} 1 900 1 {idx_prsnt_all_items} "
        # Done button
        f"5 0 31 2 {local_var(0)} {v_done_btn} "
        f"902 1 0 "
        # Get button
        f"5 0 31 2 {local_var(0)} {v_get_btn} "
        f"4 0 32 2 {v_sel_item} 0 "
        f"1530 3 {id_trp_player} {v_sel_item} {v_imod} "
        f"2325 2 1 {v_sel_item} "
        f"1106 1 {qstr(existing_qs['qstr_added_item'])} 3 0 "
        # Grid slot click
        f"5 0 "
        f"6 3 {local_var(2)} 1 57 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(2)} "
        f"4 0 32 2 {local_var(3)} 0 2133 2 {v_sel_item} {local_var(3)} 900 1 {idx_prsnt_all_items} 3 0 "
        f"3 0 "
        f"3 0"
    )
    
    code_all_items_run = (
        f"-61.000000 7 "
        f"4 0 1073741895 1 1 71 1 225 902 1 0 2060 1 4 3 0" # Esc / Right click -> mnu_reports
    )
    
    prsnt_blocks.append(f"prsnt_all_items 0 {id_mesh_load_window} 4\n{code_all_items_load} \n{code_all_items_hover} \n{code_all_items_event} \n{code_all_items_run} \n")
    
    # Append presentations to presentations.txt
    prsnt_to_append = []
    if "prsnt_faction_troop_tree" not in existing_prsnts:
        prsnt_to_append.append(prsnt_blocks[0])
        prsnt_count += 1
    if "prsnt_troop_note" not in existing_prsnts:
        prsnt_to_append.append(prsnt_blocks[1])
        prsnt_count += 1
    if "prsnt_all_items" not in existing_prsnts:
        prsnt_to_append.append(prsnt_blocks[2])
        prsnt_count += 1
        
    if prsnt_to_append:
        prsnt_lines[1] = f" {prsnt_count}\n"
        prsnt_lines.extend(prsnt_to_append)
        with open(prsnt_path, "w", encoding="latin1") as f:
            f.writelines(prsnt_lines)
        print(f"Updated presentations.txt: added {len(prsnt_to_append)} presentations, total = {prsnt_count}")

    # -------------------------------------------------------------
    # 6. Update menus.txt under menu_reports
    # -------------------------------------------------------------
    menus_path = os.path.join(MODULE_DIR, "menus.txt")
    backup_file(menus_path)
    with open(menus_path, "r", encoding="latin1") as f:
        menus_content = f.read()
        
    target_needle = "mno_resume_travelling  0  Resume_travelling.  1 2040 0  ."
    menu_reports_pos = menus_content.find("menu_reports ")
    
    if menu_reports_pos != -1:
        # Find the number of menu items in menu_reports
        # Pattern: menu_reports <flags> <text> <mesh> <num_operations> ... <num_menu_items>
        # Let's inspect the menu header
        resume_pos = menus_content.find(target_needle, menu_reports_pos)
        if resume_pos != -1 and "mno_troop_tree_viewer" not in menus_content[menu_reports_pos:resume_pos]:
            # Construct the new menu items
            # mno_troop_tree_viewer: calls start_presentation(prsnt_faction_troop_tree)
            # mno_all_items: calls start_presentation(prsnt_all_items)
            new_menu_items = (
                f" mno_troop_tree_viewer  0  View_troop_trees.  1 900 1 {idx_prsnt_troop_tree}  . "
                f" mno_all_items  0  View_all_items.  2 2133 2 {v_temp} 0 900 1 {idx_prsnt_all_items}  . "
            )
            
            # Find the number of menu options right before the first mno_
            first_mno = menus_content.find(" mno_", menu_reports_pos)
            pre_mno_text = menus_content[menu_reports_pos:first_mno]
            tokens = pre_mno_text.split()
            old_num_options = int(tokens[-1])
            new_num_options = old_num_options + 2
            
            # Replace old_num_options with new_num_options
            last_space = pre_mno_text.rfind(str(old_num_options))
            updated_header = pre_mno_text[:last_space] + str(new_num_options)
            
            # Splice
            menus_content = (
                menus_content[:menu_reports_pos] +
                updated_header +
                menus_content[first_mno:resume_pos] +
                new_menu_items +
                menus_content[resume_pos:]
            )
            
            with open(menus_path, "w", encoding="latin1") as f:
                f.write(menus_content)
            print(f"Updated menus.txt: added troop_tree_viewer and all_items into menu_reports (options: {old_num_options} -> {new_num_options})")
        else:
            print("menu_reports already contains troop tree viewer or resume_travelling not found.")

    # -------------------------------------------------------------
    # 7. Add translations to languages/cns/
    # -------------------------------------------------------------
    cns_menus_csv = os.path.join(MODULE_DIR, "languages/cns/game_menus.csv")
    if os.path.exists(cns_menus_csv):
        with open(cns_menus_csv, "r", encoding="utf-8", errors="ignore") as f:
            cns_menus = f.read()
        if "mno_troop_tree_viewer" not in cns_menus:
            with open(cns_menus_csv, "a", encoding="utf-8") as f:
                f.write("mno_troop_tree_viewer|查看兵种升级树\n")
                f.write("mno_all_items|查看所有装备物品\n")
            print("Added Chinese translations to game_menus.csv")

    cns_qs_csv = os.path.join(MODULE_DIR, "languages/cns/quick_strings.csv")
    if os.path.exists(cns_qs_csv):
        with open(cns_qs_csv, "r", encoding="utf-8", errors="ignore") as f:
            cns_qs = f.read()
        
        qs_translations = [
            ("qstr_faction_troop_tree", "兵种升级树"),
            ("qstr_view_troop_trees", "查看兵种升级树"),
            ("qstr_view_all_items", "查看所有装备物品"),
            ("qstr_all_items_title", "装备与物品查看器"),
            ("qstr_done", "完成 / 返回"),
            ("qstr_prev_page", "< 前一页"),
            ("qstr_next_page", "后一页 >"),
            ("qstr_get_item", "获取该装备"),
            ("qstr_added_item", "已将 {s1} 放入玩家物品栏。"),
            ("qstr_page_str", "第 {reg0} / {reg1} 页 (共 {reg2} 件物品)"),
            ("qstr_tree_hungary", "匈牙利王国"),
            ("qstr_tree_moldavia", "摩尔达维亚公国"),
            ("qstr_tree_ottoman", "奥斯曼帝国"),
            ("qstr_tree_wallachia", "瓦拉几亚公国"),
            ("qstr_tree_croatia", "克罗地亚王国"),
            ("qstr_tree_undead", "死灵/普通丧尸"),
            ("qstr_tree_burned", "烈焰丧尸"),
            ("qstr_tree_putrid", "腐烂丧尸"),
            ("qstr_tree_preserved", "不朽防腐丧尸"),
            ("qstr_tree_demons", "恶魔军团"),
            ("qstr_tree_brollachan", "暗影异形"),
            ("qstr_tree_golem", "魔像傀儡"),
            ("qstr_tree_outlaws", "强盗与不法之徒"),
            ("qstr_tree_commoners", "平民与雇佣军"),
            ("qstr_tree_manhunters", "赏金猎人"),
            ("qstr_tree_women", "难民与女剑士"),
            ("qstr_cat_all", "全部装备与物品"),
            ("qstr_cat_horses", "战马坐骑"),
            ("qstr_cat_1h", "单手武器"),
            ("qstr_cat_2h", "双手武器"),
            ("qstr_cat_polearms", "长杆武器"),
            ("qstr_cat_bows", "弓"),
            ("qstr_cat_arrows", "箭矢"),
            ("qstr_cat_crossbows", "弩"),
            ("qstr_cat_bolts", "弩矢"),
            ("qstr_cat_thrown", "投掷武器"),
            ("qstr_cat_shields", "盾牌"),
            ("qstr_cat_helmets", "头盔防具"),
            ("qstr_cat_armor", "身体铠甲"),
            ("qstr_cat_boots", "腿部防具"),
            ("qstr_cat_gloves", "手套防具"),
            ("qstr_cat_firearms", "火器与弹药"),
            ("qstr_cat_goods", "商品与书籍"),
            ("qstr_troop_note_name_lvl", "姓名: {s1}^等级: {reg1}^生命值: {reg0}"),
            ("qstr_troop_note_attr", "基础属性:^力量: {reg1}^智力: {reg2}^^技能:^强击: {reg3}^强弓: {reg4}^强掷: {reg5}^骑射: {reg6}^^武器熟练度:^单手武器: {reg7}^双手武器: {reg8}^长杆武器: {reg9}"),
            ("qstr_troop_note_attr2", "敏捷: {reg1}^魅力: {reg2}^^盾防: {reg3}^跑动: {reg4}^骑术: {reg5}^^弓箭: {reg6}^弩箭: {reg7}^投掷: {reg8}"),
            ("qstr_troop_note_equip", "装备清单:"),
        ]
        
        with open(cns_qs_csv, "a", encoding="utf-8") as f:
            for k, v in qs_translations:
                if k not in cns_qs:
                    f.write(f"{k}|{v}\n")
        print("Added Chinese translations to quick_strings.csv")

    print("=== Installation Finished Successfully ===")

if __name__ == "__main__":
    main()
