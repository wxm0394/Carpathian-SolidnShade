#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorder female face skins in skins.txt according to regional cultures:
1. Carpathian & Hungarian/Balkan Plain Fair (12 faces)
2. Mediterranean & Adriatic Olive/Sun-kissed (7 faces)
3. Eastern Steppe & East Asian (4 faces: asia, 04, 08, 10a4)
4. Dacian & Carpathian Folk Warpaint/Battle-scarred (5 faces: youngb, bb, ab, 03, brownb)
5. Southern/Exotic Deep Tone (3 faces: 05, africanb, etc.)
Total = 31 faces, strictly 0 drift in count.
"""

import os

SKINS_TXT = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade/skins.txt"

def reorder():
    with open(SKINS_TXT, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    line_58 = lines[57].split()
    count = int(line_58[0])
    print(f"Original female skin entries count: {count}")
    
    idx = 1
    entries = {}
    while idx < len(line_58):
        name = line_58[idx]
        color = line_58[idx+1]
        num_hair_mats = int(line_58[idx+2])
        idx += 3
        hair_group = []
        for _ in range(num_hair_mats):
            num_colors = int(line_58[idx])
            hair_mat = line_58[idx+1]
            colors = line_58[idx+2 : idx+2+num_colors]
            idx += 2 + num_colors
            hair_group.append((hair_mat, colors))
        entries[name] = (color, hair_group)
        
    print(f"Successfully extracted {len(entries)} skin definitions.")
    
    # 5 Cultural Zones (strictly matching 31 items)
    cultural_order = [
        # Zone 1: Central/Balkan European Fair
        "womanface_01", "womanface_02", "womanface_06", "womanface_11",
        "womanface_12", "womanface_14", "womanface_16", "womanface_17",
        "womanface_18", "womanface_19", "womanface_20", "womanface_21",
        "womanface_22",
        
        # Zone 2: Adriatic & Mediterranean Olive
        "womanface_07", "womanface_09", "womanface_10", "womanface_13",
        "womanface_15", "womanface_10a", "womanface_10aa",
        
        # Zone 3: Eastern Steppe & East Asian
        "womanface_asia", "womanface_04", "womanface_08", "womanface_10a4",
        
        # Zone 4: Dacian & Folk Warrior Warpaint
        "womanface_youngb", "womanface_bb", "womanface_ab", "womanface_03",
        
        # Zone 5: Near East & Deep Tone
        "womanface_brownb", "womanface_05", "womanface_africanb"
    ]
    
    assert len(cultural_order) == count, f"Count mismatch: {len(cultural_order)} vs {count}"
    assert set(cultural_order) == set(entries.keys()), f"Set mismatch: {set(cultural_order) ^ set(entries.keys())}"
    
    # Reconstruct line
    out_parts = [str(count)]
    for name in cultural_order:
        color, hair_group = entries[name]
        out_parts.extend([name, color, str(len(hair_group))])
        for hair_mat, colors in hair_group:
            out_parts.extend([str(len(colors)), hair_mat])
            out_parts.extend(colors)
            
    lines[57] = " " + "  ".join(out_parts) + " \n"
    
    with open(SKINS_TXT, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print("[+] Successfully reordered 31 female skins by cultural zones in skins.txt!")

if __name__ == "__main__":
    reorder()
