import os, sys, shutil

BASE_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules"
MOD_DIR = os.path.join(BASE_DIR, "Carpathian Solid & Shade")
VN_DIR = os.path.join(BASE_DIR, "World of Vasnar")
SZ_DIR = os.path.join(BASE_DIR, "Sayazn（美化脸）")

MOD_SCENE_DIR = os.path.join(MOD_DIR, "SceneObj")
VN_SCENE_DIR = os.path.join(VN_DIR, "SceneObj")
SZ_SCENE_DIR = os.path.join(SZ_DIR, "SceneObj")

# 15 Town mapping table
# (Target Town Num, Target Town Name, Source Mod, Source Town Num/Prefix)
TOWN_MAPPINGS = [
    (1,  "布达",        "VN", "town_26"), # Bruvik
    (2,  "赛格德",      "VN", "town_6"),  # Effalen
    (3,  "佩奇",        "VN", "town_7"),  # Wittal
    (4,  "克劳森堡",    "VN", "town_23"), # Ebenhof
    (5,  "锡比乌",      "VN", "town_4"),  # Videns
    (6,  "贝尔格莱德",  "VN", "town_24"), # Vilingen
    (7,  "特尔戈维什特","VN", "town_35"), # Elbzig
    (8,  "布加勒斯特",  "VN", "town_10"), # Drakenheir Manor
    (9,  "布勒伊拉",    "VN", "town_1"),  # Havenmour
    (10, "萨格勒布",    "VN", "town_28"), # Tollan
    (11, "苏恰瓦",      "VN", "town_34"), # Sofya
    (12, "雅西",        "VN", "town_31"), # Prav
    (13, "阿克曼",      "SZ", "town_17"), # El Mit
    (17, "索菲亚",      "SZ", "town_27"), # Kethem (bowman_ishtar_town_1)
    (18, "萨洛尼卡",    "SZ", "town_4"),  # Khun
]

SUB_SCENE_TYPES = ["center", "castle", "tavern", "prison", "arena", "store", "walls"]

# S&S Special Redlist items to preserve (unique storyline relics)
# (Target Scn, Prop Name, Approx Place Offset)
SPECIAL_RELICS = {
    "scn_town_2_center": "spr_container_small_chest",
    "scn_town_3_store": "spr_caskofamontillado",
    "scn_town_5_center": "spr_container_small_chest",
    "scn_town_6_prison": "spr_thirteen",
    "scn_town_8_center": "spr_container_chest_b",
    "scn_town_9_tavern": "spr_thirteen",
}

def load_scenes_txt(path):
    with open(path, "r", encoding="latin1") as f:
        lines = f.readlines()
    scn_dict = {}
    for l in lines:
        parts = l.strip().split()
        if len(parts) >= 2:
            scn_dict[parts[0]] = l.strip()
    return lines, scn_dict

def run_deployment():
    print("=== Deploying Complete Coherent Town Suites ===")
    
    # Load scenes.txt from all mods
    mod_scenes_path = os.path.join(MOD_DIR, "scenes.txt")
    vn_scenes_path = os.path.join(VN_DIR, "scenes.txt")
    sz_scenes_path = os.path.join(SZ_DIR, "scenes.txt")
    
    mod_lines, mod_scn_map = load_scenes_txt(mod_scenes_path)
    _, vn_scn_map = load_scenes_txt(vn_scenes_path)
    _, sz_scn_map = load_scenes_txt(sz_scenes_path)
    
    deployed_files = 0
    scenes_updated = 0
    
    for t_id, t_cn, src_mod, src_prefix in TOWN_MAPPINGS:
        print(f"\nProcessing Town {t_id} ({t_cn}) from {src_mod} {src_prefix}...")
        src_scene_dir = VN_SCENE_DIR if src_mod == "VN" else SZ_SCENE_DIR
        src_map = vn_scn_map if src_mod == "VN" else sz_scn_map
        
        for sub in SUB_SCENE_TYPES:
            target_scn = f"scn_town_{t_id}_{sub}"
            
            # Determine source file name
            if src_mod == "SZ" and t_id == 17:
                # Sayazn town 27 Kethem uses bowman_ishtar_town_1
                if sub == "center":
                    src_scn = "scn_bowman_ishtar_town_1_center"
                elif sub == "walls":
                    src_scn = "scn_bowman_ishtar_town_1_walls"
                elif sub == "castle":
                    src_scn = "scn_town_27_castle"
                elif sub == "tavern":
                    src_scn = "scn_town_27_tavern"
                elif sub == "prison":
                    src_scn = "scn_town_27_prison"
                elif sub == "arena":
                    src_scn = "scn_town_27_arena"
                elif sub == "store":
                    src_scn = "scn_town_27_store"
                else:
                    src_scn = f"scn_{src_prefix}_{sub}"
            else:
                src_scn = f"scn_{src_prefix}_{sub}"
            
            src_file = os.path.join(src_scene_dir, f"{src_scn}.sco")
            target_file = os.path.join(MOD_SCENE_DIR, f"{target_scn}.sco")
            
            if os.path.exists(src_file):
                # Copy complete coherent sub-scene file
                shutil.copy2(src_file, target_file)
                deployed_files += 1
                # print(f"  [OK] Copied {src_scn}.sco -> {target_scn}.sco ({os.path.getsize(target_file)//1024} KB)")
            else:
                # Some towns might not have custom arena or store, check fallback
                pass
            
            # Update scenes.txt terrain parameters
            if src_scn in src_map and target_scn in mod_scn_map:
                src_line = src_map[src_scn]
                src_tokens = src_line.split()
                # target line has target_scn and target name
                # format: <scn_name> <flags> <mesh> <mesh> <minx> <miny> <maxx> <maxy> <water> <hex_terrain>
                # tokens: 0: name, 1: id, 2..: parameters
                new_line = f"{target_scn} {target_scn[4:]} " + " ".join(src_tokens[2:])
                mod_scn_map[target_scn] = new_line
                scenes_updated += 1

    # Write updated scenes.txt
    new_mod_lines = []
    for l in mod_lines:
        sname = l.strip().split()[0] if l.strip() else ""
        if sname in mod_scn_map:
            new_mod_lines.append(mod_scn_map[sname] + "\r\n")
        else:
            new_mod_lines.append(l)
            
    with open(mod_scenes_path, "w", encoding="latin1") as f:
        f.writelines(new_mod_lines)
        
    print(f"\nSUCCESS: Deployed {deployed_files} sub-scene .sco files!")
    print(f"SUCCESS: Synchronized {scenes_updated} terrain records in scenes.txt!")

if __name__ == "__main__":
    run_deployment()
