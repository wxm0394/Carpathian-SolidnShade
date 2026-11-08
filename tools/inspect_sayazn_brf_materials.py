import os

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
RES_DIR = os.path.join(MOD_DIR, "Resource")

sayazn_brfs = [f for f in os.listdir(RES_DIR) if f.startswith("sz_") and f.endswith(".brf")]

print(f"Total sz_ BRFs: {len(sayazn_brfs)}")

# Let's check which materials are defined across all BRF files in Resource/
# And which materials are used by meshes in sz_sayazn_*.brf!

# We can scan BRF files for material names:
# In BRF format, material references in mesh:
# We can search for material names defined in sz_sayazn_materials.brf, sz_sayazn_uniforms_materials.brf, etc.

