#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_equipment_packs.py
Stage 5 Pre-Execution: Import equipment packs from 'World of Vasnar' and 'Sayazn'
into Carpathian Solid & Shade with zero-drift protection for existing 906 items.
"""

import os
import sys
import glob
import re
import shutil

CARPATHIAN_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
VASNAR_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/World of Vasnar"
SAYAZN_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Sayazn（美化脸）"
COMM_RES_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/CommonRes"

EXCLUDED_BRFS = {
    "materials_face_gen.brf", "meshes_face_gen.brf", "textures_face_gen.brf",
    "shaders.brf", "core_shaders.brf", "materials.brf", "skeletons.brf",
    "uimeshes.brf", "body_meshes.brf", "early_load.brf", "core_materials.brf",
    "materials_face_gen_gaolu.brf", "sayazn_materials_face_gen.brf"
}

def split_item_chunks(path):
    with open(path, "r", errors="ignore") as f:
        lines = f.readlines()
    chunks = []
    current_chunk = []
    for line in lines[2:]:
        if line.strip().startswith("itm_"):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [line]
        elif current_chunk:
            current_chunk.append(line)
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def get_brf_mesh_set(brf_path):
    with open(brf_path, "rb") as f:
        data = f.read()
    tokens = re.findall(rb"[a-zA-Z0-9_\-\.]{2,}", data)
    return {t.decode("ascii", errors="ignore").lower() for t in tokens}

def match_items(chunks, res_dir, comm_meshes, existing_ids):
    brf_meshes = {}
    for p in glob.glob(os.path.join(res_dir, "*.brf")):
        bname = os.path.basename(p)
        brf_meshes[bname] = get_brf_mesh_set(p)

    matched = []
    used_brfs = set()
    for c in chunks:
        parts = c[0].split()
        itm_id = parts[0]
        if itm_id in existing_ids:
            continue
        try:
            num_m = int(parts[3])
            meshes = [parts[4 + i * 2] for i in range(num_m)]
        except Exception:
            continue

        all_found = True
        item_brfs = set()
        for m in meshes:
            ml = m.lower()
            if ml in comm_meshes:
                continue
            found = False
            for bname, mset in brf_meshes.items():
                if ml in mset:
                    found = True
                    item_brfs.add(bname)
                    break
            if not found:
                all_found = False
                break
        
        if all_found:
            matched.append((c, item_brfs))
            used_brfs |= item_brfs

    return matched, used_brfs

def main():
    print("=== Starting Equipment Packs Import Pipeline ===")
    
    # 1. Load CommonRes tokens
    print("[1/7] Indexing CommonRes meshes...")
    comm_meshes = set()
    for p in glob.glob(os.path.join(COMM_RES_DIR, "*.brf")):
        comm_meshes |= get_brf_mesh_set(p)
    print(f"  CommonRes meshes indexed: {len(comm_meshes)}")

    # 2. Parse Carpathian existing items
    c_item_file = os.path.join(CARPATHIAN_DIR, "item_kinds1.txt")
    c_chunks = split_item_chunks(c_item_file)
    c_ids = set(c[0].split()[0] for c in c_chunks)
    print(f"[2/7] Carpathian baseline items: {len(c_chunks)}")
    assert len(c_chunks) == 906, f"Expected 906 baseline items, got {len(c_chunks)}"

    # 3. Match Vasnar items
    print("[3/7] Matching World of Vasnar items...")
    v_chunks = split_item_chunks(os.path.join(VASNAR_DIR, "item_kinds1.txt"))
    v_matched, v_brfs = match_items(v_chunks, os.path.join(VASNAR_DIR, "Resource"), comm_meshes, c_ids)
    print(f"  Vasnar matched items: {len(v_matched)} (using {len(v_brfs)} BRFs)")

    # 4. Match Sayazn items
    print("[4/7] Matching Sayazn items...")
    s_chunks = split_item_chunks(os.path.join(SAYAZN_DIR, "item_kinds1.txt"))
    all_seen_ids = set(c_ids)
    for c, _ in v_matched:
        all_seen_ids.add(c[0].split()[0])
    s_matched, s_brfs = match_items(s_chunks, os.path.join(SAYAZN_DIR, "Resource"), comm_meshes, all_seen_ids)
    print(f"  Sayazn matched items: {len(s_matched)} (using {len(s_brfs)} BRFs)")

    # Material BRFs to include
    v_mat_extras = {"Innistrad_Materials.brf", "Tempered_mat.brf", "pm_materials.brf"}
    s_mat_extras = {"sayazn_materials.brf", "sayazn_uniforms_materials.brf", "OSP_Jaakko_Materials.brf"}
    
    v_brfs_to_copy = (v_brfs | v_mat_extras) - EXCLUDED_BRFS
    s_brfs_to_copy = (s_brfs | s_mat_extras) - EXCLUDED_BRFS

    # 5. Copy BRFs with prefix and copy DDS textures
    print("[5/7] Copying BRF resources and textures...")
    c_res_dir = os.path.join(CARPATHIAN_DIR, "Resource")
    c_tex_dir = os.path.join(CARPATHIAN_DIR, "Textures")
    
    added_mod_resources = []
    
    # Copy Vasnar BRFs
    for b in sorted(list(v_brfs_to_copy)):
        src = os.path.join(VASNAR_DIR, "Resource", b)
        dst_name = f"vn_{b}"
        dst = os.path.join(c_res_dir, dst_name)
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy2(src, dst)
        res_stem = os.path.splitext(dst_name)[0]
        added_mod_resources.append(res_stem)

    # Copy Sayazn BRFs
    for b in sorted(list(s_brfs_to_copy)):
        src = os.path.join(SAYAZN_DIR, "Resource", b)
        dst_name = f"sz_{b}"
        dst = os.path.join(c_res_dir, dst_name)
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy2(src, dst)
        res_stem = os.path.splitext(dst_name)[0]
        added_mod_resources.append(res_stem)

    print(f"  Copied/Registered {len(added_mod_resources)} new BRF resource files.")

    # Incremental copy textures from Vasnar
    v_tex_copied = 0
    for f in os.listdir(os.path.join(VASNAR_DIR, "Textures")):
        if f.lower().endswith(".dds"):
            dst = os.path.join(c_tex_dir, f)
            if not os.path.exists(dst):
                src = os.path.join(VASNAR_DIR, "Textures", f)
                shutil.copy2(src, dst)
                v_tex_copied += 1
    print(f"  Incrementally copied {v_tex_copied} textures from Vasnar.")

    # Incremental copy textures from Sayazn
    s_tex_copied = 0
    for f in os.listdir(os.path.join(SAYAZN_DIR, "Textures")):
        if f.lower().endswith(".dds"):
            dst = os.path.join(c_tex_dir, f)
            if not os.path.exists(dst):
                src = os.path.join(SAYAZN_DIR, "Textures", f)
                shutil.copy2(src, dst)
                s_tex_copied += 1
    print(f"  Incrementally copied {s_tex_copied} textures from Sayazn.")

    # Update module.ini
    ini_path = os.path.join(CARPATHIAN_DIR, "module.ini")
    with open(ini_path, "r", errors="ignore") as f:
        ini_content = f.read()

    ini_additions = []
    for r in added_mod_resources:
        directive = f"load_mod_resource = {r}"
        if directive not in ini_content:
            ini_additions.append(directive)

    if ini_additions:
        with open(ini_path, "a") as f:
            f.write("\n# === Imported Vasnar & Sayazn Equipment Packs ===\n")
            for d in ini_additions:
                f.write(f"{d}\n")
        print(f"  Appended {len(ini_additions)} resource entries to module.ini")

    # 6. Append new items to item_kinds1.txt
    print("[6/7] Updating item_kinds1.txt...")
    total_new_items = []
    current_ids = set(c_ids)

    # Process Vasnar items
    for c, _ in v_matched:
        lines = list(c)
        parts = lines[0].split()
        itm_id = parts[0]
        if itm_id in current_ids:
            new_id = f"itm_vn_{itm_id[4:]}"
            parts[0] = new_id
            lines[0] = " " + " ".join(parts) + "\n"
            current_ids.add(new_id)
        else:
            current_ids.add(itm_id)
        total_new_items.append(lines)

    # Process Sayazn items
    for c, _ in s_matched:
        lines = list(c)
        parts = lines[0].split()
        itm_id = parts[0]
        if itm_id in current_ids:
            new_id = f"itm_sz_{itm_id[4:]}"
            parts[0] = new_id
            lines[0] = " " + " ".join(parts) + "\n"
            current_ids.add(new_id)
        else:
            current_ids.add(itm_id)
        total_new_items.append(lines)

    grand_total_count = len(c_chunks) + len(total_new_items)
    print(f"  Grand total items: {grand_total_count} ({len(c_chunks)} baseline + {len(total_new_items)} new)")

    # Write item_kinds1.txt
    with open(c_item_file, "w") as f:
        f.write("itemsfile version 3\n")
        f.write(f"{grand_total_count}\n")
        # Write 906 baseline items untouched
        for c in c_chunks:
            for l in c:
                f.write(l)
            if not c[-1].endswith("\n"):
                f.write("\n")
        # Write new items
        for c in total_new_items:
            for l in c:
                f.write(l)
            if not c[-1].endswith("\n"):
                f.write("\n")

    print("  item_kinds1.txt updated successfully.")

    # 7. Update scripts.txt for all_items_populate_category
    print("[7/7] Updating all_items_populate_category in scripts.txt...")
    scripts_path = os.path.join(CARPATHIAN_DIR, "scripts.txt")
    with open(scripts_path, "r") as f:
        s_lines = f.readlines()

    target_idx = -1
    for i, l in enumerate(s_lines):
        if "all_items_populate_category" in l:
            target_idx = i + 1
            break

    if target_idx != -1:
        code_line = s_lines[target_idx]
        # Replace 0 910 with 0 8000 for clearing slots
        code_line = code_line.replace(" 0 910 ", " 0 8000 ")
        # Replace 1 902 with 1 <grand_total_count> for item iteration
        code_line = code_line.replace(" 1 902 ", f" 1 {grand_total_count} ")
        s_lines[target_idx] = code_line
        with open(scripts_path, "w") as f:
            f.writelines(s_lines)
        print(f"  scripts.txt updated: loop extended to 1..{grand_total_count}, slots to 8000.")

    # 8. Clean up skins.txt hair_black
    skins_path = os.path.join(CARPATHIAN_DIR, "skins.txt")
    with open(skins_path, "r") as f:
        skins_lines = f.readlines()
    
    modified_skins = False
    for i in range(len(skins_lines)):
        if "hair_blonde  hair_red  hair_brunette  hair_black  hair_white" in skins_lines[i]:
            skins_lines[i] = skins_lines[i].replace(
                "5  hair_blonde  hair_red  hair_brunette  hair_black  hair_white",
                "1  hair_blonde"
            )
            modified_skins = True
        if "beard_blonde  beard_red  beard_brunette  beard_black  beard_white" in skins_lines[i]:
            skins_lines[i] = skins_lines[i].replace(
                "5  beard_blonde  beard_red  beard_brunette  beard_black  beard_white",
                "1  beard_blonde"
            )
            modified_skins = True

    if modified_skins:
        with open(skins_path, "w") as f:
            f.writelines(skins_lines)
        print("  skins.txt hair_black definitions sanitized to standard 1 hair_blonde.")

    print("=== Pipeline Complete! ===")

if __name__ == "__main__":
    main()
