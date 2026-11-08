import os, struct

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
RES_DIR = os.path.join(MOD_DIR, "Resource")
COMMON_RES = "/home/wxm/GOG Games/Mount Blade Warband/game/CommonRes"

target_meshes = [
    'arena_tunicY_new', 'nomad_armor_new', 'blue_dress_new',
    'woolen_dress', 'shirt_a', 'rich_tunic_a'
]

# Scan all brfs in mod and commonres to find which BRF defines each target mesh,
# and what material it references!

def find_mesh_in_brf(brf_path, mesh_name):
    with open(brf_path, "rb") as f:
        data = f.read()
    target = mesh_name.encode('latin1') + b'\x00'
    pos = 0
    found = []
    while True:
        idx = data.find(target, pos)
        if idx == -1:
            break
        # inspect nearby bytes for material string
        # In OpenBRF mesh struct:
        # string name, string material
        # usually material name follows closely after mesh name!
        sub = data[idx:idx+200]
        tokens = [t.decode('latin1', errors='ignore') for t in sub.split(b'\x00') if len(t) > 0]
        found.append(tokens)
        pos = idx + len(target)
    return found

print("Searching for target meshes...")
for m in target_meshes:
    print(f"\nTarget mesh: {m}")
    found = False
    for d in [RES_DIR, COMMON_RES]:
        for f in os.listdir(d):
            if f.endswith(".brf"):
                p = os.path.join(d, f)
                res = find_mesh_in_brf(p, m)
                if res:
                    for r in res[:2]:
                        print(f"  Found in {f}: tokens={r[:4]}")
                    found = True

