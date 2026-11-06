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
def mesh_id(n): return OPMASK_MESH + n

# Strict, canonical item category definitions
# Maps category index -> (qstr_identifier, [list of itp_type numbers])
ITEM_CATEGORIES = [
    ("qstr_cat_all", []),               # 0: 全部
    ("qstr_cat_horses", [1]),           # 1: 战马 (itp_type_horse = 1)
    ("qstr_cat_1h", [2]),               # 2: 单手 (itp_type_one_handed_wpn = 2)
    ("qstr_cat_2h", [3]),               # 3: 双手 (itp_type_two_handed_wpn = 3)
    ("qstr_cat_polearms", [4]),         # 4: 长杆 (itp_type_polearm = 4)
    ("qstr_cat_bows", [8]),             # 5: 弓类 (itp_type_bow = 8)
    ("qstr_cat_crossbows", [9]),        # 6: 弩类 (itp_type_crossbow = 9)
    ("qstr_cat_arrows", [5]),           # 7: 箭矢 (itp_type_arrows = 5)
    ("qstr_cat_bolts", [6]),            # 8: 弩矢 (itp_type_bolts = 6)
    ("qstr_cat_thrown", [10]),          # 9: 投掷 (itp_type_thrown = 10)
    ("qstr_cat_shields", [7]),          # 10: 盾牌 (itp_type_shield = 7)
    ("qstr_cat_helmets", [12]),         # 11: 头部 (itp_type_head_armor = 12)
    ("qstr_cat_armor", [13]),           # 12: 身体 (itp_type_body_armor = 13)
    ("qstr_cat_boots", [14]),           # 13: 腿部 (itp_type_foot_armor = 14)
    ("qstr_cat_gloves", [15]),          # 14: 手套 (itp_type_hand_armor = 15)
    ("qstr_cat_firearms", [16, 17, 18]),# 15: 火器与弹药 (pistol=16, musket=17, bullets=18)
    ("qstr_cat_goods", [11, 20]),       # 16: 商品与书籍 (goods=11, book=20)
]

def make_op_block(raw_str):
    tokens = raw_str.split()
    ops, i = [], 0
    while i < len(tokens):
        op = int(tokens[i])
        n = int(tokens[i+1])
        args = tokens[i+2 : i+2+n]
        ops.append((op, n, args))
        i += 2 + n
    flat = []
    for op, n, args in ops:
        flat += [str(op), str(n)] + list(args)
    return f"{len(ops)} {' '.join(flat)}"

def make_trigger(interval, raw_str):
    op_str = make_op_block(raw_str)
    return f"{interval:.6f}  {op_str} "

def verify_scripts_file(path):
    with open(path, "r", encoding="latin1") as f:
        lines = [l.strip() for l in f if l.strip()]
    declared_count = int(lines[1])
    actual_scripts = []
    i = 2
    while i < len(lines):
        line = lines[i]
        if line.endswith("-1"):
            name = line.split()[0]
            body = lines[i+1]
            actual_scripts.append((name, body))
            i += 2
        else:
            raise ValueError(f"Malformed scripts.txt at line {i}: {line[:40]}")
    assert len(actual_scripts) == declared_count, f"Count mismatch: header {declared_count} vs actual {len(actual_scripts)}"
    print(f"Verified scripts.txt: exactly {declared_count} valid script definitions.")

def verify_presentations_file(path):
    with open(path, "r", encoding="latin1") as f:
        lines = [l.strip() for l in f if l.strip()]
    declared_count = int(lines[1])
    actual_prsnts = []
    i = 2
    while i < len(lines):
        line = lines[i]
        if line.startswith("prsnt_"):
            actual_prsnts.append(line.split()[0])
        i += 1
    assert len(actual_prsnts) == declared_count, f"Count mismatch: header {declared_count} vs actual {len(actual_prsnts)}"
    print(f"Verified presentations.txt: exactly {declared_count} valid presentation definitions.")

