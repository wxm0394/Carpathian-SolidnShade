import os, sys, struct

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
SCENE_DIR = os.path.join(MOD_DIR, "SceneObj")

sys.path.append(os.path.join(MOD_DIR, "tools"))
from sco_anchor_transplanter import parse_sco, write_sco

def add_entry_point(recs, entry_no, pos, rot_y_deg=0):
    rot_pos = [
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0,
        pos[0], pos[1], pos[2]
    ]
    new_rec = {
        "index": len(recs),
        "otype": 1, # Entry Point
        "sub_id": 0,
        "unused": 0,
        "rot_pos": rot_pos,
        "sname": "entry_point",
        "vraw": entry_no, # Entry Point number
        "scale": [1.0, 1.0, 1.0],
        "raw": b""
    }
    recs.append(new_rec)

# 1. Calibrate Town 11 (Suceava) - Missing Entry 3 (Tavern Exit)
sco_11 = os.path.join(SCENE_DIR, "scn_town_11_center.sco")
if os.path.exists(sco_11):
    ver, recs, tail = parse_sco(sco_11)
    if not any(r['otype'] == 1 and r['vraw'] == 3 for r in recs):
        # Anchor near entry 0
        e0 = [r for r in recs if r['otype'] == 1 and r['vraw'] == 0][0]
        pos = e0['rot_pos'][9:12]
        add_entry_point(recs, 3, [pos[0] + 8.0, pos[1] + 5.0, pos[2]])
        write_sco(sco_11, ver, recs, tail)
        print("Calibrated Town 11: Added Entry 3 (Tavern exit)")

# 2. Calibrate Town 12 (Iasi) - Missing Entry 3 (Tavern Exit)
sco_12 = os.path.join(SCENE_DIR, "scn_town_12_center.sco")
if os.path.exists(sco_12):
    ver, recs, tail = parse_sco(sco_12)
    if not any(r['otype'] == 1 and r['vraw'] == 3 for r in recs):
        e0 = [r for r in recs if r['otype'] == 1 and r['vraw'] == 0][0]
        pos = e0['rot_pos'][9:12]
        add_entry_point(recs, 3, [pos[0] + 6.0, pos[1] - 4.0, pos[2]])
        write_sco(sco_12, ver, recs, tail)
        print("Calibrated Town 12: Added Entry 3 (Tavern exit)")

# 3. Calibrate Town 18 (Thessaloniki / Sayazn town 4)
sco_18 = os.path.join(SCENE_DIR, "scn_town_18_center.sco")
if os.path.exists(sco_18):
    ver, recs, tail = parse_sco(sco_18)
    e0 = [r for r in recs if r['otype'] == 1 and r['vraw'] == 0][0]
    bx, by, bz = e0['rot_pos'][9:12]
    
    # Missing crucial doors / exits
    # Entry 2: Player enter town spawn
    if not any(r['otype'] == 1 and r['vraw'] == 2 for r in recs):
        add_entry_point(recs, 2, [bx - 5.0, by - 5.0, bz])
    # Entry 4: Castle exit
    if not any(r['otype'] == 1 and r['vraw'] == 4 for r in recs):
        add_entry_point(recs, 4, [bx + 15.0, by + 12.0, bz])
    # Entry 5: Prison exit
    if not any(r['otype'] == 1 and r['vraw'] == 5 for r in recs):
        add_entry_point(recs, 5, [bx + 18.0, by + 8.0, bz])
    # Entry 6: Arena exit
    if not any(r['otype'] == 1 and r['vraw'] == 6 for r in recs):
        add_entry_point(recs, 6, [bx - 12.0, by + 15.0, bz])
    # Entry 7: Store exit
    if not any(r['otype'] == 1 and r['vraw'] == 7 for r in recs):
        add_entry_point(recs, 7, [bx + 5.0, by - 12.0, bz])
        
    # Missing merchants: Entry 9 (Mayor), 12 (Armorer), 13 (Horse merchant)
    if not any(r['otype'] == 1 and r['vraw'] == 9 for r in recs):
        add_entry_point(recs, 9, [bx + 4.0, by + 6.0, bz])
    if not any(r['otype'] == 1 and r['vraw'] == 12 for r in recs):
        add_entry_point(recs, 12, [bx + 8.0, by - 8.0, bz])
    if not any(r['otype'] == 1 and r['vraw'] == 13 for r in recs):
        add_entry_point(recs, 13, [bx - 15.0, by - 15.0, bz])

    # 17 Town Walkers (23..39) for vibrant street life
    existing_walkers = set([r['vraw'] for r in recs if r['otype'] == 1 and 23 <= r['vraw'] <= 39])
    
    # Path coordinates along the main street / squares of town 18
    walker_offsets = [
        (-8, 4), (-12, 10), (-6, 18), (2, 22), (10, 16),
        (14, 8), (12, -2), (6, -8), (-2, -14), (-10, -8),
        (-16, 2), (-14, 14), (0, 12), (8, 4), (4, -4),
        (-4, -2), (2, 2)
    ]
    
    for i, w_idx in enumerate(range(23, 40)):
        if w_idx not in existing_walkers:
            dx, dy = walker_offsets[i]
            add_entry_point(recs, w_idx, [bx + dx, by + dy, bz])
            
    write_sco(sco_18, ver, recs, tail)
    print("Calibrated Town 18: Successfully injected Entries 2,4,5,6,7, 9,12,13 and full 17 walkers (23..39)!")

