#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade - Phase 2 Comprehensive Map Sculpting & Scaling Engine
1. Scale continental geometry & party coordinates by factor 0.75.
2. Extend infinite ocean buffer (Terrain 0) around boundaries to completely banish edge skybox.
3. Lock camera boundaries in module.ini with 120+ unit buffer.
4. Reduce party map speed multiplier to 65% in scripts.txt (increasing journey time by ~15.4%).
5. Sculpt 6 historical geographical terrains with realistic elevation & materials.
"""

import os
import math
import collections

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
MAP_TXT = os.path.join(MOD_DIR, "map.txt")
PARTIES_TXT = os.path.join(MOD_DIR, "parties.txt")
MODULE_INI = os.path.join(MOD_DIR, "module.ini")
SCRIPTS_TXT = os.path.join(MOD_DIR, "scripts.txt")

SCALE = 0.75

def scale_parties():
    print(f"[*] Scaling parties.txt coordinates by {SCALE}...")
    with open(PARTIES_TXT, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    out_lines = []
    party_count = 0
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 15 and parts[0] == '1':
            try:
                coord_idx = -1
                for i in range(5, len(parts) - 6):
                    try:
                        f0 = float(parts[i])
                        f1 = float(parts[i+1])
                        f2 = float(parts[i+2])
                        f3 = float(parts[i+3])
                        f4 = float(parts[i+4])
                        f5 = float(parts[i+5])
                        f6 = float(parts[i+6])
                        if abs(f0 - f2) < 1e-4 and abs(f1 - f3) < 1e-4 and abs(f2 - f4) < 1e-4 and abs(f3 - f5) < 1e-4:
                            coord_idx = i
                            break
                    except ValueError:
                        continue
                
                if coord_idx != -1:
                    for k in range(6):
                        val = float(parts[coord_idx + k])
                        parts[coord_idx + k] = f"{val * SCALE:.6f}"
                    out_lines.append(" " + " ".join(parts) + " \n")
                    party_count += 1
                    continue
            except Exception as e:
                pass
        out_lines.append(line)
        
    with open(PARTIES_TXT, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)
    print(f"[+] Scaled {party_count} parties in parties.txt successfully.")

def update_speed():
    print("[*] Updating game_get_party_speed_multiplier in scripts.txt to 65%...")
    with open(SCRIPTS_TXT, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if line.strip() == "game_get_party_speed_multiplier -1":
            toks = lines[i+1].strip().split()
            if len(toks) >= 7 and toks[-2] == "1" and toks[-1] in ["100", "65"]:
                toks[-1] = "65"
                lines[i+1] = " " + " ".join(toks) + "\n"
                print(f"[+] Set game_get_party_speed_multiplier line to: {lines[i+1].strip()}")
                break
                
    with open(SCRIPTS_TXT, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def update_camera_bounds():
    print("[*] Updating camera boundaries in module.ini...")
    with open(MODULE_INI, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    new_bounds = {
        "map_min_x": " -265.000000",
        "map_max_x": "  265.000000",
        "map_min_y": " -375.000000",
        "map_max_y": "  265.000000"
    }
    
    for i, line in enumerate(lines):
        for k, v in new_bounds.items():
            if line.strip().startswith(k):
                lines[i] = f"{k:<11}= {v}\n"
                print(f"[+] Updated {lines[i].strip()}")
                
    with open(MODULE_INI, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def sculpt_and_close_map():
    print(f"[*] Reading and sculpting map.txt (scale={SCALE})...")
    with open(MAP_TXT, 'r', encoding='utf-8', errors='ignore') as fp:
        num_verts = int(fp.readline().strip())
        verts = []
        for _ in range(num_verts):
            parts = fp.readline().split()
            verts.append([float(parts[0]) * SCALE, float(parts[1]) * SCALE, float(parts[2])])
            
        num_faces = int(fp.readline().strip())
        faces = []
        for _ in range(num_faces):
            parts = fp.readline().split()
            faces.append([int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])])
            
    print(f"[*] Original: {num_verts} vertices, {num_faces} faces.")
    
    # 1. 6 Historical Terrain Sculpting Rules
    print("[*] Sculpting 6 historical geographical zones...")
    
    for face in faces:
        t_type = face[0]
        v0, v1, v2 = verts[face[3]], verts[face[4]], verts[face[5]]
        cx = (v0[0] + v1[0] + v2[0]) / 3.0
        cy = (v0[1] + v1[1] + v2[1]) / 3.0
        cz = (v0[2] + v1[2] + v2[2]) / 3.0
        
        # Keep rivers and deep ocean undisturbed
        if t_type in [0, 8]:
            continue
            
        # Zone 1: Hungarian Plain & Middle Danube (-240 <= X <= -60, 70 <= Y <= 240)
        if -240 <= cx <= -60 and 70 <= cy <= 240:
            if t_type in [4, 5]:
                face[0] = 1 # Plain
            elif t_type in [2, 11] and cz < 3.0:
                face[0] = 1 # Fertile plain meadow
            for vid in [face[3], face[4], face[5]]:
                verts[vid][2] = max(0.8, min(3.5, verts[vid][2] * 0.75 + 0.5))
                
        # Zone 2: Transylvania & Carpathian Mountains (-60 <= X <= 135, 90 <= Y <= 255)
        elif -60 <= cx <= 135 and 90 <= cy <= 255:
            if t_type in [4, 5, 9, 11] or cz > 5.0:
                peak_factor = min(1.35, 1.0 + (cz / 15.0) * 0.4)
                new_z = cz * peak_factor
                for vid in [face[3], face[4], face[5]]:
                    verts[vid][2] = max(7.5, min(16.5, verts[vid][2] * peak_factor))
                if new_z > 12.0:
                    face[0] = 5 # Snow-capped peaks
                elif new_z > 8.5:
                    face[0] = 4 # Mountain rock
                else:
                    face[0] = 9 # Alpine coniferous forest
            elif 3.0 <= cz <= 5.5 and -20 <= cx <= 80:
                face[0] = 1 # Basin plains
                for vid in [face[3], face[4], face[5]]:
                    verts[vid][2] = max(2.5, min(5.0, verts[vid][2]))
                    
        # Zone 3: Wallachia & Lower Danube North Bank (30 <= X <= 185, 15 <= Y <= 105)
        elif 30 <= cx <= 185 and 15 <= cy <= 105:
            if cz < 2.0 and t_type != 8:
                face[0] = 10 # Lowland wetland swamp
            elif t_type in [4, 5]:
                face[0] = 3 # Mixed lowland forest
            else:
                face[0] = 1 # Alluvial plain
            for vid in [face[3], face[4], face[5]]:
                verts[vid][2] = max(0.6, min(2.8, verts[vid][2] * 0.7))
                
        # Zone 4: Moldavia & Northern Black Sea (135 <= X <= 280, 75 <= Y <= 260)
        elif 135 <= cx <= 280 and 75 <= cy <= 260:
            if cx > 210:
                face[0] = 2 # Dry steppe
            elif cz > 3.0:
                face[0] = 11 # Moldavian rolling hills
            for vid in [face[3], face[4], face[5]]:
                verts[vid][2] = max(1.5, min(5.5, verts[vid][2]))
                
        # Zone 5: Balkan Interior (Bosnia/Serbia/Bulgaria) (-140 <= X <= 60, -120 <= Y <= 50)
        elif -140 <= cx <= 60 and -120 <= cy <= 50:
            if cz > 5.0 or t_type in [4, 11]:
                face[0] = 4 if cz > 8.0 else 11
                for vid in [face[3], face[4], face[5]]:
                    verts[vid][2] = max(5.0, min(13.5, verts[vid][2] * 1.15))
            else:
                face[0] = 3 # Gorge woodlands
                
        # Zone 6: Croatia/Dalmatia & Adriatic Coastal Waters (-280 <= X <= -135, -120 <= Y <= 140)
        elif -280 <= cx <= -135 and -120 <= cy <= 140:
            if cx < -210 and cy < 50:
                face[0] = 0 # Adriatic bay
                for vid in [face[3], face[4], face[5]]:
                    verts[vid][2] = 0.0
            elif cz > 6.0:
                face[0] = 4 # Dinaric coastal cliffs
                for vid in [face[3], face[4], face[5]]:
                    verts[vid][2] = max(5.5, min(14.0, verts[vid][2] * 1.1))
            else:
                face[0] = 11 # Mediterranean scrub & rocky coast
                
    # 2. Extract Boundary Edges & Stitch Outer Ocean Grid
    print("[*] Extracting boundary edge loops to seal world edge...")
    edge_faces = collections.defaultdict(list)
    for f_idx, fc in enumerate(faces):
        v = [fc[3], fc[4], fc[5]]
        for i in range(3):
            e = tuple(sorted((v[i], v[(i+1)%3])))
            edge_faces[e].append((f_idx, v[i], v[(i+1)%3]))
            
    boundary_edges = []
    for e, flist in edge_faces.items():
        if len(flist) == 1:
            boundary_edges.append(flist[0])
            
    print(f"[*] Found {len(boundary_edges)} unclosed boundary edges on continental frontier.")
    
    # Outer world ocean rectangle anchors: X in [-420, 420], Y in [-560, 480], Z = 0.0
    outer_anchors = []
    
    # 1. South edge (Y = -560, X from -420 to 420)
    for x in range(-420, 421, 40):
        outer_anchors.append([float(x), -560.0, 0.0])
    # 2. East edge (X = 420, Y from -540 to 460)
    for y in range(-540, 461, 40):
        outer_anchors.append([420.0, float(y), 0.0])
    # 3. North edge (Y = 460, X from 400 down to -420)
    for x in range(400, -421, -40):
        outer_anchors.append([float(x), 460.0, 0.0])
    # 4. West edge (X = -420, Y from 440 down to -540)
    for y in range(440, -541, -40):
        outer_anchors.append([-420.0, float(y), 0.0])
        
    start_anchor_idx = len(verts)
    verts.extend(outer_anchors)
    print(f"[*] Appended {len(outer_anchors)} infinite ocean perimeter anchor vertices.")
    
    def find_nearest_anchor(vx, vy):
        best_d2 = 1e18
        best_idx = 0
        for idx, anc in enumerate(outer_anchors):
            d2 = (anc[0] - vx)**2 + (anc[1] - vy)**2
            if d2 < best_d2:
                best_d2 = d2
                best_idx = idx
        return start_anchor_idx + best_idx
        
    ocean_face_count = 0
    for f_idx, v_a, v_b in boundary_edges:
        va_pt = verts[v_a]
        vb_pt = verts[v_b]
        
        # Drop boundary vertex Z to sea level
        verts[v_a][2] = max(0.0, min(1.2, verts[v_a][2]))
        verts[v_b][2] = max(0.0, min(1.2, verts[v_b][2]))
        
        anc_a = find_nearest_anchor(va_pt[0], va_pt[1])
        anc_b = find_nearest_anchor(vb_pt[0], vb_pt[1])
        
        if anc_a == anc_b:
            faces.append([0, 0, 3, v_a, v_b, anc_a])
            ocean_face_count += 1
        else:
            faces.append([0, 0, 3, v_a, v_b, anc_a])
            faces.append([0, 0, 3, v_b, anc_b, anc_a])
            ocean_face_count += 2
            
    print(f"[+] Stitched {ocean_face_count} deep ocean triangles to seal continental frontier.")
    
    # 3. Write back map.txt
    print(f"[*] Writing updated map.txt ({len(verts)} vertices, {len(faces)} faces)...")
    with open(MAP_TXT, 'w', encoding='utf-8') as out_f:
        out_f.write(f"{len(verts)}\n")
        for v in verts:
            out_f.write(f" {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        out_f.write(f"{len(faces)}\n")
        for fc in faces:
            out_f.write(f"{fc[0]} {fc[1]}  {fc[2]}  {fc[3]}  {fc[4]}  {fc[5]}\n")
            
    print("[+] map.txt successfully sculpted, scaled, and sealed!")

def main():
    print("=== Carpathian Solid & Shade Phase 2 Map Overhaul Engine ===")
    scale_parties()
    update_speed()
    update_camera_bounds()
    sculpt_and_close_map()
    print("=== All Map Tasks Completed Successfully! ===")

if __name__ == "__main__":
    main()
