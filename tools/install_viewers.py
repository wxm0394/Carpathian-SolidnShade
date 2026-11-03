import os, sys, shutil

MODULE_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
SOURCE_1866 = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/1866_Ultimate_WB"

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

def reg(n): return OPMASK_REGISTER + n
def local_var(n): return OPMASK_LOCAL_VARIABLE + n
def global_var(n): return OPMASK_VARIABLE + n
def qstr(n): return OPMASK_QUICK_STRING + n
def str_id(n): return OPMASK_STRING + n
def script_id(n): return OPMASK_SCRIPT + n
def prsnt_id(n): return OPMASK_PRESENTATION + n
def troop_id(n): return OPMASK_TROOP + n

def make_op_block(raw_str):
    toks = raw_str.split()
    idx = 0
    ops = []
    while idx < len(toks):
        op = int(toks[idx])
        nargs = int(toks[idx+1])
        if idx + 2 + nargs > len(toks):
            raise ValueError(f"Truncated statement at idx {idx}: op {op}, nargs {nargs}, remaining {len(toks)-(idx+2)}")
        args = toks[idx+2 : idx+2+nargs]
        ops.append((op, nargs, args))
        idx += 2 + nargs
    return f"{len(ops)} {' '.join(toks)}"

def make_trigger(interval, raw_str):
    return f"{interval:.6f}  {make_op_block(raw_str)}"

def verify_scripts_file(path):
    with open(path, "r", encoding="latin1") as f:
        tokens = f.read().split()
    assert tokens[0] == "scriptsfile" and tokens[1] == "version"
    num_scripts = int(tokens[3])
    idx = 4
    for s in range(num_scripts):
        s_name = tokens[idx]
        idx += 1
        flag = int(tokens[idx])
        idx += 1
        num_ops = int(tokens[idx])
        idx += 1
        for _ in range(num_ops):
            op = int(tokens[idx])
            idx += 1
            nargs = int(tokens[idx])
            idx += 1
            idx += nargs
    assert idx == len(tokens), f"Scripts file verification mismatch: parsed {idx} tokens, file has {len(tokens)}"
    print(f"Verified scripts.txt: {num_scripts} scripts, total {len(tokens)} tokens, 100% OK.")

def verify_presentations_file(path):
    with open(path, "r", encoding="latin1") as f:
        tokens = f.read().split()
    assert tokens[0] == "presentationsfile" and tokens[1] == "version"
    num_prsnt = int(tokens[3])
    idx = 4
    for p in range(num_prsnt):
        p_name = tokens[idx]
        idx += 1
        flags = int(tokens[idx])
        idx += 1
        mesh = int(tokens[idx])
        idx += 1
        num_triggers = int(tokens[idx])
        idx += 1
        for _ in range(num_triggers):
            interval = tokens[idx]
            idx += 1
            num_ops = int(tokens[idx])
            idx += 1
            for _ in range(num_ops):
                op = int(tokens[idx])
                idx += 1
                nargs = int(tokens[idx])
                idx += 1
                idx += nargs
    assert idx == len(tokens), f"Presentations file verification mismatch: parsed {idx} tokens, file has {len(tokens)}"
    print(f"Verified presentations.txt: {num_prsnt} presentations, total {len(tokens)} tokens, 100% OK.")

