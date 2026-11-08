import os

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"

with open(os.path.join(MOD_DIR, "item_kinds1.txt"), "r", encoding="latin1") as f:
    lines = [l.strip() for l in f if l.strip()]

# In scripts.txt, category 12 is: types = [13] (body armor)
# Loop runs from item 1 to item_scan_limit (which was 902 in the old script, or 5004 now)
# Let's see what was matched when limit was 902 vs all!

matches_old = []
matches_all = []

item_idx = 0
for l in lines[2:]:
    if l.startswith("itm_"):
        item_idx += 1
        parts = l.split()
        itm_id = parts[0]
        raw_name = parts[1]
        try:
            num_m = int(parts[3])
            meshes = [parts[4 + m*2] for m in range(num_m)]
            flag_idx = 4 + num_m * 2
            flags = int(parts[flag_idx])
            itype = flags & 0xFF
            if itype == 13:
                if item_idx < 902:
                    matches_old.append((item_idx, itm_id, raw_name, meshes))
                matches_all.append((item_idx, itm_id, raw_name, meshes))
        except Exception:
            pass

print(f"Old script matches (<902): {len(matches_old)}")
print(f"All matches: {len(matches_all)}")

# Let's inspect the first 56 of matches_all
print("\nFirst 56 of matches_all (Page 1):")
for i, (idx, iid, name, meshes) in enumerate(matches_all[:56]):
    r = i // 8 + 1
    c = i % 8 + 1
    print(f"[{r},{c}] #{i+1:2d} (item #{idx:4d}): {iid:35s} {name:30s} meshes={meshes}")

