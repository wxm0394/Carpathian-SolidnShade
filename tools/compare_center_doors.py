import os, struct

def parse_sco(path):
    with open(path, "rb") as f:
        data = f.read()
    magic = struct.unpack("<i", data[:4])[0]
    num_objs = struct.unpack("<i", data[4:8])[0]
    pos = 8
    objs = []
    for idx in range(num_objs):
        otype = struct.unpack("<i", data[pos:pos+4])[0]
        pos += 4
        sname_len = struct.unpack("<i", data[pos:pos+4])[0]
        pos += 4
        sname = data[pos:pos+sname_len].decode('latin1', errors='ignore')
        pos += sname_len
        vraw = struct.unpack("<I", data[pos:pos+4])[0]
        pos += 4
        # 12 floats for rot & pos
        floats = struct.unpack("<12f", data[pos:pos+48])
        pos += 48
        # 3 floats scale
        scale = struct.unpack("<3f", data[pos:pos+12])
        pos += 12
        # obj pos is floats[9:12]
        obj_pos = floats[9:12]
        objs.append({
            "idx": idx, "otype": otype, "name": sname, "pos": obj_pos, "val": vraw
        })
    return objs

cur_objs = parse_sco("/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade/SceneObj/scn_town_1_center.sco")
src_objs = parse_sco("/home/wxm/GOG Games/Mount Blade Warband/game/Modules/World of Vasnar/SceneObj/scn_town_26_center.sco")

print(f"Current town_1_center objects: {len(cur_objs)}")
print(f"Source town_26_center objects: {len(src_objs)}")

# Let's filter for entry points (name == 'entry_point' or otype == 0) and doors (name contains 'door' or 'passage')
print("\n--- Current town_1_center Doors & Entry Points ---")
for o in cur_objs:
    if 'entry' in o['name'].lower() or 'door' in o['name'].lower() or 'passage' in o['name'].lower() or o['otype'] == 0:
        print(f"  [otype={o['otype']}] {o['name']:25s} pos=({o['pos'][0]:7.2f}, {o['pos'][1]:7.2f}, {o['pos'][2]:7.2f}) val={o['val']}")

print("\n--- Source town_26_center Doors & Entry Points ---")
for o in src_objs:
    if 'entry' in o['name'].lower() or 'door' in o['name'].lower() or 'passage' in o['name'].lower() or o['otype'] == 0:
        print(f"  [otype={o['otype']}] {o['name']:25s} pos=({o['pos'][0]:7.2f}, {o['pos'][1]:7.2f}, {o['pos'][2]:7.2f}) val={o['val']}")