def run():
    print("=== Installing Viewers & Merging Notes Hooks into Carpathian Solid & Shade ===")
    
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
        ("mesh_white_plane", "mesh_white_plane 0 white_plane 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 1.000000 1.000000 1.000000"),
        ("mesh_load_window", "mesh_load_window 0 load_window 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 1.000000 1.000000 1.000000"),
        ("mesh_mp_inventory_choose", "mesh_mp_inventory_choose 0 mp_inventory_choose 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 1.000000 1.000000 1.000000"),
    ]
    mesh_added = False
    for m_name, m_entry in needed_meshes:
        if m_name not in existing_meshes:
            existing_meshes[m_name] = mesh_count
            mesh_lines.append(m_entry + "\r\n")
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
        ("qstr_cat_crossbows", "qstr_cat_crossbows Crossbows"),
        ("qstr_cat_arrows", "qstr_cat_arrows Arrows"),
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
        script_orig_lines = [l.strip() for l in f if l.strip()]
        
    actual_base_scripts = []
    i = 2
    while i < len(script_orig_lines):
        line = script_orig_lines[i]
        if line.endswith("-1"):
            name = line.split()[0]
            body = script_orig_lines[i+1]
            actual_base_scripts.append((name, body))
            i += 2
        else:
            i += 1
            
    # Seamless merge of Official 11-02 Patch: Note Callback Hooks
    official_hooks = [
        "game_get_troop_note",
        "game_get_center_note",
        "game_get_faction_note",
        "game_get_quest_note",
        "game_get_info_page_note",
    ]
    base_script_names = {s[0] for s in actual_base_scripts}
    for h in official_hooks:
        if h not in base_script_names:
            actual_base_scripts.append((h, "1 2075 1 0"))
            base_script_names.add(h)
            
    base_script_count = len(actual_base_scripts)
    print(f"Base scripts (including 11-02 note hooks): {base_script_count}")
    
    # Custom scripts indexing
    idx_prsnt_lines = base_script_count
    idx_prsnt_lines_to = base_script_count + 1
    idx_upgrade_tree_troop_and_name = base_script_count + 2
    idx_upgrade_tree_troop_cost = base_script_count + 3
    idx_get_max_hp = base_script_count + 4
    idx_copy_inventory = base_script_count + 5
    idx_game_get_upgrade_cost = base_script_count + 6
    idx_prsnt_culture_troop_tree = base_script_count + 7
    idx_all_items_populate = base_script_count + 8
    
    prsnt_orig_path = os.path.join(MODULE_DIR, "presentations.txt.orig_pre_viewers")
    with open(prsnt_orig_path, "r", encoding="latin1") as f:
        prsnt_orig_lines = f.readlines()
    prsnt_count_orig = int(prsnt_orig_lines[1].strip())
    
    idx_prsnt_troop_tree = prsnt_count_orig
    idx_prsnt_troop_note = idx_prsnt_troop_tree + 1
    idx_prsnt_all_items = idx_prsnt_troop_note + 1
    
    id_tab_party = 2 # tab_game_party_window

    print(f"Indices: troop_tree={prsnt_id(idx_prsnt_troop_tree)}, all_items={prsnt_id(idx_prsnt_all_items)}")

    # 4. Helper scripts from 1866 with strict ID remapping
    with open(os.path.join(SOURCE_1866, "scripts.txt"), "r", encoding="latin1") as f:
        _sl = [l.strip() for l in f if l.strip()]
    _s1866 = {}
    for _i in range(2, len(_sl), 2):
        _s1866[_sl[_i].split()[0]] = _sl[_i + 1]
        
    _REMAP = {
        (TAG_SCRIPT, 444): (TAG_SCRIPT, idx_game_get_upgrade_cost),
        (TAG_SCRIPT, 446): (TAG_SCRIPT, idx_prsnt_lines_to),
        (TAG_SCRIPT, 447): (TAG_SCRIPT, idx_upgrade_tree_troop_and_name),
        (TAG_SCRIPT, 448): (TAG_SCRIPT, idx_upgrade_tree_troop_cost),
        (TAG_SCRIPT, 449): (TAG_SCRIPT, idx_prsnt_lines),
        (TAG_TROOP, 489): (TAG_TROOP, id_trp_temp_a & 0xFFFFFFFF),
        (TAG_TROOP, 490): (TAG_TROOP, id_trp_temp_b & 0xFFFFFFFF),
        (TAG_TROOP, 491): (TAG_TROOP, id_trp_temp_c & 0xFFFFFFFF),
        (TAG_MESH, 165): (TAG_MESH, id_mesh_white_plane),
        (TAG_TABLEAU, 2): (TAG_TABLEAU, id_tab_party),
        (TAG_QUICK_STRING, 6): (TAG_QUICK_STRING, 6),
        (TAG_QUICK_STRING, 44): (TAG_QUICK_STRING, 44),
    }
    _SAFE_TAGS = {0, TAG_REGISTER, TAG_LOCAL_VARIABLE}

    def parse_1866(name):
        t = _s1866[name].split()
        ops, i = [], 1
        while i < len(t):
            op, n = int(t[i]), int(t[i + 1])
            ops.append([op, n, t[i + 2:i + 2 + n]])
            i += 2 + n
        assert len(ops) == int(t[0]), name
        return ops

    def remap_ops(ops, ctx):
        out = []
        for op, n, args in ops:
            new_args = []
            for a in args:
                raw = int(a)
                if raw < 0:
                    new_args.append(a)
                    continue
                tag = raw >> 56
                val = raw & 0xFFFFFFFFFFFFFF
                if (tag, val) in _REMAP:
                    t_tag, t_val = _REMAP[(tag, val)]
                    new_args.append(str((t_tag << 56) | t_val))
                elif tag in _SAFE_TAGS:
                    new_args.append(a)
                else:
                    raise ValueError(f"[{ctx}] unmapped token {a} (tag={tag}, val={val}) in op {op}")
            out.append((op, n, new_args))
        return out

    def ser(ops):
        tk = []
        for op, n, args in ops:
            tk += [str(op), str(n)] + list(args)
        return f"{len(ops)} {' '.join(tk)}"

    new_scripts = []
    # 0..3: lines, lines_to, troop_and_name, troop_cost
    for _nm in ["prsnt_lines", "prsnt_lines_to", "prsnt_upgrade_tree_troop_and_name", "prsnt_upgrade_tree_troop_cost"]:
        new_scripts.append((_nm, ser(remap_ops(parse_1866(_nm), _nm))))
        
    # 4. get_troop_max_hp
    code_hp = make_op_block(
        f"21 1 {local_var(0)} 2172 3 {local_var(1)} {local_var(0)} 0 "
        f"2170 3 {local_var(2)} {local_var(0)} 7 "
        f"2122 3 {reg(0)} {local_var(2)} 2 2105 2 {reg(0)} {local_var(1)} 2105 2 {reg(0)} 35"
    )
    new_scripts.append(("get_troop_max_hp", code_hp))

    # 5. copy_inventory
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
    new_scripts.append(("copy_inventory", code_copy_inv))

    # 6. game_get_upgrade_cost
    code_upgrade_cost = make_op_block(
        f"21 1 {local_var(0)} 2171 2 {local_var(1)} {local_var(0)} "
        f"4 0 33 3 {local_var(1)} 0 6 2133 2 {reg(0)} 10 "
        f"5 0 33 3 {local_var(1)} 6 11 2133 2 {reg(0)} 20 "
        f"5 0 33 3 {local_var(1)} 11 16 2133 2 {reg(0)} 40 "
        f"5 0 33 3 {local_var(1)} 16 21 2133 2 {reg(0)} 80 "
        f"5 0 33 3 {local_var(1)} 21 26 2133 2 {reg(0)} 120 "
        f"5 0 2133 2 {reg(0)} 160 3 0"
    )
    new_scripts.append(("game_get_upgrade_cost", code_upgrade_cost))

    # 7. prsnt_culture_troop_tree: 1866 Caba'drin algorithm verbatim + root troop dispatch
    ROOT_TROOPS = [
        184, 198, 212, 222, 235,       # Hungary, Moldavia, Ottoman, Wallachia, Croatia
        80, 84, 88, 92, 97, 104, 108,  # Undead: Zombie, Burned, Putrid, Preserved, Demon, Brollachan, Golem
        22, 24, 265, 256, 249          # Commoners, Townsmen, Refugees/Women, Manhunters, Outlaws
    ]
    _ops = parse_1866("prsnt_culture_troop_tree")
    hdr = [(21, 1, [str(local_var(0))]), (4, 0, [])]
    for ci, rt in enumerate(ROOT_TROOPS):
        if ci > 0:
            hdr.append((5, 0, []))
        if ci < len(ROOT_TROOPS) - 1:
            hdr.append((31, 2, [str(local_var(0)), str(ci)]))
        hdr.append((2133, 2, [str(local_var(3)), str(troop_id(rt))]))
    hdr.append((3, 0, []))
    body = remap_ops(_ops[88:], "prsnt_culture_troop_tree")
    new_scripts.append(("prsnt_culture_troop_tree", ser(hdr + body)))

    # 8. all_items_populate_category (Strict Warband standard item types)
    pop_items_lines = [
        f"21 1 {local_var(0)}", # store_script_param_1, :category
        f"6 3 {local_var(6)} 0 910 500 3 {id_trp_temp_c} {local_var(6)} 0 3 0", # clear stale slots
        f"2133 2 {local_var(1)} 0", # assign, :num_matches, 0
        f"6 3 {local_var(2)} 1 902", # try_for_range, :item, 1, 902
        f"1570 2 {local_var(3)} {local_var(2)}", # item_get_type, :type, :item
        f"2133 2 {local_var(4)} 0", # assign, :match, 0
        f"4 0 31 2 {local_var(0)} 0 2133 2 {local_var(4)} 1", # cat 0: all
    ]
    for cat_idx, (q_id, types) in enumerate(ITEM_CATEGORIES[1:], 1):
        conds = " ".join([f"31 2 {local_var(3)} {t}" for t in types])
        if len(types) > 1:
            pop_items_lines.append(f"5 0 31 2 {local_var(0)} {cat_idx} 4 0 {' '.join([f'2147483678 2 {local_var(3)} {t}' if i < len(types)-1 else f'31 2 {local_var(3)} {t}' for i, t in enumerate(types)])} 2133 2 {local_var(4)} 1 3 0")
        else:
            pop_items_lines.append(f"5 0 31 2 {local_var(0)} {cat_idx} {conds} 2133 2 {local_var(4)} 1")
            
    pop_items_lines.extend([
        f"3 0",
        f"4 0 31 2 {local_var(4)} 1",
        f"2105 2 {local_var(1)} 1",
        f"500 3 {id_trp_temp_c} {local_var(1)} {local_var(2)}",
        f"3 0 3 0",
        f"500 3 {id_trp_temp_c} 0 {local_var(1)}" # slot 0: total matches
    ])
    code_pop_items = make_op_block(" ".join(pop_items_lines))
    new_scripts.append(("all_items_populate_category", code_pop_items))

    # Assemble complete scripts.txt
    all_final_scripts = actual_base_scripts + new_scripts
    scripts_path = os.path.join(MODULE_DIR, "scripts.txt")
    out_lines = [
        "scriptsfile version 1\r\n",
        f"{len(all_final_scripts)}\r\n"
    ]
    for s_name, s_body in all_final_scripts:
        out_lines.append(f"{s_name} -1\r\n")
        out_lines.append(f" {s_body}\r\n")
        
    with open(scripts_path, "w", encoding="latin1") as f:
        f.writelines(out_lines)
    print(f"Wrote scripts.txt with {len(all_final_scripts)} scripts.")
    verify_scripts_file(scripts_path)

    # 5. presentations.txt
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
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_commoners'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_townsmen'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_women'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_manhunters'])} "
        f"931 2 {v_obj_1} {qstr(existing_qs['qstr_tree_outlaws'])} "
        f"2112 3 {v_tree_sel} 0 17 "
        f"927 2 {v_obj_1} {v_tree_sel} "
        f"1 2 {script_id(idx_prsnt_culture_troop_tree)} {v_tree_sel}"
    )
    
    p1_t1 = make_trigger(-62.0,
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} 2124 1 1000 "
        f"4 0 31 2 {local_var(0)} {v_obj_1} 2133 2 {v_tree_sel} {local_var(1)} 900 1 {prsnt_id(idx_prsnt_troop_tree)} "
        f"5 0 31 2 {local_var(0)} {v_obj_21} 902 1 0 "
        f"5 0 "
        f"520 3 {local_var(2)} {id_trp_temp_c} 100 2105 2 {local_var(2)} 1 2133 2 {local_var(3)} 0 "
        f"6 3 {local_var(4)} 101 {local_var(2)} "
        f"2147483680 2 {local_var(3)} 0 "
        f"540 3 {id_trp_temp_c} {local_var(4)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(4)} "
        f"3 0 "
        f"32 2 {local_var(3)} 0 2133 2 {v_temp} {local_var(3)} 2133 2 {v_next_prsnt} {prsnt_id(idx_prsnt_troop_tree)} 900 1 {prsnt_id(idx_prsnt_troop_note)} "
        f"3 0"
    )
    
    p1_t2 = make_trigger(-61.0,
        f"4 0 1073741895 1 1 71 1 225 902 1 0 2060 1 4 3 0"
    )
    prsnt_blocks.append(f"prsnt_faction_troop_tree 0 {id_mesh_load_window} 3\r\n{p1_t0}\r\n{p1_t1}\r\n{p1_t2}\r\n")

    # 2) prsnt_troop_note
    p2_t0 = make_trigger(-60.0,
        f"902 1 999999 2124 1 1000 "
        f"1 3 {script_id(idx_copy_inventory)} {v_temp} {id_trp_temp_a} "
        f"6 3 {local_var(0)} 0 10 "
        f"1541 3 {local_var(1)} {id_trp_temp_a} {local_var(0)} "
        f"32 2 {local_var(1)} -1 1530 2 {id_trp_temp_a} {local_var(1)} 1543 3 {id_trp_temp_a} {local_var(0)} -1 3 0 "
        f"940 2 {v_obj_1} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 885 730 2 1 30 926 2 {v_obj_1} 1 "
        f"1 2 {script_id(idx_get_max_hp)} {v_temp} 2171 2 {reg(1)} {v_temp} 2322 2 1 {v_temp} "
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
        f"911 2 {reg(7)} {mesh_id(id_mesh_mp_inventory_choose)} "
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
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        f"4 0 31 2 {local_var(0)} {v_obj_1} 902 1 0 900 1 {v_next_prsnt} 3 0"
    )
    
    p2_t2 = make_trigger(-61.0,
        f"4 0 1073741895 1 1 71 1 225 902 1 0 2060 1 4 3 0"
    )
    prsnt_blocks.append(f"prsnt_troop_note 0 {id_mesh_load_window} 3\r\n{p2_t0}\r\n{p2_t1}\r\n{p2_t2}\r\n")

    # 3) prsnt_all_items (Spacious, clean UI, no overlapping controls)
    cat_items_code = " ".join([f"931 2 {v_cat_sel} {qstr(existing_qs[cat_info[0]])} " for cat_info in ITEM_CATEGORIES])
    
    p3_t0 = make_trigger(-60.0,
        f"902 1 999999 2124 1 1000 "
        f"1 2 {script_id(idx_all_items_populate)} {v_cat} "
        f"520 3 {local_var(0)} {id_trp_temp_c} 0 "
        f"2120 3 {local_var(1)} {local_var(0)} 55 2108 2 {local_var(1)} 56 "
        f"2111 2 {local_var(1)} 1 "
        f"2112 3 {v_page} 0 {local_var(1)} "
        f"911 2 {reg(1)} {mesh_id(id_mesh_load_window)} 729 2 1 0 730 2 1 0 926 2 {reg(1)} 1 "
        # 1. Title at (30, 665), left aligned (0)
        f"910 3 {reg(1)} {qstr(existing_qs['qstr_all_items_title'])} 0 "
        f"729 2 1 30 730 2 1 665 926 2 {reg(1)} 1 "
        # 2. Pagination controls in center: (330 .. 580)
        f"940 2 {v_prev_btn} {qstr(existing_qs['qstr_prev_page'])} "
        f"729 2 1 330 730 2 1 660 926 2 {v_prev_btn} 1 "
        f"2120 3 {reg(0)} {v_page} 1 2133 2 {reg(1)} {local_var(1)} 2133 2 {reg(2)} {local_var(0)} "
        f"910 3 {reg(3)} {qstr(existing_qs['qstr_page_str'])} 16 "
        f"729 2 1 440 730 2 1 665 926 2 {reg(3)} 1 "
        f"940 2 {v_next_btn} {qstr(existing_qs['qstr_next_page'])} "
        f"729 2 1 550 730 2 1 660 926 2 {v_next_btn} 1 "
        # 3. Category Selector at (680, 660) - completely separated from grid!
        f"916 1 {v_cat_sel} "
        f"729 2 1 680 730 2 1 660 926 2 {v_cat_sel} 1 "
        f"{cat_items_code}"
        f"927 2 {v_cat_sel} {v_cat} "
        # 4. Done button: top right at (890, 660)
        f"940 2 {v_done_btn} {qstr(existing_qs['qstr_done'])} "
        f"729 2 1 890 730 2 1 660 926 2 {v_done_btn} 1 "
        # 5. 8x7 Items Grid (Left side, X=25, Y=560 down to 60)
        f"2133 2 {local_var(3)} 25 2133 2 {local_var(4)} 560 2133 2 {local_var(5)} 1 "
        f"6 3 {local_var(6)} 0 7 "
        f"6 3 {local_var(7)} 0 8 "
        f"2122 3 {local_var(8)} {v_page} 56 2105 2 {local_var(8)} {local_var(5)} 2105 2 {local_var(8)} 1 "
        f"520 3 {local_var(9)} {id_trp_temp_c} {local_var(8)} "
        f"911 2 {reg(1)} {mesh_id(id_mesh_mp_inventory_choose)} "
        f"729 2 1 640 730 2 1 640 925 2 {reg(1)} 1 "
        f"729 2 1 {local_var(3)} 730 2 1 {local_var(4)} 926 2 {reg(1)} 1 "
        f"500 3 {id_trp_temp_a} {local_var(5)} {reg(1)} "
        f"500 3 {id_trp_temp_b} {local_var(5)} {local_var(9)} "
        f"2120 3 {local_var(12)} {local_var(5)} 60 500 3 {id_trp_temp_a} {local_var(12)} 0 "
        f"4 0 32 2 {local_var(9)} 0 "
        f"944 2 {reg(2)} {local_var(9)} 500 3 {id_trp_temp_a} {local_var(12)} {reg(2)} "
        f"729 2 1 800 730 2 1 800 925 2 {reg(2)} 1 "
        f"2120 3 {local_var(10)} {local_var(3)} 40 2120 3 {local_var(11)} {local_var(4)} 40 "
        f"729 2 1 {local_var(10)} 730 2 1 {local_var(11)} 926 2 {reg(2)} 1 "
        f"3 0 "
        f"2105 2 {local_var(3)} 80 2105 2 {local_var(5)} 1 3 0 "
        f"2133 2 {local_var(3)} 25 2106 2 {local_var(4)} 80 3 0 "
        # 6. Right Preview Panel
        f"4 0 2147483680 2 {v_sel_item} 0 "
        f"520 3 {v_sel_item} {id_trp_temp_b} 1 3 0 "
        f"911 2 {reg(1)} {mesh_id(id_mesh_mp_inventory_choose)} "
        f"729 2 1 1800 730 2 1 1800 925 2 {reg(1)} 1 "
        f"729 2 1 730 730 2 1 340 926 2 {reg(1)} 1 "
        f"4 0 32 2 {v_sel_item} 0 "
        f"944 2 {reg(2)} {v_sel_item} "
        f"729 2 1 2400 730 2 1 2400 925 2 {reg(2)} 1 "
        f"729 2 1 840 730 2 1 450 926 2 {reg(2)} 1 "
        f"2325 2 1 {v_sel_item} "
        f"910 3 {reg(3)} {qstr(6)} 16 "
        f"729 2 1 840 730 2 1 300 926 2 {reg(3)} 1 "
        f"940 2 {v_get_btn} {qstr(existing_qs['qstr_get_item'])} "
        f"729 2 1 780 730 2 1 220 926 2 {v_get_btn} 1 3 0"
    )
    
    p3_t1 = make_trigger(-63.0,
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        f"4 0 31 2 {local_var(1)} 0 "
        f"6 3 {local_var(2)} 1 57 "
        f"2120 3 {local_var(4)} {local_var(2)} 60 "
        f"4 0 1073741855 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} 540 3 {id_trp_temp_a} {local_var(4)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(2)} "
        f"4 0 32 2 {local_var(3)} 0 "
        f"946 2 0 {local_var(0)} 972 4 {local_var(3)} {v_imod} 0 100 "
        f"2133 2 {v_tooltip_slot} {local_var(2)} "
        f"3 0 3 0 3 0 "
        f"5 0 "
        f"6 3 {local_var(2)} 1 57 "
        f"2120 3 {local_var(4)} {local_var(2)} 60 "
        f"4 0 1073741855 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} 540 3 {id_trp_temp_a} {local_var(4)} {local_var(0)} "
        f"4 0 31 2 {v_tooltip_slot} {local_var(2)} 971 0 3 0 "
        f"3 0 3 0 3 0"
    )
    
    p3_t2 = make_trigger(-62.0,
        f"2071 1 {local_var(0)} 2072 1 {local_var(1)} "
        f"4 0 31 2 {local_var(0)} {v_cat_sel} "
        f"2133 2 {v_cat} {local_var(1)} 2133 2 {v_page} 0 2133 2 {v_sel_item} 0 900 1 {prsnt_id(idx_prsnt_all_items)} "
        f"5 0 31 2 {local_var(0)} {v_prev_btn} "
        f"2106 2 {v_page} 1 2111 2 {v_page} 0 900 1 {prsnt_id(idx_prsnt_all_items)} "
        f"5 0 31 2 {local_var(0)} {v_next_btn} "
        f"2105 2 {v_page} 1 900 1 {prsnt_id(idx_prsnt_all_items)} "
        f"5 0 31 2 {local_var(0)} {v_done_btn} "
        f"902 1 0 "
        f"5 0 31 2 {local_var(0)} {v_get_btn} "
        f"4 0 32 2 {v_sel_item} 0 "
        f"1530 3 {id_trp_player} {v_sel_item} {v_imod} "
        f"2325 2 1 {v_sel_item} "
        f"1106 1 {qstr(existing_qs['qstr_added_item'])} 3 0 "
        f"5 0 "
        f"6 3 {local_var(2)} 1 57 "
        f"2120 3 {local_var(4)} {local_var(2)} 60 "
        f"4 0 1073741855 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} 540 3 {id_trp_temp_a} {local_var(4)} {local_var(0)} "
        f"520 3 {local_var(3)} {id_trp_temp_b} {local_var(2)} "
        f"4 0 32 2 {local_var(3)} 0 "
        f"2133 2 {v_sel_item} {local_var(3)} "
        f"900 1 {prsnt_id(idx_prsnt_all_items)} 3 0 "
        f"3 0 3 0 "
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

    # 6. Update languages/cns/quick_strings.csv
    cns_csv = os.path.join(MODULE_DIR, "languages/cns/quick_strings.csv")
    if os.path.exists(cns_csv):
        with open(cns_csv, "r", encoding="utf-8", errors="ignore") as f:
            cns_lines = f.readlines()
            
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
            ("qstr_tree_hungary", "匈牙利王国"),
            ("qstr_tree_moldavia", "摩尔达维亚公国"),
            ("qstr_tree_ottoman", "奥斯曼帝国"),
            ("qstr_tree_wallachia", "瓦拉几亚公国"),
            ("qstr_tree_croatia", "克罗地亚王国"),
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
            ("qstr_cat_crossbows", "弩类武器"),
            ("qstr_cat_arrows", "箭矢弹药"),
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
            cns_lines = [l for l in cns_lines if not l.startswith(k + "|")]
            cns_lines.append(f"{k}|{v}\r\n")
            cns_updated = True
        if cns_updated:
            with open(cns_csv, "w", encoding="utf-8") as f:
                f.writelines(cns_lines)
            print("Updated languages/cns/quick_strings.csv with Chinese localizations.")

    # 7. Update menus.txt with tagged presentation references
    menus_path = os.path.join(MODULE_DIR, "menus.txt")
    with open(menus_path, "r", encoding="latin1") as f:
        menus_content = f.read()
    
    import re
    menus_content = re.sub(
        r'(mno_troop_tree_viewer\s+\d+\s+[^\.]+\.\s+1\s+900\s+1\s+)\d+',
        r'\g<1>' + str(prsnt_id(idx_prsnt_troop_tree)),
        menus_content
    )
    menus_content = re.sub(
        r'(mno_all_items\s+\d+\s+[^\.]+\.\s+\d+\s+2133\s+2\s+\d+\s+0\s+900\s+1\s+)\d+',
        r'\g<1>' + str(prsnt_id(idx_prsnt_all_items)),
        menus_content
    )
    with open(menus_path, "w", encoding="latin1") as f:
        f.write(menus_content)
    print("Updated menus.txt with tagged presentation references.")

    print("ALL INSTALLATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run()
