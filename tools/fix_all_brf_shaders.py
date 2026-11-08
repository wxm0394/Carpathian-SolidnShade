import os, struct

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
RES_DIR = os.path.join(MOD_DIR, "Resource")

SHADER_MAP = {
    # Skin bump nospec high shaders (Primary culprit of white armors)
    "standart_shader_skin_bump_nospec_high": "standart_shader_nobump_nospec",
    "standart_shader_skin_bump_nospec": "standart_shader_nobump_nospec",
    "standart_shader_bump_nospec_high_noterraincolor_Instanced": "standart_shader_nobump_nospec",
    "standart_shader_bump_nospec": "standart_shader_nobump_nospec",

    # Specular bump high shaders
    "specular_shader_skin_bump_high": "specular_shader",
    "specular_shader_noskin_bump_high": "specular_shader",
    "specular_shader_bump_Instanced": "specular_shader",
    "specular_shader_skin_bump": "specular_shader",
    "specular_shader_skin_bump_colorspec_high": "specular_shader",
    "specular_shader_skin_bump_high_aniso": "specular_shader",

    # Nospecular shaders
    "nospecular_shader_noskin_bump_high": "standart_shader_nobump_nospec",
    "nospecular_shader_skin_bump_high": "standart_shader_nobump_nospec",
    "nospecular_shader_skin_bump": "standart_shader_nobump_nospec",
    "nospecular_shader_skin_bump_high_aniso": "standart_shader_nobump_nospec",

    # Faceshader and envmap
    "faceshader_high_specular": "faceshader",
    "envmap_shader_noskin_bump_colorspec": "envmap_shader",
    "map_ocean_shader_high": "map_ocean_shader",
    "water_shader_high": "water_shader",
    "water_shader_mud_high": "water_shader",

    # Banner & diffuse fallbacks
    "tex_mul_color_alpha_lance_banner": "standart_shader",
    "dot3_alpha_two_diffuse": "standart_shader",
}

total_replacements = 0
modified_files = 0

for f in sorted(os.listdir(RES_DIR)):
    if f.endswith(".brf") and not f.endswith(".bak.brf"):
        p = os.path.join(RES_DIR, f)
        with open(p, "rb") as fp:
            data = fp.read()
        
        orig_data = data
        file_replaced = 0
        
        for old_s, new_s in SHADER_MAP.items():
            pattern_old = struct.pack("<I", len(old_s)) + old_s.encode("ascii")
            pattern_new = struct.pack("<I", len(new_s)) + new_s.encode("ascii")
            
            c = data.count(pattern_old)
            if c > 0:
                data = data.replace(pattern_old, pattern_new)
                file_replaced += c
                total_replacements += c
        
        if file_replaced > 0:
            with open(p, "wb") as fp:
                fp.write(data)
            modified_files += 1
            print(f"Patched {f:35s}: replaced {file_replaced:3d} shader references")

print(f"\nCOMPLETED: Replaced {total_replacements} shader references across {modified_files} BRF files!")
