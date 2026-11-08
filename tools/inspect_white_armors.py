import os, sys

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
with open(os.path.join(MOD_DIR, "item_kinds1.txt"), "r", encoding="latin1") as f:
    lines = [l.strip() for l in f if l.strip()]

body_armors = []
for l in lines[2:]:
    if l.startswith("itm_"):
        parts = l.split()
        itm_id = parts[0]
        raw_name = parts[1]
        try:
            num_meshes = int(parts[3])
            meshes = [parts[4 + m*2] for m in range(num_meshes)]
            flag_idx = 4 + num_meshes*2
            flags = int(parts[flag_idx])
            itype = flags & 0xFF
            if itype == 13: # itp_type_body_armor
                body_armors.append((itm_id, raw_name, meshes))
        except Exception:
            pass

print(f"Total body armors: {len(body_armors)}")
print("Page 1 body armors (first 56):")
for idx, (itm_id, name, meshes) in enumerate(body_armors[:56]):
    # 8 items per row in 8x7 grid
    row = idx // 8 + 1
    col = idx % 8 + 1
    print(f"[{row},{col}] ({idx+1:2d}): {itm_id:32s} {name:32s} meshes={meshes}")

