import os, struct

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
RES_DIR = os.path.join(MOD_DIR, "Resource")
TEX_DIR = os.path.join(MOD_DIR, "Textures")

# Let's read openBRF structure or scan strings
# In BRF, materials define:
# [mat_name] [shader_name] [diffuseA_tex] [diffuseB_tex] [bump_tex] [specular_tex]

def scan_materials_in_brf(brf_path):
    mats = {}
    with open(brf_path, "rb") as f:
        data = f.read()
    
    # BRF header: 4 bytes length, string "rfver ", 4 bytes ver
    # Then chunks: 'texture', 'material', 'mesh', etc.
    # Let's scan for chunk type "matr" or "material"
    # Actually in BRF format:
    # 4-byte chunk type string: 'tex_', 'mat_', 'mesh', 'anim', 'skel', 'body'
    pos = 0
    while pos < len(data) - 8:
        tag = data[pos:pos+4]
        if tag in (b'mat_', b'matr'):
            # Found material chunk!
            pass
        pos += 1
    return mats

print("Scanning all Textures in mod...")
mod_textures = set([f.lower() for f in os.listdir(TEX_DIR) if f.endswith(".dds")])
print(f"Total textures in Textures/: {len(mod_textures)}")

# Check Vasnar textures directory
VN_TEX = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/World of Vasnar/Textures"
vn_textures = set([f.lower() for f in os.listdir(VN_TEX) if f.endswith(".dds")])
print(f"Total textures in Vasnar Textures/: {len(vn_textures)}")

# Are there textures in Vasnar that are NOT in mod Textures/?
missing_in_mod = vn_textures - mod_textures
print(f"Textures in Vasnar Textures/ missing in mod Textures/: {len(missing_in_mod)}")
if missing_in_mod:
    print("Sample missing textures from Vasnar:")
    for t in sorted(list(missing_in_mod))[:20]:
        print(f"  {t}")

# Also check Sayazn
SZ_TEX = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Sayazn（美化脸）/Textures"
sz_textures = set([f.lower() for f in os.listdir(SZ_TEX) if f.endswith(".dds")])
missing_sz_in_mod = sz_textures - mod_textures
print(f"Textures in Sayazn Textures/ missing in mod Textures/: {len(missing_sz_in_mod)}")
if missing_sz_in_mod:
    print("Sample missing textures from Sayazn:")
    for t in sorted(list(missing_sz_in_mod))[:20]:
        print(f"  {t}")

