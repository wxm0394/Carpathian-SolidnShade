import os, sys

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
SCENE_DIR = os.path.join(MOD_DIR, "SceneObj")

sys.path.append(os.path.join(MOD_DIR, "tools"))
from sco_anchor_transplanter import parse_sco

TOWNS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18]

print("=== 15 Towns Complete Suite Audit ===")
for tid in TOWNS:
    center_file = os.path.join(SCENE_DIR, f"scn_town_{tid}_center.sco")
    if not os.path.exists(center_file):
        print(f"Town {tid:2d}: scn_town_{tid}_center.sco MISSING!")
        continue
    
    ver, recs, _ = parse_sco(center_file)
    entries = set([r['vraw'] for r in recs if r['otype'] == 1])
    doors = [r for r in recs if 'door' in r['sname'].lower() or 'passage' in r['sname'].lower()]
    
    # Check crucial functional entries
    has_e2 = 2 in entries # enter town spawn
    has_e3 = 3 in entries # tavern exit
    has_e4 = 4 in entries # castle exit
    has_e5 = 5 in entries # prison exit
    has_e6 = 6 in entries # arena exit
    has_e7 = 7 in entries # store exit
    
    # Check merchants (9..13)
    merchants = [e for e in entries if 9 <= e <= 13]
    # Check walkers (23..39)
    walkers = [e for e in entries if 23 <= e <= 39]
    
    # Check subscene files
    subscenes = ["castle", "tavern", "prison", "arena", "store", "walls"]
    sub_status = []
    for sub in subscenes:
        sf = os.path.join(SCENE_DIR, f"scn_town_{tid}_{sub}.sco")
        if os.path.exists(sf):
            sub_status.append(f"{sub}:{os.path.getsize(sf)//1024}K")
        else:
            sub_status.append(f"{sub}:MISSING")
            
    print(f"Town {tid:2d} (Objects: {len(recs):4d}, Doors: {len(doors):2d}): "
          f"Doors=[Tavern:{'✓' if has_e3 else '✗'}, Castle:{'✓' if has_e4 else '✗'}, Prison:{'✓' if has_e5 else '✗'}, Arena:{'✓' if has_e6 else '✗'}, Store:{'✓' if has_e7 else '✗'}] "
          f"Merchants={len(merchants)}/5, Walkers={len(walkers)}/17")
    print(f"         Sub-scenes: {', '.join(sub_status)}")

