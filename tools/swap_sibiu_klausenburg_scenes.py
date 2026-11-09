#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade (1521) — 锡比乌 (Sibiu, town_3) 与 克劳森堡 (Kolozsvar, town_5)
城市场景、全套子场景、攻城场景、路人NPC与35座红线机制无损互换迁移工具
"""

import os
import sys
import shutil

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
SCENE_DIR = os.path.join(MOD_DIR, "SceneObj")
SCENES_TXT = os.path.join(MOD_DIR, "scenes.txt")

sys.path.append(os.path.join(MOD_DIR, "tools"))
from sco_anchor_transplanter import parse_sco, write_sco

SUB_TYPES = ["center", "castle", "tavern", "store", "arena", "prison", "walls", "alley"]

# Scene IDs in scenes.txt:
# town_3: center=44, castle=63, tavern=82, store=101, arena=120, prison=139, walls=158, alley=177
# town_5: center=46, castle=65, tavern=84, store=103, arena=122, prison=141, walls=160, alley=179
SCENE_ID_PAIRS = [
    ("center", 44, 46),
    ("castle", 63, 65),
    ("tavern", 82, 84),
    ("store", 101, 103),
    ("arena", 120, 122),
    ("prison", 139, 141),
    ("walls", 158, 160),
    ("alley", 177, 179),
]


def backup_files():
    bak_dir = os.path.join(SCENE_DIR, "bak_swap_t3_t5")
    os.makedirs(bak_dir, exist_ok=True)
    for sub in SUB_TYPES:
        for t in [3, 5]:
            fname = f"scn_town_{t}_{sub}.sco"
            src = os.path.join(SCENE_DIR, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(bak_dir, fname))
    shutil.copy2(SCENES_TXT, SCENES_TXT + ".bak_swap_t3_t5")
    print(f"1. Backed up town_3 and town_5 .sco files and scenes.txt to {bak_dir}")


def swap_scenes_txt():
    print("2. Swapping geometry, meshes, boundaries, and terrain parameters in scenes.txt...")
    lines = open(SCENES_TXT, "r", encoding="latin1").read().splitlines()
    count = int(lines[1])

    # Parse each scene: idx = 2 + sc_id * 4
    # Line 0: <scn_name> <tag> <mesh1> <mesh2> <minx> <miny> <maxx> <maxy> <water_level> <terrain_hash>
    # Line 1: <extra / line2>
    # Line 2: <chests>
    # Line 3: <outer_terrain>

    for sub, id3, id5 in SCENE_ID_PAIRS:
        idx3 = 2 + id3 * 4
        idx5 = 2 + id5 * 4

        # Read line 0 tokens
        t3_tokens = lines[idx3].split()
        t5_tokens = lines[idx5].split()

        # Swap geometry parameters (from index 2 onwards)
        new_line_3 = t3_tokens[0] + " " + t3_tokens[1] + " " + " ".join(t5_tokens[2:])
        new_line_5 = t5_tokens[0] + " " + t5_tokens[1] + " " + " ".join(t3_tokens[2:])
        lines[idx3] = new_line_3
        lines[idx5] = new_line_5

        # Swap line 1 (extra)
        l1_3 = lines[idx3 + 1]
        l1_5 = lines[idx5 + 1]
        lines[idx3 + 1] = l1_5
        lines[idx5 + 1] = l1_3

        # Swap line 3 (outer terrain)
        l3_3 = lines[idx3 + 3]
        l3_5 = lines[idx5 + 3]
        lines[idx3 + 3] = l3_5
        lines[idx5 + 3] = l3_3

        # Line 2 (chests):
        # We explicitly enforce the Redlist storyline rules:
        # scn_town_3_store (101): MUST have "1  100000" (Cask of Amontillado / bonus_chest_4)
        # scn_town_5_store (103): MUST have "  0 "
        # scn_town_5_center (46): MUST have "1  100000" (Kolozsvar Hidden Chest / bonus_chest_2)
        # scn_town_3_center (44): MUST have "  0 "
        # castles retain their player chests ("1  100000")
        if sub == "store":
            lines[idx3 + 2] = "1  100000"
            lines[idx5 + 2] = "  0 "
        elif sub == "center":
            lines[idx3 + 2] = "  0 "
            lines[idx5 + 2] = "1  100000"
        elif sub == "castle":
            lines[idx3 + 2] = "1  100000"
            lines[idx5 + 2] = "1  100000"

    # Write back scenes.txt with CRLF
    open(SCENES_TXT, "w", encoding="latin1", newline="").write("\r\n".join(lines) + "\r\n")
    print("   Updated scenes.txt successfully!")


def swap_and_calibrate_scos():
    print("3. Swapping all 8 sub-scene .sco files and calibrating Redlist relics...")
    # First, read and parse all files into memory
    sco_data = {}
    for sub in SUB_TYPES:
        for t in [3, 5]:
            fname = f"scn_town_{t}_{sub}.sco"
            p = os.path.join(SCENE_DIR, fname)
            ver, recs, tail = parse_sco(p)
            sco_data[(t, sub)] = (ver, recs, tail)

    # For each sub-type, swap:
    # new town_3 gets old town_5 recs
    # new town_5 gets old town_3 recs
    new_sco = {}
    for sub in SUB_TYPES:
        new_sco[(3, sub)] = (sco_data[(5, sub)][0], [dict(r) for r in sco_data[(5, sub)][1]], sco_data[(5, sub)][2])
        new_sco[(5, sub)] = (sco_data[(3, sub)][0], [dict(r) for r in sco_data[(3, sub)][1]], sco_data[(3, sub)][2])

    # Now, calibrate Redlist relics on the newly swapped files:

    # --------------------------------------------------------------------------
    # A. scn_town_3_store (Sibiu Store):
    # Now has old town_5 store layout (interior_house_b).
    # Needs: spr_caskofamontillado on floor, spr_thirteen on wall!
    # Entry 0 is [-5.585, 1.532, -0.431], Entry 9 (Merchant) is [-0.046, 0.364, 0.076]
    # We place:
    # spr_caskofamontillado at [1.80, 2.20, 0.00]
    # spr_thirteen at [1.80, 2.38, 1.25]
    # --------------------------------------------------------------------------
    ver, recs, tail = new_sco[(3, "store")]
    # Strip any old relics if present
    recs = [r for r in recs if r["sname"] not in ("spr_caskofamontillado", "spr_thirteen")]

    # Add spr_caskofamontillado
    cask_rec = {
        "index": len(recs),
        "otype": 0,
        "sub_id": 0,
        "unused": 0,
        "rot_pos": [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            1.80, 2.20, 0.00
        ],
        "sname": "spr_caskofamontillado",
        "vraw": 0,
        "scale": [1.0, 1.0, 1.0],
        "raw": b""
    }
    recs.append(cask_rec)

    # Add spr_thirteen
    thirteen_rec = {
        "index": len(recs),
        "otype": 0,
        "sub_id": 0,
        "unused": 0,
        "rot_pos": [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            1.80, 2.38, 1.25
        ],
        "sname": "spr_thirteen",
        "vraw": 0,
        "scale": [1.0, 1.0, 1.0],
        "raw": b""
    }
    recs.append(thirteen_rec)
    new_sco[(3, "store")] = (ver, recs, tail)
    print("   [Calibrated] scn_town_3_store: Injected spr_caskofamontillado and spr_thirteen at [1.80, 2.20, 0.00]")

    # --------------------------------------------------------------------------
    # B. scn_town_5_store (Kolozsvar Store):
    # Now has old town_3 store layout. Strip any old spr_caskofamontillado or spr_thirteen!
    # --------------------------------------------------------------------------
    ver, recs, tail = new_sco[(5, "store")]
    recs = [r for r in recs if r["sname"] not in ("spr_caskofamontillado", "spr_thirteen")]
    new_sco[(5, "store")] = (ver, recs, tail)
    print("   [Calibrated] scn_town_5_store: Cleaned old relics.")

    # --------------------------------------------------------------------------
    # C. scn_town_5_center (Kolozsvar Center):
    # Now has old town_3 center layout (113KB, Wittal).
    # Needs: spr_container_small_chest (Bonus Chest #2, Samurai gear).
    # There is a box stack at [320.0, 168.0, 12.54].
    # We place spr_container_small_chest tucked neatly behind the wooden crates at [321.20, 167.50, 12.54]!
    # --------------------------------------------------------------------------
    ver, recs, tail = new_sco[(5, "center")]
    recs = [r for r in recs if r["sname"] not in ("spr_container_small_chest",)]

    chest_rec = {
        "index": len(recs),
        "otype": 0,
        "sub_id": 0,
        "unused": 0,
        "rot_pos": [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            321.20, 167.50, 12.54
        ],
        "sname": "spr_container_small_chest",
        "vraw": 0,
        "scale": [1.0, 1.0, 1.0],
        "raw": b""
    }
    recs.append(chest_rec)
    new_sco[(5, "center")] = (ver, recs, tail)
    print("   [Calibrated] scn_town_5_center: Injected spr_container_small_chest at [321.20, 167.50, 12.54]")

    # --------------------------------------------------------------------------
    # D. scn_town_3_center (Sibiu Center):
    # Now has old town_5 center layout (515KB, Videns).
    # Strip any old spr_container_small_chest so there is no ghost chest!
    # --------------------------------------------------------------------------
    ver, recs, tail = new_sco[(3, "center")]
    recs = [r for r in recs if r["sname"] not in ("spr_container_small_chest",)]
    new_sco[(3, "center")] = (ver, recs, tail)
    print("   [Calibrated] scn_town_3_center: Cleaned old spr_container_small_chest.")

    # --------------------------------------------------------------------------
    # E. Castle player chests:
    # Ensure both castle scenes have spr_player_chest!
    # --------------------------------------------------------------------------
    for t in [3, 5]:
        ver, recs, tail = new_sco[(t, "castle")]
        has_chest = any(r["sname"] == "spr_player_chest" for r in recs)
        if not has_chest:
            # Anchor near entry 0
            e0 = [r for r in recs if r["otype"] == 1 and r["vraw"] == 0]
            if e0:
                pos = e0[0]["rot_pos"][9:12]
                chest = {
                    "index": len(recs),
                    "otype": 0,
                    "sub_id": 0,
                    "unused": 0,
                    "rot_pos": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, pos[0] + 1.2, pos[1] + 1.2, pos[2]],
                    "sname": "spr_player_chest",
                    "vraw": 0,
                    "scale": [1.0, 1.0, 1.0],
                    "raw": b""
                }
                recs.append(chest)
                new_sco[(t, "castle")] = (ver, recs, tail)
                print(f"   [Calibrated] scn_town_{t}_castle: Injected spr_player_chest")

    # Write all 16 .sco files back to SceneObj
    for sub in SUB_TYPES:
        for t in [3, 5]:
            fname = f"scn_town_{t}_{sub}.sco"
            p = os.path.join(SCENE_DIR, fname)
            ver, recs, tail = new_sco[(t, sub)]
            write_sco(p, ver, recs, tail)

    print("   Wrote all 16 sub-scene .sco files successfully!")


def main():
    print("========================================================================")
    print(" Carpathian Solid & Shade (1521) — 锡比乌与克劳森堡城市场景全套互换")
    print("========================================================================")
    backup_files()
    swap_scenes_txt()
    swap_and_calibrate_scos()
    print("========================================================================")
    print(" 互换与红线机关无损迁移完成！")
    print("========================================================================")


if __name__ == "__main__":
    main()
