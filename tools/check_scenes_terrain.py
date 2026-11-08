import os

mod_dir = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
vn_dir = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/World of Vasnar"

def get_scene_line(scenes_path, scn_name):
    with open(scenes_path, "r", encoding="latin1") as f:
        for l in f:
            if l.startswith(scn_name + " "):
                return l.strip()
    return None

cur_town1 = get_scene_line(os.path.join(mod_dir, "scenes.txt"), "scn_town_1_center")
vn_town26 = get_scene_line(os.path.join(vn_dir, "scenes.txt"), "scn_town_26_center")

print("Current town_1_center scene line:")
print(" ", cur_town1)
print("\nVasnar town_26_center scene line:")
print(" ", vn_town26)

