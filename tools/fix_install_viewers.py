import os, sys, re

MODULE_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
INSTALL_VIEWERS_SCRIPT = os.path.join(MODULE_DIR, "tools/install_viewers.py")

with open(INSTALL_VIEWERS_SCRIPT, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Fix ITEM_CATEGORIES loop limit from 902 to dynamic total items in item_kinds1.txt
# Read actual item count
item_kinds_path = os.path.join(MODULE_DIR, "item_kinds1.txt")
with open(item_kinds_path, "r", encoding="latin1") as f:
    lines = [l.strip() for l in f if l.strip()]
actual_total_items = int(lines[1])
print(f"Detected {actual_total_items} items in item_kinds1.txt")

# Replace loop limit 902 with actual_total_items + 1
# Also fix opcode 2147483678 with 1073741855 (this_or_next|eq with 2 args)
old_pop = """    # 8. all_items_populate_category (Strict Warband standard item types)
    pop_items_lines = [
        f"21 1 {local_var(0)}", # store_script_param_1, :category
        f"6 3 {local_var(6)} 0 910 500 3 {id_trp_temp_c} {local_var(6)} 0 3 0", # clear stale slots
        f"2133 2 {local_var(1)} 0", # assign, :num_matches, 0
        f"6 3 {local_var(2)} 1 902", # try_for_range, :item, 1, 902
        f"1570 2 {local_var(3)} {local_var(2)}", # item_get_type, :type, :item
        f"2133 2 {local_var(4)} 0", # assign, :match, 0
        f"4 0 31 2 {local_var(0)} 0 2133 2 {local_var(4)} 1", # cat 0: all
    ]
    for cat_idx, (q_id, types) in enumerate(ITEM_CATEGORIES[1:], 1):
        conds = " ".join([f"31 2 {local_var(3)} {t}" for t in types])
        if len(types) > 1:
            pop_items_lines.append(f"5 0 31 2 {local_var(0)} {cat_idx} 4 0 {' '.join([f'2147483678 2 {local_var(3)} {t}' if i < len(types)-1 else f'31 2 {local_var(3)} {t}' for i, t in enumerate(types)])} 2133 2 {local_var(4)} 1 3 0")
        else:
            pop_items_lines.append(f"5 0 31 2 {local_var(0)} {cat_idx} {conds} 2133 2 {local_var(4)} 1")"""

new_pop = f"""    # 8. all_items_populate_category (Strict Warband standard item types, full {actual_total_items} items)
    item_scan_limit = {actual_total_items + 1}
    pop_items_lines = [
        f"21 1 {{local_var(0)}}", # store_script_param_1, :category
        f"6 3 {{local_var(6)}} 0 {{item_scan_limit + 10}} 500 3 {{id_trp_temp_c}} {{local_var(6)}} 0 3 0", # clear stale slots
        f"2133 2 {{local_var(1)}} 0", # assign, :num_matches, 0
        f"6 3 {{local_var(2)}} 1 {{item_scan_limit}}", # try_for_range, :item, 1, item_scan_limit
        f"1570 2 {{local_var(3)}} {{local_var(2)}}", # item_get_type, :type, :item
        f"2133 2 {{local_var(4)}} 0", # assign, :match, 0
        f"4 0 31 2 {{local_var(0)}} 0 2133 2 {{local_var(4)}} 1", # cat 0: all
    ]
    for cat_idx, (q_id, types) in enumerate(ITEM_CATEGORIES[1:], 1):
        if len(types) > 1:
            # this_or_next | eq is 1073741855, with exactly 2 arguments!
            cond_ops = []
            for i, t in enumerate(types):
                if i < len(types) - 1:
                    cond_ops.append(f"1073741855 2 {{local_var(3)}} {{t}}")
                else:
                    cond_ops.append(f"31 2 {{local_var(3)}} {{t}}")
            pop_items_lines.append(f"5 0 31 2 {{local_var(0)}} {{cat_idx}} 4 0 {' '.join(cond_ops)} 2133 2 {{local_var(4)}} 1 3 0")
        else:
            pop_items_lines.append(f"5 0 31 2 {{local_var(0)}} {{cat_idx}} 31 2 {{local_var(3)}} {{types[0]}} 2133 2 {{local_var(4)}} 1")"""

assert old_pop in code, "Could not find old_pop in install_viewers.py!"
code = code.replace(old_pop, new_pop)

# 2. Fix p3_t1 and p3_t2 grid slot matching opcode:
# In p3_t1:
# f"4 0 1073741855 3 {id_trp_temp_a} {local_var(2)} {local_var(0)} 540 3 {id_trp_temp_a} {local_var(4)} {local_var(0)} "
# Replace 1073741855 (which is this_or_next|eq) with 1073742364 (this_or_next|troop_slot_eq = 1073741824 + 540)
code = code.replace(
    f"4 0 1073741855 3 {{id_trp_temp_a}} {{local_var(2)}} {{local_var(0)}} 540 3 {{id_trp_temp_a}} {{local_var(4)}} {{local_var(0)}} ",
    f"4 0 1073742364 3 {{id_trp_temp_a}} {{local_var(2)}} {{local_var(0)}} 540 3 {{id_trp_temp_a}} {{local_var(4)}} {{local_var(0)}} "
)

with open(INSTALL_VIEWERS_SCRIPT, "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully patched install_viewers.py!")
