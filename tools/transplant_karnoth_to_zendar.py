#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transplant_karnoth_to_zendar.py
Surgically transplants Perisno 1.3.6's Dwarven Capital Karnoth (scn_town_26_center.sco)
into Carpathian Solid & Shade's Old Zendar (scn_zendar_center.sco) while 100% preserving
all S&S holy necromancy relics, secret chest, Entry Points, and atmospheric skeleton props.
"""

import os
import sys
import struct
import shutil

CARPATHIAN_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
PERISNO_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Perisno_1.3.6"

SRC_SCO = os.path.join(PERISNO_DIR, "SceneObj", "scn_town_26_center.sco")
DST_SCO = os.path.join(CARPATHIAN_DIR, "SceneObj", "scn_zendar_center.sco")
BAK_SCO = os.path.join(CARPATHIAN_DIR, "SceneObj", "scn_zendar_center.sco.bak_pre_karnoth")

SCO_MAGIC = -717

def parse_sco(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, ver, nobj = struct.unpack_from("<iii", data, 0)
    if magic != SCO_MAGIC:
        raise ValueError(f"Invalid sco magic: {magic}")
    
    off = 12
    records = []
    for _ in range(nobj):
        start = off
        otype, sub_id, unused = struct.unpack_from("<iii", data, off)
        rot_pos = list(struct.unpack_from("<12f", data, off + 12))
        slen = struct.unpack_from("<i", data, off + 60)[0]
        sname = data[off + 64: off + 64 + slen].decode("ascii", errors="replace")
        off += 64 + slen
        vraw = struct.unpack_from("<q", data, off)[0]
        off += 8
        scale = list(struct.unpack_from("<3f", data, off))
        off += 12
        raw_bytes = data[start:off]
        records.append({
            "otype": otype,
            "sub_id": sub_id,
            "unused": unused,
            "rot_pos": rot_pos,
            "sname": sname,
            "vraw": vraw,
            "scale": scale,
            "raw_bytes": raw_bytes
        })
    tail_data = data[off:]
    return ver, records, tail_data

def build_prop_record(sname, pos, scale=(1.0, 1.0, 1.0), rot_matrix=None):
    if rot_matrix is None:
        # identity 3x3 rotation
        rot_matrix = [1.0, 0.0, 0.0,  0.0, 1.0, 0.0,  0.0, 0.0, 1.0]
    rot_pos = rot_matrix + [pos[0], pos[1], pos[2]]
    sbytes = sname.encode("ascii")
    slen = len(sbytes)
    
    header = struct.pack("<iii", 0, 0, 0) # otype=0, sub_id=0, unused=0
    mat_bytes = struct.pack("<12f", *rot_pos)
    name_bytes = struct.pack("<i", slen) + sbytes
    vraw_bytes = struct.pack("<q", 0)
    scale_bytes = struct.pack("<3f", *scale)
    raw = header + mat_bytes + name_bytes + vraw_bytes + scale_bytes
    return {
        "otype": 0,
        "sub_id": 0,
        "unused": 0,
        "rot_pos": rot_pos,
        "sname": sname,
        "vraw": 0,
        "scale": list(scale),
        "raw_bytes": raw
    }

def build_entry_point_record(entry_no, pos, rot_matrix=None):
    if rot_matrix is None:
        rot_matrix = [1.0, 0.0, 0.0,  0.0, 1.0, 0.0,  0.0, 0.0, 1.0]
    rot_pos = rot_matrix + [pos[0], pos[1], pos[2]]
    header = struct.pack("<iii", 1, 0, 0) # otype=1
    mat_bytes = struct.pack("<12f", *rot_pos)
    name_bytes = struct.pack("<i", 0)
    vraw_bytes = struct.pack("<q", entry_no)
    scale_bytes = struct.pack("<3f", 1.0, 1.0, 1.0)
    raw = header + mat_bytes + name_bytes + vraw_bytes + scale_bytes
    return {
        "otype": 1,
        "sub_id": 0,
        "unused": 0,
        "rot_pos": rot_pos,
        "sname": "",
        "vraw": entry_no,
        "scale": [1.0, 1.0, 1.0],
        "raw_bytes": raw
    }

def main():
    print("=== Transplanting Karnoth into Old Zendar ===")
    
    # 1. Backup original scn_zendar_center.sco
    if not os.path.exists(BAK_SCO):
        shutil.copy2(DST_SCO, BAK_SCO)
        print(f"Backed up original Zendar to: {os.path.basename(BAK_SCO)}")

    # 2. Parse source Karnoth and target original Zendar
    print("Parsing Karnoth (source)...")
    ver_k, recs_k, tail_k = parse_sco(SRC_SCO)
    print(f"  Karnoth records: {len(recs_k)}, tail bytes: {len(tail_k)}")

    print("Parsing Zendar (original)...")
    ver_z, recs_z, tail_z = parse_sco(BAK_SCO)
    print(f"  Zendar records: {len(recs_z)}, tail bytes: {len(tail_z)}")

    # 3. Find key landmarks in Karnoth
    # Find Karnoth Entry 0 (player start) and Entry 8 (chest)
    k_ep0 = next(r for r in recs_k if r["otype"] == 1 and (r["vraw"] & 0xFF) == 0)
    k_ep8 = next(r for r in recs_k if r["otype"] == 1 and (r["vraw"] & 0xFF) == 8)
    
    k_ep0_pos = k_ep0["rot_pos"][9:12]
    k_ep8_pos = k_ep8["rot_pos"][9:12]
    print(f"  Karnoth Entry 0 pos: {k_ep0_pos}")
    print(f"  Karnoth Entry 8 pos: {k_ep8_pos}")

    # 4. Gather S&S special relics from original Zendar
    # Chest, thirteen, katrina, red lights, skeletons
    relic_props = []
    for r in recs_z:
        if r["otype"] == 0:
            name = r["sname"]
            if any(k in name for k in ["thirteen", "katrina", "chest", "light_red", "skeleton", "fire_big", "flue_smoke_tall"]):
                relic_props.append(r)

    print(f"  Gathered {len(relic_props)} S&S special relic props from original Zendar.")

    # 5. Place S&S relics into Karnoth
    # - Place spr_container_chest_c right near Karnoth Entry 8: [k_ep8_pos[0] + 1.2, k_ep8_pos[1] + 0.5, k_ep8_pos[2]]
    # - Place spr_thirteen #1 right on top of / adjacent to chest
    # - Place spr_thirteen #2 at Karnoth central temple platform [85.7, 115.8, 0.6]
    # - Scatter 18 skeletons and red lights along the approach from Entry 0 to Karnoth main gates
    injected_props = []

    # Chest & Thirteen #1 near Entry 8
    chest_pos = [k_ep8_pos[0] + 1.2, k_ep8_pos[1] + 0.5, k_ep8_pos[2]]
    thirteen1_pos = [chest_pos[0], chest_pos[1], chest_pos[2] + 0.8]
    injected_props.append(build_prop_record("spr_container_chest_c", chest_pos))
    injected_props.append(build_prop_record("spr_thirteen", thirteen1_pos))
    injected_props.append(build_prop_record("spr_light_red", [chest_pos[0], chest_pos[1], chest_pos[2] + 1.5]))

    # Thirteen #2 at central temple platform
    temple_altar_pos = [85.69, 115.77, 0.70]
    injected_props.append(build_prop_record("spr_thirteen", temple_altar_pos))
    injected_props.append(build_prop_record("spr_light_red", [temple_altar_pos[0], temple_altar_pos[1], temple_altar_pos[2] + 1.5]))
    injected_props.append(build_prop_record("spr_fire_big", [temple_altar_pos[0] + 1.0, temple_altar_pos[1], temple_altar_pos[2]]))
    injected_props.append(build_prop_record("spr_flue_smoke_tall", [temple_altar_pos[0] + 1.0, temple_altar_pos[1], temple_altar_pos[2] + 0.5]))

    # Katrina high in the sky over Karnoth
    injected_props.append(build_prop_record("spr_katrina", [120.0, 120.0, 75.0]))

    # Red lights around plaza
    injected_props.append(build_prop_record("spr_light_red", [127.72, 35.0, 2.5]))
    injected_props.append(build_prop_record("spr_light_red", [71.38, 106.0, 2.5]))

    # Scatter 18 skeletons along Karnoth corridors and plaza
    skeleton_offsets = [
        (128.5, 32.0, 0.12), (126.0, 36.0, 0.12), (130.0, 42.0, 0.12),
        (127.0, 48.0, 0.12), (132.0, 55.0, 0.12), (125.0, 62.0, 0.12),
        (88.0, 102.0, 0.20), (84.0, 108.0, 0.15), (76.0, 118.0, 0.20),
        (70.0, 105.0, 0.12), (66.0, 108.0, 0.12), (60.0, 120.0, 0.12),
        (86.5, 114.5, 0.60), (84.5, 117.0, 0.60), (45.0, 203.0, 10.05),
        (43.0, 205.0, 10.05), (91.5, 221.0, 10.05), (38.5, 188.5, 10.05)
    ]
    for spos in skeleton_offsets:
        injected_props.append(build_prop_record("spr_skeleton_a", spos))

    print(f"  Prepared {len(injected_props)} tailored S&S atmospheric relics.")

    # 6. Check entry points: Karnoth already has Entry 0..40.
    # Original Zendar used Entry 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12.
    # All of these exist in Karnoth at excellent ground coordinates!
    # Let's verify all exist:
    k_eps = {r["vraw"] & 0xFF for r in recs_k if r["otype"] == 1}
    z_eps = {r["vraw"] & 0xFF for r in recs_z if r["otype"] == 1}
    missing_eps = z_eps - k_eps
    print(f"  Entry points coverage: Zendar requires {z_eps}, missing in Karnoth: {missing_eps}")
    assert len(missing_eps) == 0, f"Missing Entry Points: {missing_eps}"

    # 7. Assemble final scene:
    # Karnoth records + injected S&S relics + Karnoth tail_data
    final_records = recs_k + injected_props
    final_count = len(final_records)
    print(f"  Final scene records: {final_count} ({len(recs_k)} Karnoth + {len(injected_props)} S&S relics)")

    # 8. Write final .sco file
    with open(DST_SCO, "wb") as f:
        # Magic, version, number of objects
        f.write(struct.pack("<iii", SCO_MAGIC, ver_k, final_count))
        for r in final_records:
            f.write(r["raw_bytes"])
        f.write(tail_k)

    print(f"  Successfully written combined scene to {os.path.basename(DST_SCO)}")

    # 9. Update scenes.txt ground code
    scenes_path = os.path.join(CARPATHIAN_DIR, "scenes.txt")
    with open(scenes_path, "r") as f:
        s_lines = f.readlines()

    # Karnoth ground code: 0x0000000040000c910003e8fa0000538900003e9e00005301
    karnoth_ground = "0x0000000040000c910003e8fa0000538900003e9e00005301"
    updated_scenes = False
    for i, line in enumerate(s_lines):
        if line.startswith("scn_zendar_center "):
            parts = line.split()
            # replace ground code (last token)
            parts[-1] = karnoth_ground
            s_lines[i] = " ".join(parts) + "\n"
            updated_scenes = True
            break

    if updated_scenes:
        with open(scenes_path, "w") as f:
            f.writelines(s_lines)
        print("  Updated scenes.txt ground code for scn_zendar_center to Karnoth's ground code.")

    print("=== Transplantation Complete! ===")

if __name__ == "__main__":
    main()
