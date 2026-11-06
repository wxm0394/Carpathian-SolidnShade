#!/usr/bin/env python3
"""
Carpathian Solid & Shade — .sco 场景红名单自动体检与机关移植工具
用法:
  1) 全量体检当前 SceneObj 是否丢失任何 S&S 机关/暗门/出生点:
     python3 sco_sns_tool.py audit "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"

  2) 将旧备份 .sco 中的暗门(Passage)与 S&S 专属物件一键移植进新替换的 .sco (自动放在指定坐标待 Ctrl+E 微调):
     python3 sco_sns_tool.py transplant old_scn_town_6_prison.sco SceneObj/scn_town_6_prison.sco 0,2,0
"""
import os
import struct
import sys

SCO_MAGIC = -717  # 0xFFFFFD33

REDLIST_RULES = {
    "scn_town_2_center":       {"entries": [0], "passages": [], "props": ["spr_container_small_chest"]},
    "scn_town_2_tavern":       {"entries": [0, 16], "passages": [], "props": []},
    "scn_town_3_store":        {"entries": [0], "passages": [], "props": ["spr_caskofamontillado"]},
    "scn_town_5_center":       {"entries": [0], "passages": [], "props": ["spr_container_small_chest"]},
    "scn_town_6_prison":       {"entries": [0], "passages": [(17, 0)], "props": ["spr_thirteen"]},
    "scn_town_9_tavern":       {"entries": [0], "passages": [(18, 0)], "props": ["spr_thirteen"]},
    "scn_town_11_center":      {"entries": [0, 8], "passages": [], "props": []},
    "scn_town_12_center":      {"entries": [0, 8], "passages": [], "props": []},
    "scn_town_13_center":      {"entries": [0], "passages": [], "props": ["spr_container_chest_b"]},
    "scn_town_14_castle":      {"entries": [0, 1], "passages": [(19, 0)], "props": ["spr_thirteen"]},
    "scn_town_15_center":      {"entries": [0, 8], "passages": [], "props": []},
    "scn_town_17_tavern":      {"entries": [0, 8], "passages": [], "props": ["spr_purloinedletter"]},
    "scn_town_18_center":      {"entries": [0, 8], "passages": [], "props": ["spr_VenusDeMilo"]},
    "scn_castle_12_prison":    {"entries": [0, 1], "passages": [], "props": []},
    "scn_castle_15_exterior":  {"entries": [0], "passages": [], "props": ["spr_snakedummy"]},
    "scn_castle_24_interior":  {"entries": [0, 3], "passages": [], "props": []},
    "scn_castle_25_interior":  {"entries": [0, 3], "passages": [], "props": []},
    "scn_castle_36_interior":  {"entries": [0, 3], "passages": [], "props": []},
    "scn_village_4":           {"entries": [0], "passages": [], "props": ["spr_container_small_chest", "spr_sheriffarrow"]},
    "scn_village_5":           {"entries": [0, 5], "passages": [], "props": []},
    "scn_village_20":          {"entries": [0, 5], "passages": [], "props": ["spr_ChessTower"]},
    "scn_village_25":          {"entries": [0, 5], "passages": [], "props": []},
    "scn_village_27":          {"entries": [0, 5], "passages": [], "props": []},
    "scn_village_31":          {"entries": [0, 5], "passages": [], "props": ["spr_hut"]},
    "scn_village_35":          {"entries": [0, 5, 7, 8], "passages": [], "props": ["spr_strangeshell", "spr_poseidonruins"]},
    "scn_village_41":          {"entries": [0, 6, 7], "passages": [], "props": []},
    "scn_village_43":          {"entries": [0], "passages": [(21, 0)], "props": []},
    "scn_village_48":          {"entries": [0, 5], "passages": [(11, 0)], "props": ["spr_UnderworldGate", "spr_Ferryboat"]},
    "scn_village_56":          {"entries": [0], "passages": [], "props": ["spr_goldbug"]},
    "scn_village_61":          {"entries": [0, 5], "passages": [], "props": []},
    "scn_village_66":          {"entries": [0], "passages": [], "props": ["spr_container_small_chest", "spr_annabelleetombstone"]},
    "scn_village_67":          {"entries": [0], "passages": [(10, 0)], "props": []},
    "scn_village_75":          {"entries": [0, 5], "passages": [], "props": []},
    "scn_village_84":          {"entries": [0], "passages": [], "props": ["spr_cocoon"]},
    "scn_village_88":          {"entries": [0, 5], "passages": [], "props": ["spr_gorgonruins"]},
}


