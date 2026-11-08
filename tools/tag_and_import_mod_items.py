import os, sys, shutil

BASE_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules"
MOD_DIR = os.path.join(BASE_DIR, "Carpathian Solid & Shade")
SS_ORIG_DIR = os.path.join(BASE_DIR, "SolidAndShadeWB")
VASNAR_DIR = os.path.join(BASE_DIR, "World of Vasnar")
SAYAZN_DIR = os.path.join(BASE_DIR, "Sayazn（美化脸）")

def parse_items_file(path):
    with open(path, "r", encoding="latin1") as f:
        content = f.read()
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    count = int(lines[1])
    items = []
    i = 2
    while i < len(lines):
        line = lines[i]
        if line.startswith("itm_"):
            block = [line]
            j = i + 1
            while j < len(lines) and not lines[j].startswith("itm_"):
                block.append(lines[j])
                j += 1
            items.append(block)
            i = j
        else:
            i += 1
    return count, items

# 1. Load original Solid & Shade item IDs (Whitelist - NEVER modify or tag these!)
_, ss_items = parse_items_file(os.path.join(SS_ORIG_DIR, "item_kinds1.txt"))
ss_orig_ids = set([block[0].split()[0] for block in ss_items])
print(f"Original Solid & Shade item count: {len(ss_orig_ids)}")

# 2. Load Vasnar items
_, vn_items = parse_items_file(os.path.join(VASNAR_DIR, "item_kinds1.txt"))
vn_map = {block[0].split()[0]: block for block in vn_items}

# 3. Load Sayazn items
_, sz_items = parse_items_file(os.path.join(SAYAZN_DIR, "item_kinds1.txt"))
sz_map = {block[0].split()[0]: block for block in sz_items}

# 4. Load Current mod items
mod_count, mod_items = parse_items_file(os.path.join(MOD_DIR, "item_kinds1.txt"))
cur_ids = set([block[0].split()[0] for block in mod_items])
print(f"Current mod item count: {len(mod_items)}")

# 5. Tag existing items in current mod if they originate from Vasnar or Sayazn
tagged_vn_count = 0
tagged_sz_count = 0

def add_tag_to_header_line(line, tag):
    parts = line.split()
    itm_id = parts[0]
    raw_name = parts[1]
    clean_tag = tag.replace(" ", "_")
    if clean_tag not in raw_name:
        parts[1] = f"{raw_name}_{clean_tag}"
    return " ".join(parts)

modified_mod_items = []
for block in mod_items:
    itm_id = block[0].split()[0]
    new_block = list(block)
    # Whitelist protection
    if itm_id in ss_orig_ids:
        modified_mod_items.append(new_block)
        continue

    if itm_id in sz_map or itm_id.startswith("itm_sz_") or "sayazn" in itm_id.lower():
        new_block[0] = add_tag_to_header_line(new_block[0], "[Sayazn]")
        tagged_sz_count += 1
    elif itm_id in vn_map or itm_id.startswith("itm_vn_") or "vasnar" in itm_id.lower() or "innistrad" in itm_id.lower():
        new_block[0] = add_tag_to_header_line(new_block[0], "[World_of_Vasnar]")
        tagged_vn_count += 1
    
    modified_mod_items.append(new_block)

print(f"Tagged {tagged_sz_count} existing Sayazn items and {tagged_vn_count} existing Vasnar items.")

# 6. Import missing items from Vasnar and Sayazn
added_vn_count = 0
added_sz_count = 0

for block in vn_items:
    itm_id = block[0].split()[0]
    if itm_id not in cur_ids and itm_id not in ss_orig_ids and not itm_id.startswith("itm_items_end"):
        new_block = list(block)
        new_block[0] = add_tag_to_header_line(new_block[0], "[World_of_Vasnar]")
        modified_mod_items.append(new_block)
        cur_ids.add(itm_id)
        added_vn_count += 1

for block in sz_items:
    itm_id = block[0].split()[0]
    if itm_id not in cur_ids and itm_id not in ss_orig_ids and not itm_id.startswith("itm_items_end"):
        new_block = list(block)
        new_block[0] = add_tag_to_header_line(new_block[0], "[Sayazn]")
        modified_mod_items.append(new_block)
        cur_ids.add(itm_id)
        added_sz_count += 1

print(f"Added {added_vn_count} new Vasnar items and {added_sz_count} new Sayazn items.")
print(f"Final total item count: {len(modified_mod_items)}")

# 7. Write updated item_kinds1.txt
out_path = os.path.join(MOD_DIR, "item_kinds1.txt")
with open(out_path, "w", encoding="latin1") as f:
    f.write("itemsfile version 3\n")
    f.write(f"{len(modified_mod_items)}\n")
    for block in modified_mod_items:
        for line in block:
            f.write(f" {line}\n")

print(f"Successfully wrote {out_path} with {len(modified_mod_items)} items!")

# 8. Update Chinese localization in languages/cns/item_kinds.csv
cns_csv_path = os.path.join(MOD_DIR, "languages/cns/item_kinds.csv")
if os.path.exists(cns_csv_path):
    with open(cns_csv_path, "r", encoding="utf-8", errors="ignore") as f:
        cns_lines = f.readlines()
    
    cns_dict = {}
    for l in cns_lines:
        if "|" in l:
            k, v = l.strip().split("|", 1)
            cns_dict[k] = v

    for block in modified_mod_items:
        itm_id = block[0].split()[0]
        if itm_id in ss_orig_ids:
            continue
        header = block[0]
        if "[World_of_Vasnar]" in header:
            curr_val = cns_dict.get(itm_id, block[0].split()[1].replace("_", " "))
            if "[World of Vasnar]" not in curr_val:
                cns_dict[itm_id] = f"{curr_val} [World of Vasnar]"
        elif "[Sayazn]" in header:
            curr_val = cns_dict.get(itm_id, block[0].split()[1].replace("_", " "))
            if "[Sayazn]" not in curr_val:
                cns_dict[itm_id] = f"{curr_val} [Sayazn]"

    with open(cns_csv_path, "w", encoding="utf-8") as f:
        for k, v in sorted(cns_dict.items()):
            f.write(f"{k}|{v}\n")
    print("Updated Chinese item_kinds.csv with origin tags!")

