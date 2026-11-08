#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restores Solid & Shade's original (4e02128) face codes & mapped warpaint skin indices
for all 37 fixed story, myth, boss, occult, and tarot NPCs in troops.txt (using 6-bit
skin_idx mask ~(0x3F << 12)), while ensuring 0 random walkers, villagers, tavern NPCs,
Native companions, or 5 human kingdoms (fac_kingdom_1..5) ever roll warpaint skins.
"""

import os
import subprocess

MOD = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"

MAN_WP_MAP = {
    1: 20,   # manface_young_2b
    3: 21,   # manface_midageb
    5: 22,   # manface_youngb
    7: 23,   # manface_young_3b
    9: 24,   # manface_7b
    11: 25,  # manface_midage_2b
    13: 26,  # manface_ruggedb
    15: 27,  # manface_africanb
}

WOMAN_WP_MAP = {
    1: 26,   # womanface_youngb   (Crimson Red)
    3: 27,   # womanface_bb       (Obsidian Black)
    5: 28,   # womanface_ab       (Olive-Moss Green)
    7: 29,   # womanface_brownb   (Deep Teal on Golden-Bronze)
    9: 30,   # womanface_africanb (Chalk-Ivory White + Pearl Studs on Ebony)
}

# Complete verified set of 37 fixed Solid & Shade story / myth / boss / occult NPCs
STORY_WARPAINT_IDS = {
    # Male S&S Bosses, Nursery-Rhyme Horrors, Tarot, Special Companions, Underworld Gods (25)
    35:  "trp_moontooth",
    70:  "trp_shadowlordleader",
    75:  "trp_deadantihero",
    121: "trp_charon",
    122: "trp_jackfrost",
    123: "trp_jackfrost2",
    144: "trp_pothinus",
    145: "trp_theking",
    147: "trp_thebutcher",
    149: "trp_thecandlestickmaker",
    150: "trp_thepiper",
    154: "trp_thyself",
    168: "trp_dolomite",
    169: "trp_horsekiller",
    285: "trp_ramun_the_slave_trader",
    288: "trp_dranton",
    289: "trp_kradus",
    321: "trp_tarot_reader_1",
    354: "trp_npc32",
    356: "trp_npc34",
    467: "trp_knight_6_4",
    470: "trp_knight_6_7",
    473: "trp_knight_6_10",
    474: "trp_knight_6_11",
    475: "trp_knight_6_12",
    # Female S&S Three Fates, Underworld Goddesses, Bosses, Special Companions (12)
    146: "trp_thequeen",
    148: "trp_thebaker",
    164: "trp_mamad",
    171: "trp_enmity",
    290: "trp_buxworth",
    355: "trp_npc33",
    469: "trp_knight_6_6",
    476: "trp_knight_6_13",
    481: "trp_knight_6_18",   # Clotho, Spinner
    482: "trp_knight_6_19",   # Lachesis, Alotter
    483: "trp_knight_6_20",   # Atropos, Unturnable
    496: "trp_knight_6_1_wife",  # Persephone
}


def set_skin_6bit(w0, new_skin):
    return (w0 & ~(0x3F << 12)) | ((new_skin & 0x3F) << 12)


def get_woman_skins_list(skins_txt):
    lines = skins_txt.splitlines()
    for i, l in enumerate(lines):
        if l.strip().startswith("woman 1"):
            toks = lines[i + 9].split()
            idx = 1
            out = []
            while idx < len(toks):
                nm = toks[idx]
                nh = int(toks[idx + 2])
                idx += 3
                for _ in range(nh):
                    nc = int(toks[idx])
                    idx += 2 + nc
                out.append(nm)
            return out
    raise RuntimeError("woman 1 not found in skins.txt")


def main():
    head_skins = get_woman_skins_list(
        subprocess.check_output(["git", "-C", MOD, "show", "HEAD:skins.txt"]).decode("utf-8", "ignore")
    )
    cur_skins = get_woman_skins_list(open(os.path.join(MOD, "skins.txt"), encoding="utf-8").read())

    wp_to_clean_name = {
        "womanface_youngb":   "womanface_11",
        "womanface_bb":       "womanface_12",
        "womanface_ab":       "womanface_03",
        "womanface_brownb":   "womanface_04",
        "womanface_africanb": "womanface_05",
    }
    head_wom_to_cur_clean = {}
    for hi, nm in enumerate(head_skins):
        clean_nm = wp_to_clean_name.get(nm, nm)
        head_wom_to_cur_clean[hi] = cur_skins.index(clean_nm)

    orig_lines = [
        l.strip()
        for l in subprocess.check_output(["git", "-C", MOD, "show", "4e02128:troops.txt"])
        .decode("utf-8", "ignore")
        .splitlines()
        if l.strip()
    ]
    head_troop_lines = [
        l.strip()
        for l in subprocess.check_output(["git", "-C", MOD, "show", "HEAD:troops.txt"])
        .decode("utf-8", "ignore")
        .splitlines()
        if l.strip()
    ]

    troops_path = os.path.join(MOD, "troops.txt")
    raw_lines = open(troops_path, "r", encoding="utf-8").readlines()
    non_empty_indices = [i for i, l in enumerate(raw_lines) if l.strip()]

    cnt = int(raw_lines[non_empty_indices[1]].strip())
    assert cnt == int(orig_lines[1]) == int(head_troop_lines[1])

    restored_story = 0
    remapped_clean_female = 0

    for ti in range(cnt):
        base_ne = 2 + ti * 6
        t0_cur = raw_lines[non_empty_indices[base_ne]].split()
        tid = t0_cur[0]
        flags = int(t0_cur[4])
        race = flags & 0xF
        hero = bool(flags & 0x10)

        face_line_idx = non_empty_indices[base_ne + 5]
        fw_head = [int(x) for x in head_troop_lines[base_ne + 5].split()]

        if ti in STORY_WARPAINT_IDS:
            assert tid == STORY_WARPAINT_IDS[ti], f"ID mismatch at #{ti}: {tid} != {STORY_WARPAINT_IDS[ti]}"
            fw_4e = [int(x) for x in orig_lines[base_ne + 5].split()]
            s1_orig = (fw_4e[0] >> 12) & 0x3F
            s2_orig = (fw_4e[4] >> 12) & 0x3F

            wp_map = MAN_WP_MAP if race == 0 else WOMAN_WP_MAP
            new_s1 = wp_map[s1_orig]
            fw_new = list(fw_4e)
            fw_new[0] = set_skin_6bit(fw_4e[0], new_s1)

            if fw_4e[4:8] != [0, 0, 0, 0]:
                if not hero:
                    # Non-hero unique boss/troop (#70, #164, #168, #169, #171): lock BOTH f1 & f2 skin to warpaint
                    new_s2 = wp_map.get(s2_orig, new_s1)
                    fw_new[4] = set_skin_6bit(fw_4e[4], new_s2)
                else:
                    # Hero troop: f2 is unused by engine, keep clean skin index <= 6
                    fw_new[4] = set_skin_6bit(fw_4e[4], s2_orig if s2_orig % 2 == 0 else 0)

            raw_lines[face_line_idx] = "  " + " ".join(str(x) for x in fw_new[:4]) + " " + " ".join(str(x) for x in fw_new[4:8]) + " \n"
            restored_story += 1

        elif race == 1:
            # Non-story female troop: map HEAD skin indices cleanly into cur 0..25 warpaint-free table
            fw_new = list(fw_head)
            s1_h = (fw_head[0] >> 12) & 0x3F
            s2_h = (fw_head[4] >> 12) & 0x3F
            ns1 = head_wom_to_cur_clean.get(s1_h, min(s1_h, 25))
            ns2 = head_wom_to_cur_clean.get(s2_h, min(s2_h, 25)) if fw_head[4:8] != [0, 0, 0, 0] else 0
            if ns1 != s1_h or (fw_head[4:8] != [0, 0, 0, 0] and ns2 != s2_h):
                fw_new[0] = set_skin_6bit(fw_head[0], ns1)
                if fw_head[4:8] != [0, 0, 0, 0]:
                    fw_new[4] = set_skin_6bit(fw_head[4], ns2)
                raw_lines[face_line_idx] = "  " + " ".join(str(x) for x in fw_new[:4]) + " " + " ".join(str(x) for x in fw_new[4:8]) + " \n"
                remapped_clean_female += 1

        elif race == 0:
            # Non-story male troop: verify strictly < 20
            s1_h = (fw_head[0] >> 12) & 0x3F
            s2_h = (fw_head[4] >> 12) & 0x3F
            if s1_h >= 20 or s2_h >= 20:
                fw_new = list(fw_head)
                fw_new[0] = set_skin_6bit(fw_head[0], s1_h % 8)
                if fw_head[4:8] != [0, 0, 0, 0]:
                    fw_new[4] = set_skin_6bit(fw_head[4], s2_h % 8)
                raw_lines[face_line_idx] = "  " + " ".join(str(x) for x in fw_new[:4]) + " " + " ".join(str(x) for x in fw_new[4:8]) + " \n"

    with open(troops_path, "w", encoding="utf-8") as f:
        f.writelines(raw_lines)

    print(f"Restored {restored_story}/37 fixed S&S story warpaint NPCs; remapped {remapped_clean_female} clean female troops into 0..25.")


if __name__ == "__main__":
    main()