def parse_sco(path):
    data = open(path, "rb").read()
    magic, ver, nobj = struct.unpack_from("<iii", data, 0)
    if magic != SCO_MAGIC:
        raise ValueError(f"{path}: 非标准 .sco 头 ({hex(magic & 0xFFFFFFFF)})")
    off = 12
    records = []
    for _ in range(nobj):
        start = off
        otype, sub_id, unused = struct.unpack_from("<iii", data, off)
        rot_pos = list(struct.unpack_from("<12f", data, off + 12))
        slen = struct.unpack_from("<i", data, off + 60)[0]
        off += 64
        sname = data[off : off + slen].decode("latin1", errors="replace")
        off += slen
        vraw = struct.unpack_from("<Q", data, off)[0]
        scale = list(struct.unpack_from("<3f", data, off + 8))
        off += 20
        records.append({
            "otype": otype, "sub_id": sub_id, "unused": unused,
            "rot_pos": rot_pos, "sname": sname, "vraw": vraw,
            "scale": scale, "raw": data[start:off],
        })
    return ver, records, data[off:]


def audit_mod(mod_dir):
    scn_dir = os.path.join(mod_dir, "SceneObj")
    errors = 0
    for sname, rule in REDLIST_RULES.items():
        p = os.path.join(scn_dir, sname + ".sco")
        if not os.path.exists(p):
            print(f"[缺失文件] {sname}.sco")
            errors += 1
            continue
        _, recs, _ = parse_sco(p)
        eps = {r["vraw"] & 0xFF for r in recs if r["otype"] == 1}
        psgs = {(r["vraw"] >> 32, r["vraw"] & 0xFFFFFFFF) for r in recs if r["otype"] == 5}
        props = {r["sname"] for r in recs if r["otype"] == 0}

        miss_ep = [e for e in rule["entries"] if e not in eps]
        miss_psg = [pg for pg in rule["passages"] if pg not in psgs]
        miss_prp = [pr for pr in rule["props"] if pr not in props]
        if miss_ep or miss_psg or miss_prp:
            errors += 1
            print(f"[告警] {sname}.sco -> 缺Entry={miss_ep} | 缺Passage(mno,ep)={miss_psg} | 缺Prop={miss_prp}")
    if errors == 0:
        print("[全部通过] 35/35 个红名单场景机关、暗门与出生点 100% 完整！")
    else:
        print(f"[汇总] 共发现 {errors} 个场景存在机关缺失。")


def pack_record(r):
    sb = r["sname"].encode("latin1")
    return (
        struct.pack("<iii12fi", r["otype"], r["sub_id"], r["unused"], *r["rot_pos"], len(sb))
        + sb
        + struct.pack("<Q3f", r["vraw"], *r["scale"])
    )


def transplant_special(old_sco, new_sco, pos_xyz):
    ver_old, recs_old, _ = parse_sco(old_sco)
    ver_new, recs_new, tail_new = parse_sco(new_sco)
    sname = os.path.splitext(os.path.basename(new_sco))[0]
    rule = REDLIST_RULES.get(sname, {"passages": [], "props": []})
    want_psg = set(rule["passages"])
    want_prp = set(rule["props"]) | {"spr_thirteen"}

    injected = []
    for r in recs_old:
        is_psg = r["otype"] == 5 and (r["vraw"] >> 32, r["vraw"] & 0xFFFFFFFF) in want_psg
        is_prp = r["otype"] == 0 and r["sname"] in want_prp
        if is_psg or is_prp:
            nr = dict(r)
            nr["rot_pos"] = list(r["rot_pos"])
            nr["rot_pos"][9:12] = pos_xyz
            injected.append(nr)

    out_recs = recs_new + injected
    header = struct.pack("<iii", SCO_MAGIC, ver_new, len(out_recs))
    body = b"".join(pack_record(r) for r in out_recs)
    with open(new_sco, "wb") as f:
        f.write(header + body + tail_new)
    print(f"[移植完成] 已向 {new_sco} 无损注入 {len(injected)} 个原版机关/暗门对象（保留原地形与 AI 网格尾部 {len(tail_new)} 字节）。")


DEFAULT_MOD_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "audit":
        mod_p = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_MOD_DIR
        audit_mod(mod_p)
    elif len(sys.argv) == 5 and sys.argv[1] == "transplant":
        xyz = [float(x) for x in sys.argv[4].split(",")]
        transplant_special(sys.argv[2], sys.argv[3], xyz)
    else:
        print(__doc__)
