import os, sys, struct

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
SCENE_DIR = os.path.join(MOD_DIR, "SceneObj")

sys.path.append(os.path.join(MOD_DIR, "tools"))
from sco_anchor_transplanter import parse_sco, write_sco

RELIC_INJECTIONS = [
    ("scn_town_2_center", "spr_container_small_chest"),
    ("scn_town_3_store", "spr_caskofamontillado"),
    ("scn_town_5_center", "spr_container_small_chest"),
    ("scn_town_8_center", "spr_container_chest_b"),
]

for scn_name, prop_name in RELIC_INJECTIONS:
    sco_path = os.path.join(SCENE_DIR, f"{scn_name}.sco")
    if os.path.exists(sco_path):
        ver, recs, tail = parse_sco(sco_path)
        has_prop = any(r['sname'] == prop_name for r in recs)
        if not has_prop:
            anchors = [r for r in recs if r['otype'] == 1 and r['vraw'] in (0, 2)]
            if not anchors:
                anchors = [r for r in recs if r['otype'] == 1]
            if anchors:
                a_pos = anchors[0]['rot_pos'][9:12]
                new_pos = [a_pos[0] + 1.5, a_pos[1] + 1.5, a_pos[2]]
                rot_pos = [
                    1.0, 0.0, 0.0,
                    0.0, 1.0, 0.0,
                    0.0, 0.0, 1.0,
                    new_pos[0], new_pos[1], new_pos[2]
                ]
                new_rec = {
                    "index": len(recs),
                    "otype": 0,
                    "sub_id": 0,
                    "unused": 0,
                    "rot_pos": rot_pos,
                    "sname": prop_name,
                    "vraw": 0,
                    "scale": [1.0, 1.0, 1.0],
                    "raw": b""
                }
                recs.append(new_rec)
                write_sco(sco_path, ver, recs, tail)
                print(f"Injected S&S relic {prop_name} into {scn_name}.sco at {new_pos}")
            else:
                print(f"Warning: No anchor found in {scn_name}.sco")
        else:
            print(f"Relic {prop_name} already present in {scn_name}.sco")