def run():
    print("=== Generating Perfect Viewers for Carpathian Solid & Shade ===")

    # 1. meshes.txt
    mesh_path = os.path.join(MODULE_DIR, "meshes.txt")
    with open(mesh_path, "r", encoding="latin1") as f:
        mesh_lines = f.readlines()
    mesh_count = int(mesh_lines[0].strip())
    existing_meshes = {}
    for i, line in enumerate(mesh_lines[1:]):
        parts = line.split()
        if parts:
            existing_meshes[parts[0]] = i
            
    needed_meshes = [
        ("mesh_white_plane", "white_plane 0"),
        ("mesh_load_window", "load_window 0"),
        ("mesh_mp_inventory_choose", "mp_inventory_choose 0"),
        ("mesh_note_window", "note_window 0"),
    ]
    mesh_added = False
    for m_id, m_line in needed_meshes:
        if m_id not in existing_meshes:
            existing_meshes[m_id] = mesh_count
            mesh_lines.append(f"{m_id} {m_line}\r\n")
            mesh_count += 1
            mesh_added = True
    if mesh_added:
        mesh_lines[0] = f"{mesh_count}\r\n"
        with open(mesh_path, "w", encoding="latin1") as f:
            f.writelines(mesh_lines)
        print(f"Updated meshes.txt: count = {mesh_count}")
    
    id_mesh_white_plane = existing_meshes["mesh_white_plane"]
    id_mesh_load_window = existing_meshes["mesh_load_window"]
    id_mesh_mp_inventory_choose = existing_meshes["mesh_mp_inventory_choose"]

    # 2. variables.txt
    var_path = os.path.join(MODULE_DIR, "variables.txt")
    with open(var_path, "r", encoding="latin1") as f:
        var_lines = f.readlines()
    existing_vars = {l.strip(): i for i, l in enumerate(var_lines) if l.strip()}
    
    needed_vars = [
        "g_presentation_obj_1",
        "g_presentation_obj_21",
        "g_presentation_troop_tree_selection",
        "temp",
        "next_prsnt",
        "g_all_items_page_no",
        "g_all_items_category",
        "g_all_items_selected_item",
        "g_all_items_imod",
        "g_all_items_obj_cat_sel",
        "g_all_items_obj_prev_btn",
        "g_all_items_obj_next_btn",
        "g_all_items_obj_done_btn",
        "g_all_items_obj_get_btn",
        "g_all_items_tooltip_slot"
    ]
    var_added = False
    for v in needed_vars:
        if v not in existing_vars:
            existing_vars[v] = len(var_lines)
            var_lines.append(v + "\r\n")
            var_added = True
    if var_added:
        with open(var_path, "w", encoding="latin1") as f:
            f.writelines(var_lines)
        print(f"Updated variables.txt: total vars = {len(var_lines)}")
        
    v_obj_1 = global_var(existing_vars["g_presentation_obj_1"])
    v_obj_21 = global_var(existing_vars["g_presentation_obj_21"])
    v_tree_sel = global_var(existing_vars["g_presentation_troop_tree_selection"])
    v_temp = global_var(existing_vars["temp"])
    v_next_prsnt = global_var(existing_vars["next_prsnt"])
    v_page = global_var(existing_vars["g_all_items_page_no"])
    v_cat = global_var(existing_vars["g_all_items_category"])
    v_sel_item = global_var(existing_vars["g_all_items_selected_item"])
    v_imod = global_var(existing_vars["g_all_items_imod"])
    v_cat_sel = global_var(existing_vars["g_all_items_obj_cat_sel"])
    v_prev_btn = global_var(existing_vars["g_all_items_obj_prev_btn"])
    v_next_btn = global_var(existing_vars["g_all_items_obj_next_btn"])
    v_done_btn = global_var(existing_vars["g_all_items_obj_done_btn"])
    v_get_btn = global_var(existing_vars["g_all_items_obj_get_btn"])
    v_tooltip_slot = global_var(existing_vars["g_all_items_tooltip_slot"])

    # 3. quick_strings.txt
    qs_path = os.path.join(MODULE_DIR, "quick_strings.txt")
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
        ("qstr_tree_townsmen", "qstr_tree_townsmen Townsmen_&_Mercenaries"),
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
    for q_id, q_line in needed_qs:
        if q_id not in existing_qs:
            existing_qs[q_id] = qs_count
            qs_lines.append(q_line + "\r\n")
            qs_count += 1
            qs_added = True
    if qs_added:
        qs_lines[0] = f"{qs_count}\r\n"
        with open(qs_path, "w", encoding="latin1") as f:
            f.writelines(qs_lines)
        print(f"Updated quick_strings.txt: count = {qs_count}")

    # Troops
    troops_path = os.path.join(MODULE_DIR, "troops.txt")
    with open(troops_path, "r", encoding="latin1") as f:
        t_records = f.read().split("\ntrp_")
    t_map = {}
    for idx, r in enumerate(t_records[1:]):
        tid = "trp_" + r.split()[0]
        t_map[tid] = idx
    
    id_trp_temp_a = troop_id(t_map["trp_temp_array_a"])
    id_trp_temp_b = troop_id(t_map["trp_temp_array_b"])
    id_trp_temp_c = troop_id(t_map["trp_temp_array_c"])
    id_trp_player = troop_id(t_map["trp_player"])

    # Base counts from clean orig backups
    script_orig_path = os.path.join(MODULE_DIR, "scripts.txt.orig_pre_viewers")
    with open(script_orig_path, "r", encoding="latin1") as f:
        script_orig_lines = f.readlines()
    script_count_orig = int(script_orig_lines[1].strip())
    
    idx_prsnt_lines = script_count_orig
    idx_prsnt_lines_to = idx_prsnt_lines + 1
    idx_upgrade_tree_troop_and_name = idx_prsnt_lines_to + 1
    idx_upgrade_tree_troop_cost = idx_upgrade_tree_troop_and_name + 1
    idx_get_max_hp = idx_upgrade_tree_troop_cost + 1
    idx_copy_inventory = idx_get_max_hp + 1
    idx_game_get_upgrade_cost = idx_copy_inventory + 1
    idx_prsnt_culture_troop_tree = idx_game_get_upgrade_cost + 1
    idx_all_items_populate = idx_prsnt_culture_troop_tree + 1
    
    prsnt_orig_path = os.path.join(MODULE_DIR, "presentations.txt.orig_pre_viewers")
    with open(prsnt_orig_path, "r", encoding="latin1") as f:
        prsnt_orig_lines = f.readlines()
    prsnt_count_orig = int(prsnt_orig_lines[1].strip())
    
    idx_prsnt_troop_tree = prsnt_count_orig
    idx_prsnt_troop_note = idx_prsnt_troop_tree + 1
    idx_prsnt_all_items = idx_prsnt_troop_note + 1
    
    id_tab_party = 2 # tab_game_party_window

    print(f"Base counts: scripts={script_count_orig}, prsnts={prsnt_count_orig}")

    # 4. Generate new scripts
    new_scripts = []
    
    # 1. prsnt_lines (15 ops)
    code_prsnt_lines = make_op_block(
        f"23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 23 2 {local_var(3)} 4 23 2 {local_var(4)} 5 "
        f"911 2 {reg(1)} {id_mesh_white_plane} "
        f"2107 2 {local_var(0)} 50 2107 2 {local_var(1)} 50 "
        f"729 2 0 {local_var(0)} 730 2 0 {local_var(1)} 925 2 {reg(1)} 0 "
        f"729 2 0 {local_var(2)} 730 2 0 {local_var(3)} 926 2 {reg(1)} 0 "
        f"921 2 {reg(1)} {local_var(4)}"
    )
    new_scripts.append(("prsnt_lines", f" {code_prsnt_lines}"))
    
    # 2. prsnt_lines_to (25 ops)
    code_lines_to = make_op_block(
        f"23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 23 2 {local_var(3)} 4 23 2 {local_var(4)} 5 "
        f"4 0 31 2 {local_var(0)} {local_var(2)} "
        f"2121 3 {local_var(5)} {local_var(1)} {local_var(3)} 2113 1 {local_var(5)} 2110 2 {local_var(1)} {local_var(3)} "
        f"1 6 {idx_prsnt_lines} 4 {local_var(5)} {local_var(0)} {local_var(1)} {local_var(4)} "
        f"5 0 31 2 {local_var(1)} {local_var(3)} "
        f"2121 3 {local_var(5)} {local_var(0)} {local_var(2)} 2113 1 {local_var(5)} 2110 2 {local_var(0)} {local_var(2)} "
        f"1 6 {idx_prsnt_lines} {local_var(5)} 4 {local_var(0)} {local_var(1)} {local_var(4)} "
        f"5 0 "
        f"2120 3 {local_var(6)} {local_var(0)} {local_var(2)} 2108 2 {local_var(6)} 2 2106 2 {local_var(6)} 6 "
        f"1 6 {idx_prsnt_lines} {local_var(0)} {local_var(1)} {local_var(6)} {local_var(1)} {local_var(4)} "
        f"1 6 {idx_prsnt_lines} {local_var(6)} {local_var(1)} {local_var(6)} {local_var(3)} {local_var(4)} "
        f"1 6 {idx_prsnt_lines} {local_var(6)} {local_var(3)} {local_var(2)} {local_var(3)} {local_var(4)} "
        f"3 0"
    )
    new_scripts.append(("prsnt_lines_to", f" {code_lines_to}"))
    
    # 3. prsnt_upgrade_tree_troop_and_name (40 ops)
    code_troop_name = make_op_block(
        f"23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 23 2 {local_var(3)} 4 "
        f"2322 2 1 {local_var(0)} "
        f"910 3 {reg(1)} {qstr(6)} 4112 "
        f"4 0 2147483678 2 {local_var(3)} 100 "
        f"729 2 1 480 730 2 1 480 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1 "
        f"2106 2 {local_var(1)} 42 2122 3 {local_var(4)} {local_var(0)} 2 "
        f"938 4 {reg(1)} -1 {(TAG_TABLEAU<<56)+id_tab_party} {local_var(4)} "
        f"729 2 1 300 730 2 1 400 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1 "
        f"5 0 "
        f"729 2 1 600 730 2 1 600 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1 "
        f"2106 2 {local_var(1)} 52 2122 3 {local_var(4)} {local_var(0)} 2 "
        f"938 4 {reg(1)} -1 {(TAG_TABLEAU<<56)+id_tab_party} {local_var(4)} "
        f"729 2 1 375 730 2 1 500 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1 "
        f"3 0"
    )
    new_scripts.append(("prsnt_upgrade_tree_troop_and_name", f" {code_troop_name}"))
    
    # 4. prsnt_upgrade_tree_troop_cost (11 ops)
    code_cost = make_op_block(
        f"23 2 {local_var(0)} 1 23 2 {local_var(1)} 2 23 2 {local_var(2)} 3 "
        f"1 2 {idx_game_get_upgrade_cost} {local_var(0)} "
        f"910 3 {reg(1)} {qstr(44)} 4100 "
        f"729 2 1 {local_var(1)} 730 2 1 {local_var(2)} 926 2 {reg(1)} 1 "
        f"729 2 1 600 730 2 1 600 925 2 {reg(1)} 1"
    )
    new_scripts.append(("prsnt_upgrade_tree_troop_cost", f" {code_cost}"))

    # 5. get_troop_max_hp
    code_hp = make_op_block(
        f"21 1 {local_var(0)} 2172 3 {local_var(1)} {local_var(0)} 0 "
        f"2170 3 {local_var(2)} {local_var(0)} 7 "
        f"2122 3 {reg(0)} {local_var(2)} 2 2105 2 {reg(0)} {local_var(1)} 2105 2 {reg(0)} 35"
    )
    new_scripts.append(("get_troop_max_hp", f" {code_hp}"))

    # 6. copy_inventory
    code_copy_inv = make_op_block(
        f"21 1 {local_var(0)} 21 1 {local_var(1)} "
        f"6 3 {local_var(2)} 0 10 "
        f"1543 3 {local_var(1)} {local_var(2)} -1 "
        f"3 0 "
        f"6 3 {local_var(2)} 0 10 "
        f"1541 3 {local_var(3)} {local_var(0)} {local_var(2)} "
        f"32 2 {local_var(3)} -1 "
        f"1543 3 {local_var(1)} {local_var(2)} {local_var(3)} "
        f"3 0"
    )
    new_scripts.append(("copy_inventory", f" {code_copy_inv}"))

    # 7. game_get_upgrade_cost
    code_upgrade_cost = make_op_block(
        f"21 1 {local_var(0)} 2171 2 {local_var(1)} {local_var(0)} "
        f"4 0 33 3 {local_var(1)} 0 6 2133 2 {reg(0)} 10 "
        f"5 0 33 3 {local_var(1)} 6 11 2133 2 {reg(0)} 20 "
        f"5 0 33 3 {local_var(1)} 11 16 2133 2 {reg(0)} 40 "
        f"5 0 33 3 {local_var(1)} 16 21 2133 2 {reg(0)} 80 "
        f"5 0 33 3 {local_var(1)} 21 26 2133 2 {reg(0)} 120 "
        f"5 0 2133 2 {reg(0)} 160 3 0"
    )
    new_scripts.append(("game_get_upgrade_cost", f" {code_upgrade_cost}"))

    # 8. prsnt_culture_troop_tree (Full 1866 Caba'drin algorithm with 17 root branches)
    ROOT_TROOPS = [
        184,  # 0: 匈牙利/摩拉维亚 (trp_swadian_recruit)
        198,  # 1: 瓦拉几亚 (trp_vaegir_recruit)
        212,  # 2: 奥斯曼 (trp_khergit_tribesman)
        222,  # 3: 克罗地亚 (trp_nord_recruit)
        235,  # 4: 摩尔多瓦 (trp_rhodok_tribesman)
        80,   # 5: 普通丧尸 (trp_undead1)
        84,   # 6: 火焚丧尸 (trp_burned1)
        88,   # 7: 腐烂丧尸 (trp_putrid1)
        92,   # 8: 防腐丧尸 (trp_preserved1)
        97,   # 9: 恶魔与毁灭者 (trp_demon)
        104,  # 10: 暗影造物 (trp_brollachan)
        108,  # 11: 魔偶与血肉机 (trp_golem)
        22,   # 12: 雇佣平民与民兵 (trp_farmer)
        24,   # 13: 雇佣城镇工人与剑士 (trp_townsman)
        265,  # 14: 难民与女剑客姐妹 (trp_refugee)
        256,  # 15: 赏金猎人与猎奴首领 (trp_manhunter)
        249,  # 16: 盗匪与绿林好汉 (trp_bandit)
    ]
    
    # Read 1866 ops
    with open(os.path.join(SOURCE_1866, "scripts.txt"), "r", encoding="latin1") as f:
        s_lines_1866 = [l.strip() for l in f if l.strip()]
    s_map_1866 = {}
    for i in range(2, len(s_lines_1866), 2):
        parts = s_lines_1866[i].split()
        s_map_1866[parts[0]] = s_lines_1866[i+1]
    
    toks_1866 = s_map_1866['prsnt_culture_troop_tree'].split()
    ops_1866 = []
    i = 1
    while i < len(toks_1866):
        op = int(toks_1866[i])
        nargs = int(toks_1866[i+1])
        args = toks_1866[i+2 : i+2+nargs]
        ops_1866.append((op, nargs, args))
        i += 2 + nargs
        
    culture_tree_ops = []
    # Param 1: choice
    culture_tree_ops.append((21, 1, [str(local_var(0))]))
    culture_tree_ops.append((4, 0, [])) # try_begin
    for c_idx, root_id in enumerate(ROOT_TROOPS):
        if c_idx > 0:
            culture_tree_ops.append((5, 0, [])) # else_try
        if c_idx < len(ROOT_TROOPS) - 1:
            culture_tree_ops.append((31, 2, [str(local_var(0)), str(c_idx)]))
        culture_tree_ops.append((2133, 2, [str(local_var(1)), "0"]))
        culture_tree_ops.append((2133, 2, [str(local_var(2)), "0"]))
        culture_tree_ops.append((2133, 2, [str(local_var(15)), str(troop_id(root_id))]))
    culture_tree_ops.append((3, 0, [])) # try_end
    
    # Append Caba'drin algorithm (ops 76..328) with translated IDs
    for idx in range(76, len(ops_1866)):
        op, nargs, args = ops_1866[idx]
        new_args = []
        for a in args:
            val = int(a)
            if val == 360287970189640169: # trp_temp_array_a in 1866
                new_args.append(str(id_trp_temp_a))
            elif val == 360287970189640170: # trp_temp_array_b in 1866
                new_args.append(str(id_trp_temp_b))
            elif val == 360287970189640171: # trp_temp_array_c in 1866
                new_args.append(str(id_trp_temp_c))
            elif val == 936748722493063614: # script_prsnt_lines_to in 1866
                new_args.append(str(script_id(idx_prsnt_lines_to)))
            elif val == 936748722493063615: # script_prsnt_upgrade_tree_troop_and_name in 1866
                new_args.append(str(script_id(idx_upgrade_tree_troop_and_name)))
            elif val == 936748722493063616: # script_prsnt_upgrade_tree_troop_cost in 1866
                new_args.append(str(script_id(idx_upgrade_tree_troop_cost)))
            else:
                new_args.append(a)
        if idx in [82, 83]: # make mesh1/mesh2 overlay invisible
            new_args[1] = "0"
        culture_tree_ops.append((op, nargs, new_args))
        
    # Serialize culture tree ops
    culture_tree_toks = []
    for op, nargs, args in culture_tree_ops:
        culture_tree_toks.append(str(op))
        culture_tree_toks.append(str(nargs))
        culture_tree_toks.extend(args)
    code_culture_tree = f"{len(culture_tree_ops)} {' '.join(culture_tree_toks)}"
    new_scripts.append(("prsnt_culture_troop_tree", f" {code_culture_tree}"))
    
    # 9. all_items_populate_category (Strict Warband standard item types)
    pop_items_lines = [
        f"21 1 {local_var(0)}", # store_script_param_1, :category
        f"2133 2 {local_var(1)} 0", # assign, :num_matches, 0
        f"6 3 {local_var(2)} 1 902", # try_for_range, :item, 1, 902
        f"1570 2 {local_var(3)} {local_var(2)}", # item_get_type, :type, :item
        f"2133 2 {local_var(4)} 0", # assign, :match, 0
        f"4 0 31 2 {local_var(0)} 0 2133 2 {local_var(4)} 1", # cat 0: all
        f"5 0 31 2 {local_var(0)} 1 31 2 {local_var(3)} 1 2133 2 {local_var(4)} 1", # cat 1: horse (1)
        f"5 0 31 2 {local_var(0)} 2 31 2 {local_var(3)} 2 2133 2 {local_var(4)} 1", # cat 2: 1h (2)
        f"5 0 31 2 {local_var(0)} 3 31 2 {local_var(3)} 3 2133 2 {local_var(4)} 1", # cat 3: 2h (3)
        f"5 0 31 2 {local_var(0)} 4 31 2 {local_var(3)} 4 2133 2 {local_var(4)} 1", # cat 4: polearm (4)
        f"5 0 31 2 {local_var(0)} 5 31 2 {local_var(3)} 8 2133 2 {local_var(4)} 1", # cat 5: bow (8)
        f"5 0 31 2 {local_var(0)} 6 31 2 {local_var(3)} 9 2133 2 {local_var(4)} 1", # cat 6: crossbow (9)
        f"5 0 31 2 {local_var(0)} 7 31 2 {local_var(3)} 5 2133 2 {local_var(4)} 1", # cat 7: arrows (5)
        f"5 0 31 2 {local_var(0)} 8 31 2 {local_var(3)} 6 2133 2 {local_var(4)} 1", # cat 8: bolts (6)
        f"5 0 31 2 {local_var(0)} 9 31 2 {local_var(3)} 10 2133 2 {local_var(4)} 1", # cat 9: thrown (10)
        f"5 0 31 2 {local_var(0)} 10 31 2 {local_var(3)} 7 2133 2 {local_var(4)} 1", # cat 10: shield (7)
        f"5 0 31 2 {local_var(0)} 11 31 2 {local_var(3)} 12 2133 2 {local_var(4)} 1", # cat 11: head (12)
        f"5 0 31 2 {local_var(0)} 12 31 2 {local_var(3)} 13 2133 2 {local_var(4)} 1", # cat 12: body (13)
        f"5 0 31 2 {local_var(0)} 13 31 2 {local_var(3)} 14 2133 2 {local_var(4)} 1", # cat 13: foot (14)
        f"5 0 31 2 {local_var(0)} 14 31 2 {local_var(3)} 15 2133 2 {local_var(4)} 1", # cat 14: hand (15)
        f"5 0 31 2 {local_var(0)} 15 4 0 1073741855 2 {local_var(3)} 16 1073741855 2 {local_var(3)} 17 31 2 {local_var(3)} 18 2133 2 {local_var(4)} 1 3 0", # cat 15: firearms (16, 17, 18)
        f"5 0 31 2 {local_var(0)} 16 4 0 1073741855 2 {local_var(3)} 11 31 2 {local_var(3)} 20 2133 2 {local_var(4)} 1 3 0", # cat 16: goods (11, 20)
        f"3 0", # try_end
        f"4 0 31 2 {local_var(4)} 1", # if match == 1
        f"2120 3 {local_var(5)} {local_var(1)} 2", # slot = num_matches + 2
        f"500 3 {id_trp_temp_c} {local_var(5)} {local_var(2)}", # troop_set_slot, trp_temp_c, slot, item
        f"2105 2 {local_var(1)} 1", # num_matches += 1
        f"3 0", # try_end
        f"3 0", # end try_for_range
        f"500 3 {id_trp_temp_c} 0 {local_var(1)}", # troop_set_slot, trp_temp_c, 0, num_matches
        f"2133 2 {reg(0)} {local_var(1)}" # assign, reg0, num_matches
    ]
    code_populate_items = make_op_block(" ".join(pop_items_lines))
    new_scripts.append(("all_items_populate_category", f" {code_populate_items}"))

    # Write scripts.txt
    scripts_path = os.path.join(MODULE_DIR, "scripts.txt")
    scripts_lines = list(script_orig_lines)
    script_count = script_count_orig + len(new_scripts)
    scripts_lines[1] = f"{script_count}\n"
    for s_name, s_code in new_scripts:
        scripts_lines.append(f"{s_name} -1\n{s_code}\n")
    with open(scripts_path, "w", encoding="latin1") as f:
        f.writelines(scripts_lines)
    print(f"Wrote scripts.txt with {script_count} scripts.")
    verify_scripts_file(scripts_path)

    # 5. Generate presentations
    prsnt_blocks = []
    
    # 1) prsnt_faction_troop_tree
    p1_t0 = make_trigger(-60.0,
        f"902 1 999999 2124 1 1000 "
        f"940 2 {v_obj_21} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 885 730 2 1 30 926 2 {v_obj_21} 1 "
        f"729 2 1 500 730 2 1 650 729 2 3 2000 730 2 3 2000 "
        f"910 3 {reg(0)} {qstr(existing_qs['qstr_faction_troop_tree'])} 16 "
        f"921 2 {reg(0)} 16711680 926 2 {reg(0)} 1 925 2 {reg(0)} 3 "
        f"948 1 {v_obj_1} "
        f"729 2 1 500 730 2 1 600 926 2 {v_obj_1} 1 "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_hungary'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_wallachia'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_ottoman'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_croatia'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_moldavia'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_undead'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_burned'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_putrid'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_preserved'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_demons'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_brollachan'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_golem'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_commoners'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_townsmen'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_women'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_manhunters'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_outlaws'])} "
        f"2112 3 {v_tree_sel} 0 16 "
        f"927 2 {v_obj_1} {v_tree_sel} "
        f"1 2 {idx_prsnt_culture_troop_tree} {v_tree_sel}"
    )
    
    p1_t1 = make_trigger(-62.0,
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} 2124 1 1000 "
        f"4 0 31 2 {local_var(0)} {v_obj_1} 2133 2 {v_tree_sel} {local_var(1)} 900 1 {idx_prsnt_troop_tree} "
        f"5 0 31 2 {local_var(0)} {v_obj_21} 902 1 0 "
        f"5 0 "
        f"520 3 {local_var(2)} {id_trp_temp_c} 100 2105 2 {local_var(2)} 1 2133 2 {local_var(3)} 0 "
        f"6 3 {local_var(4)} 101 {local_var(2)} "
        f"2147483680 2 {local_var(3)} 0 "
        f"540 3 {id_trp_temp_c} {local_var(4)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(4)} "
        f"3 0 "
        f"32 2 {local_var(3)} 0 2133 2 {v_temp} {local_var(3)} 2133 2 {v_next_prsnt} {idx_prsnt_troop_tree} 900 1 {idx_prsnt_troop_note} "
        f"3 0"
    )
    
    p1_t2 = make_trigger(-61.0,
        f"4 0 1073741895 1 1 71 1 225 902 1 0 2060 1 4 3 0"
    )
    prsnt_blocks.append(f"prsnt_faction_troop_tree 0 {id_mesh_load_window} 3\r\n{p1_t0}\r\n{p1_t1}\r\n{p1_t2}\r\n")

    # 2) prsnt_troop_note
    p2_t0 = make_trigger(-60.0,
        f"902 1 999999 2124 1 1000 "
        f"1 3 {idx_copy_inventory} {v_temp} {id_trp_temp_a} "
        f"6 3 {local_var(0)} 0 10 "
        f"1541 3 {local_var(1)} {id_trp_temp_a} {local_var(0)} "
        f"32 2 {local_var(1)} -1 1530 2 {id_trp_temp_a} {local_var(1)} 1543 3 {id_trp_temp_a} {local_var(0)} -1 3 0 "
        f"940 2 {v_obj_1} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 885 730 2 1 30 926 2 {v_obj_1} 1 "
        f"1 2 {idx_get_max_hp} {v_temp} 2171 2 {reg(1)} {v_temp} 2322 2 1 {v_temp} "
        f"910 3 {reg(2)} {qstr(existing_qs['qstr_troop_note_name_lvl'])} 0 "
        f"729 2 1 150 730 2 1 640 926 2 {reg(2)} 1 "
        f"729 2 1 1400 730 2 1 1400 925 2 {reg(2)} 1 "
        f"2122 3 {local_var(2)} {v_temp} 2 "
        f"938 4 {reg(3)} -1 {(TAG_TABLEAU<<56)+id_tab_party} {local_var(2)} "
        f"729 2 1 400 730 2 1 360 926 2 {reg(3)} 1 "
        f"729 2 1 1000 730 2 1 1200 925 2 {reg(3)} 1 "
        f"2172 3 {reg(1)} {v_temp} 0 2172 3 {reg(2)} {v_temp} 2 "
        f"2170 3 {reg(3)} {v_temp} 7 2170 3 {reg(4)} {v_temp} 8 2170 3 {reg(5)} {v_temp} 9 2170 3 {reg(6)} {v_temp} 12 "
        f"2174 3 {reg(7)} {v_temp} 0 2174 3 {reg(8)} {v_temp} 1 2174 3 {reg(9)} {v_temp} 2 "
        f"910 3 {reg(4)} {qstr(existing_qs['qstr_troop_note_attr'])} 0 "
        f"729 2 1 150 730 2 1 200 926 2 {reg(4)} 1 "
        f"729 2 1 900 730 2 1 900 925 2 {reg(4)} 1 "
        f"2172 3 {reg(1)} {v_temp} 1 2172 3 {reg(2)} {v_temp} 3 "
        f"2170 3 {reg(3)} {v_temp} 10 2170 3 {reg(4)} {v_temp} 11 2170 3 {reg(5)} {v_temp} 13 "
        f"2174 3 {reg(6)} {v_temp} 3 2174 3 {reg(7)} {v_temp} 4 2174 3 {reg(8)} {v_temp} 5 "
        f"910 3 {reg(5)} {qstr(existing_qs['qstr_troop_note_attr2'])} 0 "
        f"729 2 1 450 730 2 1 200 926 2 {reg(5)} 1 "
        f"729 2 1 900 730 2 1 900 925 2 {reg(5)} 1 "
        f"910 3 {reg(6)} {qstr(existing_qs['qstr_troop_note_equip'])} 0 "
        f"729 2 1 730 730 2 1 600 926 2 {reg(6)} 1 "
        f"729 2 1 1200 730 2 1 1200 925 2 {reg(6)} 1 "
        f"2133 2 {local_var(3)} 730 2133 2 {local_var(4)} 540 "
        f"6 3 {local_var(5)} 0 16 "
        f"1541 3 {local_var(6)} {v_temp} {local_var(5)} "
        f"4 0 32 2 {local_var(6)} -1 "
        f"911 2 {reg(7)} {id_mesh_mp_inventory_choose} "
        f"729 2 1 600 730 2 1 600 925 2 {reg(7)} 1 "
        f"729 2 1 {local_var(3)} 730 2 1 {local_var(4)} 926 2 {reg(7)} 1 "
        f"944 2 {reg(8)} {local_var(6)} "
        f"729 2 1 750 730 2 1 750 925 2 {reg(8)} 1 "
        f"2120 3 {local_var(7)} {local_var(3)} 38 2120 3 {local_var(8)} {local_var(4)} 38 "
        f"729 2 1 {local_var(7)} 730 2 1 {local_var(8)} 926 2 {reg(8)} 1 "
        f"2105 2 {local_var(3)} 75 "
        f"2121 3 {local_var(9)} {local_var(5)} 1 2119 3 {local_var(10)} {local_var(9)} 4 "
        f"31 2 {local_var(10)} 0 2133 2 {local_var(3)} 730 2106 2 {local_var(4)} 75 "
        f"3 0 3 0"
    )
    
    p2_t1 = make_trigger(-62.0,
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} 2124 1 1000 "
        f"4 0 31 2 {local_var(0)} {v_obj_1} 900 1 {v_next_prsnt} 3 0"
    )
    
    p2_t2 = make_trigger(-61.0,
        f"4 0 1073741895 1 1 71 1 225 900 1 {v_next_prsnt} 3 0"
    )
    prsnt_blocks.append(f"prsnt_troop_note 0 {id_mesh_load_window} 3\r\n{p2_t0}\r\n{p2_t1}\r\n{p2_t2}\r\n")

    # 3) prsnt_all_items (Clean UI: Category combo box on right panel, centered pagination, left-aligned title)
    p3_t0 = make_trigger(-60.0,
        f"902 1 999999 2124 1 1000 "
        f"1 2 {idx_all_items_populate} {v_cat} "
        f"520 3 {local_var(0)} {id_trp_temp_c} 0 "
        f"2120 3 {local_var(1)} {local_var(0)} 55 2108 2 {local_var(1)} 56 "
        f"2111 2 {local_var(1)} 1 "
        f"2121 3 {local_var(2)} {local_var(1)} 1 "
        f"2112 3 {v_page} 0 {local_var(2)} "
        f"911 2 {reg(1)} {id_mesh_load_window} 729 2 1 0 730 2 1 0 926 2 {reg(1)} 1 "
        # Title: top left at (40, 665), left justified (0)
        f"910 3 {reg(1)} {qstr(existing_qs['qstr_all_items_title'])} 0 "
        f"729 2 1 40 730 2 1 665 926 2 {reg(1)} 1 "
        # Pagination: center top (360 .. 600)
        f"940 2 {v_prev_btn} {qstr(existing_qs['qstr_prev_page'])} "
        f"729 2 1 360 730 2 1 660 926 2 {v_prev_btn} 1 "
        f"2120 3 {reg(0)} {v_page} 1 2133 2 {reg(1)} {local_var(1)} 2133 2 {reg(2)} {local_var(0)} "
        f"910 3 {reg(3)} {qstr(existing_qs['qstr_page_str'])} 16 "
        f"729 2 1 480 730 2 1 665 926 2 {reg(3)} 1 "
        f"940 2 {v_next_btn} {qstr(existing_qs['qstr_next_page'])} "
        f"729 2 1 600 730 2 1 660 926 2 {v_next_btn} 1 "
        # Done button: top right at (885, 660)
        f"940 2 {v_done_btn} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 885 730 2 1 660 926 2 {v_done_btn} 1 "
        # Category Selector: MOVED TO RIGHT PANEL TOP at (730, 615)!
        f"916 1 {v_cat_sel} "
        f"729 2 1 730 730 2 1 615 926 2 {v_cat_sel} 1 "
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
        # 8x7 Items Grid (Left side, X=25, Y=560 down to 60)
        f"2133 2 {local_var(3)} 25 2133 2 {local_var(4)} 560 2133 2 {local_var(5)} 1 "
        f"6 3 {local_var(6)} 0 7 "
        f"6 3 {local_var(7)} 0 8 "
        f"2122 3 {local_var(8)} {v_page} 56 2105 2 {local_var(8)} {local_var(5)} 2105 2 {local_var(8)} 1 "
        f"520 3 {local_var(9)} {id_trp_temp_c} {local_var(8)} "
        f"911 2 {reg(1)} {id_mesh_mp_inventory_choose} "
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
        f"2133 2 {local_var(3)} 25 2106 2 {local_var(4)} 80 3 0 "
        # Right Preview Panel
        f"4 0 2147483680 2 {v_sel_item} 0 "
        f"520 3 {v_sel_item} {id_trp_temp_b} 1 3 0 "
        f"911 2 {reg(1)} {id_mesh_mp_inventory_choose} "
        f"729 2 1 1800 730 2 1 1800 925 2 {reg(1)} 1 "
        f"729 2 1 730 730 2 1 340 926 2 {reg(1)} 1 "
        f"4 0 32 2 {v_sel_item} 0 "
        f"944 2 {reg(2)} {v_sel_item} "
        f"729 2 1 2400 730 2 1 2400 925 2 {reg(2)} 1 "
        f"729 2 1 840 730 2 1 450 926 2 {reg(2)} 1 "
        f"2325 2 1 {v_sel_item} "
        f"910 3 {reg(3)} {str_id(1)} 16 "
        f"729 2 1 840 730 2 1 300 926 2 {reg(3)} 1 "
        f"940 2 {v_get_btn} {qstr(existing_qs['qstr_get_item'])} "
        f"729 2 1 780 730 2 1 220 926 2 {v_get_btn} 1 3 0"
    )
    
    p3_t1 = make_trigger(-63.0,
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        f"4 0 31 2 {local_var(1)} 0 "
        f"6 3 {local_var(2)} 1 57 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(2)} "
        f"4 0 32 2 {local_var(3)} 0 "
        f"972 4 {local_var(3)} {v_imod} 0 100 "
        f"2133 2 {v_tooltip_slot} {local_var(2)} "
        f"3 0 3 0 "
        f"5 0 "
        f"6 3 {local_var(2)} 1 57 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"4 0 31 2 {v_tooltip_slot} {local_var(2)} 971 0 3 0 "
        f"3 0 3 0"
    )
    
    p3_t2 = make_trigger(-62.0,
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        f"4 0 31 2 {local_var(0)} {v_cat_sel} "
        f"2133 2 {v_cat} {local_var(1)} 2133 2 {v_page} 0 2133 2 {v_sel_item} 0 900 1 {idx_prsnt_all_items} "
        f"5 0 31 2 {local_var(0)} {v_prev_btn} "
        f"2106 2 {v_page} 1 2111 2 {v_page} 0 900 1 {idx_prsnt_all_items} "
        f"5 0 31 2 {local_var(0)} {v_next_btn} "
        f"2105 2 {v_page} 1 900 1 {idx_prsnt_all_items} "
        f"5 0 31 2 {local_var(0)} {v_done_btn} "
        f"902 1 0 "
        f"5 0 31 2 {local_var(0)} {v_get_btn} "
        f"4 0 32 2 {v_sel_item} 0 "
        f"1530 3 {id_trp_player} {v_sel_item} {v_imod} "
        f"2325 2 1 {v_sel_item} "
        f"1106 1 {qstr(existing_qs['qstr_added_item'])} 3 0 "
        f"5 0 "
        f"6 3 {local_var(2)} 1 57 "
        f"540 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(2)} "
        f"4 0 32 2 {local_var(3)} 0 "
        f"2133 2 {v_sel_item} {local_var(3)} "
        f"900 1 {idx_prsnt_all_items} 3 0 "
        f"3 0 "
        f"3 0"
    )
    
    p3_t3 = make_trigger(-61.0,
        f"4 0 1073741895 1 1 71 1 225 902 1 0 2060 1 4 3 0"
    )
    prsnt_blocks.append(f"prsnt_all_items 0 {id_mesh_load_window} 4\r\n{p3_t0}\r\n{p3_t1}\r\n{p3_t2}\r\n{p3_t3}\r\n")

    # Write presentations.txt
    prsnt_path = os.path.join(MODULE_DIR, "presentations.txt")
    prsnt_lines = list(prsnt_orig_lines)
    prsnt_count = prsnt_count_orig + len(prsnt_blocks)
    prsnt_lines[1] = f" {prsnt_count}\r\n"
    prsnt_lines.extend(prsnt_blocks)
    with open(prsnt_path, "w", encoding="latin1") as f:
        f.writelines(prsnt_lines)
    print(f"Wrote presentations.txt with {prsnt_count} presentations.")
    verify_presentations_file(prsnt_path)

    # 6. Update languages/cns/quick_strings.csv if exists
    cns_csv = os.path.join(MODULE_DIR, "languages/cns/quick_strings.csv")
    if os.path.exists(cns_csv):
        with open(cns_csv, "r", encoding="utf-8", errors="ignore") as f:
            cns_lines = f.readlines()
        existing_cns = {l.split("|")[0].strip(): True for l in cns_lines if "|" in l}
        
        cns_additions = [
            ("qstr_faction_troop_tree", "阵营兵种升级树"),
            ("qstr_view_troop_trees", "查看兵种升级树"),
            ("qstr_view_all_items", "查看全部装备与物品"),
            ("qstr_all_items_title", "装备与物品查看器"),
            ("qstr_done", "完成 / 返回"),
            ("qstr_prev_page", "< 上一页"),
            ("qstr_next_page", "下一页 >"),
            ("qstr_get_item", "获取该装备"),
            ("qstr_added_item", "已将 {s1} 放入背包。"),
            ("qstr_page_str", "第 {reg0} / {reg1} 页 (共 {reg2} 件物品)"),
            ("qstr_tree_hungary", "摩拉维亚王国 (匈牙利)"),
            ("qstr_tree_wallachia", "瓦拉几亚公国"),
            ("qstr_tree_ottoman", "奥斯曼帝国"),
            ("qstr_tree_croatia", "克罗地亚王国"),
            ("qstr_tree_moldavia", "摩尔多瓦公国"),
            ("qstr_tree_undead", "死灵：普通丧尸"),
            ("qstr_tree_burned", "死灵：火焚丧尸"),
            ("qstr_tree_putrid", "死灵：腐烂丧尸"),
            ("qstr_tree_preserved", "死灵：防腐丧尸"),
            ("qstr_tree_demons", "死灵：恶魔与毁灭者"),
            ("qstr_tree_brollachan", "死灵：暗影造物"),
            ("qstr_tree_golem", "死灵：魔偶与血肉机"),
            ("qstr_tree_commoners", "雇佣平民与民兵"),
            ("qstr_tree_townsmen", "雇佣城镇工人与剑士"),
            ("qstr_tree_women", "难民与女剑客姐妹"),
            ("qstr_tree_manhunters", "赏金猎人与猎奴首领"),
            ("qstr_tree_outlaws", "盗匪与绿林好汉"),
            ("qstr_cat_all", "全部装备与物品"),
            ("qstr_cat_horses", "战马与坐骑"),
            ("qstr_cat_1h", "单手武器"),
            ("qstr_cat_2h", "双手武器"),
            ("qstr_cat_polearms", "长杆武器"),
            ("qstr_cat_bows", "弓类武器"),
            ("qstr_cat_arrows", "箭矢弹药"),
            ("qstr_cat_crossbows", "弩类武器"),
            ("qstr_cat_bolts", "弩矢弹药"),
            ("qstr_cat_thrown", "投掷武器"),
            ("qstr_cat_shields", "盾牌装备"),
            ("qstr_cat_helmets", "头部防具"),
            ("qstr_cat_armor", "身体铠甲"),
            ("qstr_cat_boots", "腿部防具"),
            ("qstr_cat_gloves", "手套防具"),
            ("qstr_cat_firearms", "火器与弹药"),
            ("qstr_cat_goods", "商品与书籍"),
        ]
        cns_updated = False
        for k, v in cns_additions:
            if k not in existing_cns:
                cns_lines.append(f"{k}|{v}\r\n")
                cns_updated = True
        if cns_updated:
            with open(cns_csv, "w", encoding="utf-8") as f:
                f.writelines(cns_lines)
            print("Updated languages/cns/quick_strings.csv with Chinese localizations.")

    print("ALL INSTALLATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run()
