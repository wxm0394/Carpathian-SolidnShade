#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade - Infinite Ocean Skirt & Horizon Skybox Seal
Completely seals the map edges with a vast, CCW-wound (upward normal) ocean mesh,
matching the proven architecture of Native Warband and 1866.
"""

import os
import collections

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
MAP_TXT = os.path.join(MOD_DIR, "map.txt")
BAK_TXT = os.path.join(MOD_DIR, "map.txt.bak_phase2")

def cross_product_z(p0, p1, p2):
    return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])

def build_ocean_skirt():
    print("[*] Reading clean map.txt from backup...")
    with open(BAK_TXT, 'r', encoding='utf-8', errors='ignore') as f:
        num_verts = int(f.readline().strip())
        verts = []
        for _ in range(num_verts):
            p = f.readline().split()
            verts.append([float(p[0]), float(p[1]), float(p[2])])
            
        num_faces = int(f.readline().strip())
        faces = []
        for _ in range(num_faces):
            p = f.readline().split()
            faces.append([int(p[0]), int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5])])

    print(f"[*] Base: {num_verts} vertices, {num_faces} faces.")
    
    # Prune previous dangling unclosed synthetic anchors outside continental limits
    clean_verts = []
    old_to_new = {}
    for idx, v in enumerate(verts):
        if abs(v[0]) > 410 or v[1] < -550 or v[1] > 450:
            continue
        old_to_new[idx] = len(clean_verts)
        clean_verts.append(v)
        
    clean_faces = []
    for fc in faces:
        if fc[3] in old_to_new and fc[4] in old_to_new and fc[5] in old_to_new:
            clean_faces.append([
                fc[0], fc[1], fc[2],
                old_to_new[fc[3]],
                old_to_new[fc[4]],
                old_to_new[fc[5]]
            ])
            
    print(f"[*] Pruned base to {len(clean_verts)} verts, {len(clean_faces)} faces.")
    
    # Find boundary edges
    edge_counts = collections.defaultdict(list)
    for f_idx, fc in enumerate(clean_faces):
        v = [fc[3], fc[4], fc[5]]
        for i in range(3):
            v0, v1 = v[i], v[(i+1)%3]
            ek = (min(v0, v1), max(v0, v1))
            edge_counts[ek].append((v0, v1))
            
    boundary_edges = []
    for ek, directed_list in edge_counts.items():
        if len(directed_list) == 1:
            boundary_edges.append(directed_list[0])
            
    print(f"[*] Found {len(boundary_edges)} boundary edges.")
    
    # Smooth boundary vertex elevation to sea level
    for v0, v1 in boundary_edges:
        clean_verts[v0][2] = max(0.0, min(0.8, clean_verts[v0][2] * 0.4))
        clean_verts[v1][2] = max(0.0, min(0.8, clean_verts[v1][2] * 0.4))
        
    # Outer polygon loop
    min_x, max_x = -650.0, 650.0
    min_y, max_y = -900.0, 650.0
    grid_res = 40.0
    
    xs = [min_x + i * grid_res for i in range(int((max_x - min_x) / grid_res) + 1)]
    ys = [min_y + j * grid_res for j in range(int((max_y - min_y) / grid_res) + 1)]
    
    outer_poly = []
    for x in xs:
        outer_poly.append((x, min_y))
    for y in ys[1:]:
        outer_poly.append((max_x, y))
    for x in reversed(xs[:-1]):
        outer_poly.append((x, max_y))
    for y in reversed(ys[1:-1]):
        outer_poly.append((min_x, y))
        
    outer_start_idx = len(clean_verts)
    for px, py in outer_poly:
        clean_verts.append([px, py, 0.0])
        
    poly_len = len(outer_poly)
    print(f"[*] Appended {poly_len} outer horizon boundary anchors.")
    
    def get_nearest_outer_idx(vx, vy):
        best_d2 = 1e18
        best_i = 0
        for i, (px, py) in enumerate(outer_poly):
            d2 = (px - vx)**2 + (py - vy)**2
            if d2 < best_d2:
                best_d2 = d2
                best_i = i
        return outer_start_idx + best_i

    # Stitch boundary edges to outer loop with STRICT INTEGER INDICES & CCW NORMAL
    ocean_face_count = 0
    for v0, v1 in boundary_edges:
        p0 = clean_verts[v0]
        p1 = clean_verts[v1]
        
        a0 = get_nearest_outer_idx(p0[0], p0[1])
        a1 = get_nearest_outer_idx(p1[0], p1[1])
        
        pa0 = clean_verts[a0]
        pa1 = clean_verts[a1]
        
        if a0 == a1:
            if cross_product_z(p0, p1, pa0) >= 0:
                clean_faces.append([0, 0, 3, int(v0), int(v1), int(a0)])
            else:
                clean_faces.append([0, 0, 3, int(v1), int(v0), int(a0)])
            ocean_face_count += 1
        else:
            # Quad: Triangle 1 (v0, v1, a0)
            if cross_product_z(p0, p1, pa0) >= 0:
                clean_faces.append([0, 0, 3, int(v0), int(v1), int(a0)])
            else:
                clean_faces.append([0, 0, 3, int(v1), int(v0), int(a0)])
                
            # Quad: Triangle 2 (v1, a1, a0) - NOTE: strict integer indices!
            if cross_product_z(p1, pa1, pa0) >= 0:
                clean_faces.append([0, 0, 3, int(v1), int(a1), int(a0)])
            else:
                clean_faces.append([0, 0, 3, int(a1), int(v1), int(a0)])
            ocean_face_count += 2

    # Verification: Ensure every single face element is an integer
    print("[*] Validating all face entries...")
    for f_idx, fc in enumerate(clean_faces):
        assert len(fc) == 6, f"Face {f_idx} has invalid length {len(fc)}"
        for elem_idx, val in enumerate(fc):
            assert isinstance(val, int), f"Face {f_idx} elem {elem_idx} is not int: {val}"
            
    print(f"[+] Total clean faces: {len(clean_faces)}, all integer validated.")
    
    # Write to map.txt
    with open(MAP_TXT, 'w', encoding='utf-8') as f:
        f.write(f"{len(clean_verts)}\n")
        for v in clean_verts:
            f.write(f" {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        f.write(f"{len(clean_faces)}\n")
        for fc in clean_faces:
            f.write(f"{fc[0]} {fc[1]}  {fc[2]}  {fc[3]}  {fc[4]}  {fc[5]}\n")
            
    print(f"[+] Successfully generated and validated map.txt: {len(clean_verts)} verts, {len(clean_faces)} faces.")

if __name__ == "__main__":
    build_ocean_skirt()
