import os

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
RES_DIR = os.path.join(MOD_DIR, "Resource")
TEX_DIR = os.path.join(MOD_DIR, "Textures")

# Let's inspect all BRF files from Vasnar
vn_brfs = [f for f in os.listdir(RES_DIR) if f.startswith("vn_") and f.endswith(".brf")]

print(f"Found {len(vn_brfs)} vn_ BRF files.")

# Also inspect materials in vn_Innistrad_Materials.brf, materials.brf, env_materials.brf
# We want to check:
# 1. Which materials exist in Resource/*.brf
# 2. For each material, what is its diffuse texture
# 3. Does that diffuse texture exist in Textures/*.dds?
# 4. What is its shader?

