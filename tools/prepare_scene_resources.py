#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
VASNAR_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/World of Vasnar"
SAYAZN_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Sayazn（美化脸）"

# 1. 29 Core Scene BRFs
brf_sources = [
    ("Innistrad_architecture", VASNAR_DIR),
    ("Innistrad_architecture_2", VASNAR_DIR),
    ("Innistrad_Props", VASNAR_DIR),
    ("Innistrad_vampire_houses", VASNAR_DIR),
    ("OSP_Italian_Props", VASNAR_DIR),
    ("ado_wood_props", VASNAR_DIR),
    ("ado_med_props2", VASNAR_DIR),
    ("minidungeon_props", VASNAR_DIR),
    ("Tosk_buildings", VASNAR_DIR),
    ("1257doors", VASNAR_DIR),
    ("castle_greystones", VASNAR_DIR),
    ("viking_houses", VASNAR_DIR),
    ("snowy_houses", VASNAR_DIR),
    ("wall_meshes1", VASNAR_DIR),
    ("churches", VASNAR_DIR),
    ("andal_castle", VASNAR_DIR),
    ("arabian_castle_mod", VASNAR_DIR),
    ("mansur_castles", VASNAR_DIR),
    ("town_houses_d", VASNAR_DIR),
    ("arabian_houses", VASNAR_DIR),
    ("castle_e", VASNAR_DIR),
    ("castle_i", VASNAR_DIR),
    ("1792_scene", SAYAZN_DIR),
    ("sayazn_buildings", SAYAZN_DIR),
    ("gondor_buildings_llew", SAYAZN_DIR),
    ("sayazn_castle_d", SAYAZN_DIR),
    ("sayazn_castle_e", SAYAZN_DIR),
    ("sayazn_arabian_houses", SAYAZN_DIR),
    ("sayazn_arabian_castle", SAYAZN_DIR),
]

print("[*] Copying 29 core scene BRFs...")
copied_brfs = []
for name, sdir in brf_sources:
    src = os.path.join(sdir, "Resource", name + ".brf")
    dst = os.path.join(MOD_DIR, "Resource", name + ".brf")
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copyfile(src, dst)
        copied_brfs.append(name)
        print(f"  + Copied {name}.brf ({os.path.getsize(dst)} bytes)")
    elif os.path.exists(dst):
        copied_brfs.append(name)
        print(f"  = Exists {name}.brf")

print(f"[+] Total BRFs ready: {len(copied_brfs)}")

# 2. Register in module.ini
print("[*] Registering in module.ini...")
with open(os.path.join(MOD_DIR, "module.ini"), "r", encoding="utf-8", errors="ignore") as f:
    ini_lines = f.readlines()

existing_entries = set(l.strip() for l in ini_lines)
new_entries = []
for name in copied_brfs:
    line1 = f"load_mod_resource = {name}"
    line2 = f"load_resource = {name}"
    if line1 not in existing_entries and line2 not in existing_entries:
        new_entries.append(f"load_mod_resource = {name}\n")

if new_entries:
    # Insert before scan_module_textures or at the end
    idx = len(ini_lines)
    for i, l in enumerate(ini_lines):
        if "scan_module_textures" in l:
            idx = i
            break
    ini_lines[idx:idx] = new_entries
    with open(os.path.join(MOD_DIR, "module.ini"), "w", encoding="utf-8") as f:
        f.writelines(ini_lines)
    print(f"[+] Registered {len(new_entries)} entries in module.ini")
else:
    print("[+] All entries already in module.ini")

# 3. Incremental copy Textures from Vasnar and Sayazn
print("[*] Incrementally copying missing textures from source mods...")
target_tex = set(os.listdir(os.path.join(MOD_DIR, "Textures")))
copied_tex = 0
for sdir in [VASNAR_DIR, SAYAZN_DIR]:
    stex_dir = os.path.join(sdir, "Textures")
    if os.path.exists(stex_dir):
        for f in os.listdir(stex_dir):
            if f.endswith(".dds") and f not in target_tex:
                shutil.copyfile(os.path.join(stex_dir, f), os.path.join(MOD_DIR, "Textures", f))
                target_tex.add(f)
                copied_tex += 1

print(f"[+] Incrementally copied {copied_tex} textures.")
