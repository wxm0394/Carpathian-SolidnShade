#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade (1521) — Stage 4A Overhaul Guard & Integrity Verifier
==============================================================================
用于在全面替换 1521 五大王国兵种树、装备、领主、聚落场景期间，随时执行静态安全体检：
  1. 表长度与尾部追加校验（严禁删行/插行导致索引平移）
  2. S&S 锁定槽位防误改校验（重点拦截 trp[363] 堤丰、trp[464..484] 亡灵领主、trp[490] 黑男爵、pt[108..113] 亡灵增援）
  3. 商店生命线物品 itp_merchandise (0x00010000 = 65536) 掩码存活校验（防止仪式材料断供死档）
  4. 全模组字节码（scripts/menus/triggers/simple_triggers/conversation/mission_templates）0 越界引用校验
  5. 一键列出/清理 184 件“零字节码引用”的原版中世纪装备商店售卖位（itp_merchandise），净化 1521 商店池

用法:
  python3 overhaul_guard.py snapshot [MOD_DIR]
  python3 overhaul_guard.py check [MOD_DIR]
  python3 overhaul_guard.py list-hideable [MOD_DIR]
  python3 overhaul_guard.py strip-unused-merch [MOD_DIR] [--apply]
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime

DEFAULT_MOD_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overhaul_baseline.json")

ITP_MERCHANDISE = 0x00010000  # 65536 (Warband header_items.py 真实掩码位)
TF_HERO = 0x00000010

# S&S 仪式、解剖、尸妻、宠物、盐矿大巧匠、海钓与驱魔必需从商店购买的 Native + S&S 生命线商品索引
LIFELINE_MERCH_INDICES = sorted(set(
    list(range(102, 114))   # 熏鱼/风干肉/牛肉/猪肉/面包/苹果/奶酪/鸡肉/蜂蜜/腊肠/圆白菜/黄油
    + list(range(142, 156)) # 葡萄酒/麦芽酒/香料/盐/小麦/面粉(147)/铁/油/陶器/亚麻布/毛皮/羊毛/天鹅绒/工具
    + list(range(156, 167)) + [173, 176] # 蜡/粘土/丝绸/蜡烛/木头/水晶/白银/硫酸/甲醛/黄金/钻石/番红花(173)/象牙(176)
    + list(range(180, 187)) # 7 种原版活马（杀马取马尸/海神献祭4骏马/炼蛇油/占卜）
    + [189, 196, 197, 198, 200, 201, 202, 238, 273] # 盐矿仪式护具 + 尸妻护具 + 海钓绑腿靴(200)
    + [302, 305, 317, 319, 320, 321, 420, 444]      # 木杖/棒/镰刀/小刀/屠夫刀/短剑/石头/驱魔黑风帽(444)
    + [459]                 # 商店铁铲 itm_shovel2（盗墓与换子仪式必需）
))

# 允许 1521 原地换皮修改的 troops.txt 槽位集合（其余 0..849 槽位均受保护）
EDITABLE_TROOP_INDICES = set(
    list(range(184, 248))   # 5 大历史王国常规兵种树 (64 槽)
    + list(range(358, 363)) # 5 大历史王国君主 (5 槽，注意 363 堤丰不在内！)
    + list(range(364, 464)) # 5 大历史王国领主 (100 槽，注意 464..484 亡灵领主不在内！)
    + list(range(485, 490)) # 5 大历史王国复国者 (5 槽，注意 490 黑男爵不在内！)
    + list(range(491, 512)) # 5 大历史王国贵族女士 (21 槽)
)

# 允许 1521 原地换皮修改的 party_templates.txt 槽位集合
EDITABLE_PT_INDICES = set(range(93, 108))  # pt_kingdom_1..5_reinforcements_a/b/c (15 槽，108..113 亡灵增援严禁动)


def load_csv_map(mod_dir, filename):
    d = {}
    p = os.path.join(mod_dir, "languages", "cns", filename)
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                if "|" in line:
                    k, v = line.rstrip("\r\n").split("|", 1)
                    d[k] = v
    return d


def parse_items(mod_dir):
    path = os.path.join(mod_dir, "item_kinds1.txt")
    raw_lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    non_empty = [(idx, l.strip()) for idx, l in enumerate(raw_lines) if l.strip()]
    declared = int(non_empty[1][1])
    items = []
    p = 2
    while p < len(non_empty):
        orig_ln, s = non_empty[p]
        toks = s.split()
        if toks[0].startswith("itm_"):
            num_meshes = int(toks[3])
            flag_tok_idx = 4 + 2 * num_meshes
            flags = int(toks[flag_tok_idx])
            items.append({
                "idx": len(items),
                "id": toks[0],
                "name": toks[1],
                "flags": flags,
                "raw_line_idx": orig_ln,
                "flag_tok_idx": flag_tok_idx,
            })
            p += 2
            if p < len(non_empty) and re.match(r"^\d+$", non_empty[p][1]):
                fk = int(non_empty[p][1])
                p += 1 + (1 if fk > 0 else 0)
            while p < len(non_empty) and not non_empty[p][1].startswith("itm_"):
                p += 1
        else:
            p += 1
    return declared, items, raw_lines


def parse_troops(mod_dir):
    lines = [l.strip() for l in open(os.path.join(mod_dir, "troops.txt"), encoding="utf-8", errors="replace") if l.strip()]
    declared = int(lines[1])
    troops = []
    i = 2
    while i < len(lines):
        if lines[i].startswith("trp_"):
            toks = lines[i].split()
            troops.append({
                "idx": len(troops),
                "id": toks[0],
                "name": toks[1],
                "flags": int(toks[4]),
                "up1": int(toks[8]) if len(toks) > 8 else 0,
                "up2": int(toks[9]) if len(toks) > 9 else 0,
            })
            i += 6
        else:
            i += 1
    return declared, troops


def parse_party_templates(mod_dir):
    lines = [l.strip() for l in open(os.path.join(mod_dir, "party_templates.txt"), encoding="utf-8", errors="replace") if l.strip()]
    declared = int(lines[1])
    pts = []
    for l in lines[2:]:
        if l.startswith("pt_"):
            toks = l.split()
            pts.append({"idx": len(pts), "id": toks[0], "name": toks[1]})
    return declared, pts


def parse_simple_ids(mod_dir, fn, prefix):
    lines = [l.strip() for l in open(os.path.join(mod_dir, fn), encoding="utf-8", errors="replace") if l.strip()]
    out = []
    for l in lines:
        toks = l.split()
        for t in toks[:3]:
            if t.startswith(prefix):
                out.append(t)
                break
    return out


def collect_bytecode_item_refs_and_oob(mod_dir, counts):
    """扫描全部字节码表，返回 (被引用物品索引集合, 越界错误列表)"""
    # header_common.py 真实 tag 映射:
    # 2=var, 3=str, 4=itm, 5=trp, 6=fac, 7=qst, 8=pt, 9=p, 10=scn, 12=mnu, 13=script, 15=spr, 22=qstr
    tag_map = {
        2: ("var", counts["var"]),
        3: ("str", counts["str"]),
        4: ("itm", counts["itm"]),
        5: ("trp", counts["trp"]),
        6: ("fac", counts["fac"]),
        7: ("qst", counts["qst"]),
        8: ("pt", counts["pt"]),
        9: ("p", counts["p"]),
        10: ("scn", counts["scn"]),
        12: ("mnu", counts["mnu"]),
        13: ("script", counts["script"]),
        15: ("spr", counts["spr"]),
    }
    # 直接以物品 ID 为参数的无 tag 字节码指令 (参数下标映射)
    item_op_arg_pos = {
        500: [0],    # player_has_item
        1530: [1],   # troop_add_item
        1531: [1],   # troop_remove_item
        1535: [1],   # troop_add_items
        1536: [1],   # troop_remove_items
        1538: [1],   # troop_has_item_equipped
        1543: [1],   # store_item_kind_count
        1726: [1],   # agent_has_item_equipped
    }
    ref_items = set()
    oob_errors = []

    def record_itm_arg(val, ctx, op):
        if 0 <= val < (1 << 50):
            if val >= counts["itm"]:
                oob_errors.append(f"{ctx} op={op}: untagged itm[{val}] >= {counts['itm']}")
            else:
                ref_items.add(val)

    def scan_op_stream(tokens, pos, ctx):
        num_ops = int(tokens[pos])
        pos += 1
        for _ in range(num_ops):
            op = int(tokens[pos]) & 0xFFFF
            na = int(tokens[pos + 1])
            args = [int(tokens[pos + 2 + k]) for k in range(na)]
            pos += 2 + na
            if op in item_op_arg_pos:
                for ap in item_op_arg_pos[op]:
                    if ap < len(args) and args[ap] >= 0 and args[ap] < (1 << 50):
                        record_itm_arg(args[ap], ctx, op)
            for a in args:
                if a > (1 << 56):
                    tag = (a >> 56) & 0xFF
                    idx = a & 0xFFFFFFFFFFFFFF
                    if tag == 4:
                        ref_items.add(idx)
                    if tag in tag_map:
                        tname, limit = tag_map[tag]
                        if idx >= limit:
                            oob_errors.append(f"{ctx} op={op}: {tname}[{idx}] >= {limit}")
        return pos

    # 1. scripts.txt ("scriptsfile version 1" -> count at stoks[3])
    stoks = open(os.path.join(mod_dir, "scripts.txt"), encoding="utf-8", errors="replace").read().split()
    n_scr = int(stoks[3])
    pos = 4
    for _ in range(n_scr):
        sname = stoks[pos]
        pos += 2  # name + -1.0
        pos = scan_op_stream(stoks, pos, f"script:{sname}")

    # 2. menus.txt ("menusfile version 1" -> count at mtoks[3])
    mtoks = open(os.path.join(mod_dir, "menus.txt"), encoding="utf-8", errors="replace").read().split()
    n_mnu = int(mtoks[3])
    pos = 4
    for _ in range(n_mnu):
        mname = mtoks[pos]
        pos += 4  # id flags text mesh
        pos = scan_op_stream(mtoks, pos, f"menu:{mname}")
        n_opt = int(mtoks[pos])
        pos += 1
        for _ in range(n_opt):
            oname = mtoks[pos]
            pos += 1
            pos = scan_op_stream(mtoks, pos, f"menu:{mname}/{oname}:cond")
            pos += 1  # text
            pos = scan_op_stream(mtoks, pos, f"menu:{mname}/{oname}:cons")
            pos += 1  # door

    # 3. triggers.txt ("triggersfile version 1" -> count at ttoks[3])
    ttoks = open(os.path.join(mod_dir, "triggers.txt"), encoding="utf-8", errors="replace").read().split()
    n_trg = int(ttoks[3])
    pos = 4
    for ti in range(n_trg):
        pos += 3
        pos = scan_op_stream(ttoks, pos, f"trigger[{ti}]:cond")
        pos = scan_op_stream(ttoks, pos, f"trigger[{ti}]:cons")

    # 4. simple_triggers.txt ("simple_triggers_file version 1" -> count at st_toks[3])
    st_toks = open(os.path.join(mod_dir, "simple_triggers.txt"), encoding="utf-8", errors="replace").read().split()
    n_strg = int(st_toks[3])
    pos = 4
    for ti in range(n_strg):
        pos += 1
        pos = scan_op_stream(st_toks, pos, f"simple_trigger[{ti}]")

    # 5. conversation.txt
    clines = [l.strip() for l in open(os.path.join(mod_dir, "conversation.txt"), encoding="utf-8", errors="replace") if l.strip()][2:]
    for li, l in enumerate(clines):
        ct = l.split()
        did = ct[0]
        p = scan_op_stream(ct, 3, f"dlg:{did}:cond")
        p += 2  # text + out_state
        scan_op_stream(ct, p, f"dlg:{did}:cons")

    # 6. mission_templates.txt (扫描高位 tag + 战团环境/材质检测指令如 500/1538/1543/1726)
    mtlines = [l.strip() for l in open(os.path.join(mod_dir, "mission_templates.txt"), encoding="utf-8", errors="replace") if l.strip()]
    for li, l in enumerate(mtlines):
        ltoks = l.split()
        # 触发器行: interval delay rearm cond_ops ... cons_ops ...
        if len(ltoks) >= 5 and re.match(r"^-?\d+(\.\d+)?$", ltoks[0]) and re.match(r"^-?\d+(\.\d+)?$", ltoks[1]) and re.match(r"^-?\d+(\.\d+)?$", ltoks[2]) and ltoks[3].isdigit():
            try:
                p = scan_op_stream(ltoks, 3, f"mt_line[{li}]:cond")
                if p < len(ltoks) and ltoks[p].isdigit():
                    scan_op_stream(ltoks, p, f"mt_line[{li}]:cons")
            except Exception:
                pass
        for tok in ltoks:
            if tok.isdigit() and len(tok) >= 17:
                v = int(tok)
                tag = (v >> 56) & 0xFF
                idx = v & 0xFFFFFFFFFFFFFF
                if tag == 24:
                    ref_items.add(idx)
                if tag in tag_map:
                    tname, limit = tag_map[tag]
                    if idx >= limit:
                        oob_errors.append(f"mission_templates: {tname}[{idx}] >= {limit}")

    # 7. bonus chests (troops 797..824) 物品栏引用
    tlines = [l.strip() for l in open(os.path.join(mod_dir, "troops.txt"), encoding="utf-8", errors="replace") if l.strip()]
    ti = 0
    i = 2
    while i < len(tlines):
        if tlines[i].startswith("trp_"):
            if 797 <= ti <= 824 or ti <= 183 or (283 <= ti <= 356) or (464 <= ti <= 484) or ti == 490:
                inv_toks = tlines[i + 1].split()
                for k in range(0, len(inv_toks), 2):
                    iv = int(inv_toks[k])
                    if iv >= 0:
                        if ti >= 797:
                            ref_items.add(iv)
                        if iv >= counts["itm"]:
                            oob_errors.append(f"troop[{ti}] inventory itm[{iv}] >= {counts['itm']}")
            ti += 1
            i += 6
        else:
            i += 1

    return ref_items, oob_errors


def gather_counts(mod_dir, n_itm, n_trp, n_pt):
    vars_l = [l.strip() for l in open(os.path.join(mod_dir, "variables.txt"), encoding="utf-8", errors="replace") if l.strip()]
    strs_n = int([l.strip() for l in open(os.path.join(mod_dir, "strings.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    facs_n = int([l.strip() for l in open(os.path.join(mod_dir, "factions.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    qsts_n = int([l.strip() for l in open(os.path.join(mod_dir, "quests.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    ps_n = int([l.strip() for l in open(os.path.join(mod_dir, "parties.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    scns_n = int([l.strip() for l in open(os.path.join(mod_dir, "scenes.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    mnus_n = int([l.strip() for l in open(os.path.join(mod_dir, "menus.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    scrs_n = int([l.strip() for l in open(os.path.join(mod_dir, "scripts.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    sprs_n = int([l.strip() for l in open(os.path.join(mod_dir, "scene_props.txt"), encoding="utf-8", errors="replace") if l.strip()][1].split()[0])
    return {
        "var": len(vars_l), "str": strs_n, "itm": n_itm, "trp": n_trp,
        "fac": facs_n, "qst": qsts_n, "pt": n_pt, "p": ps_n,
        "scn": scns_n, "mnu": mnus_n, "script": scrs_n, "spr": sprs_n,
    }


def is_sns_custom_item(idx):
    return (
        (56 <= idx <= 101)
        or (114 <= idx <= 141)
        or idx == 147
        or (156 <= idx <= 176)
        or idx in (255, 344, 379)
        or (448 <= idx <= 786)
        or (788 <= idx <= 816)
        or (823 <= idx <= 826)
        or (828 <= idx <= 829)
        or (832 <= idx <= 901)
    )


def cmd_snapshot(mod_dir):
    dec_itm, items, _ = parse_items(mod_dir)
    dec_trp, troops = parse_troops(mod_dir)
    dec_pt, pts = parse_party_templates(mod_dir)
    counts = gather_counts(mod_dir, len(items), len(troops), len(pts))
    ref_items, oob = collect_bytecode_item_refs_and_oob(mod_dir, counts)
    if oob:
        print(f"[错误] 当前基线存在 {len(oob)} 处字节码越界，拒绝生成快照！")
        for e in oob[:10]:
            print("  -", e)
        return 1

    locked_items = {}
    hideable_items = []
    for it in items:
        idx = it["idx"]
        if is_sns_custom_item(idx) or idx in ref_items or idx in (0, 447):
            locked_items[str(idx)] = it["id"]
        else:
            hideable_items.append(idx)

    locked_troops = {
        str(t["idx"]): t["id"]
        for t in troops
        if t["idx"] < 850 and t["idx"] not in EDITABLE_TROOP_INDICES
    }
    locked_pts = {
        str(pt["idx"]): pt["id"]
        for pt in pts
        if pt["idx"] < 114 and pt["idx"] not in EDITABLE_PT_INDICES
    }

    data = {
        "created_at": datetime.now().isoformat(),
        "mod_dir": mod_dir,
        "counts": counts,
        "locked_items": locked_items,
        "hideable_native_item_indices": hideable_items,
        "locked_troops": locked_troops,
        "locked_pts": locked_pts,
        "lifeline_merch_indices": LIFELINE_MERCH_INDICES,
    }
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[快照已生成] {BASELINE_PATH}")
    print(f"  - 锁定保护物品 ID: {len(locked_items)} / {len(items)} (可安全下架的原版装备: {len(hideable_items)} 件)")
    print(f"  - 锁定保护兵种/NPC ID: {len(locked_troops)} / {len(troops)} (允许原地换皮的 5 国槽位: {len(EDITABLE_TROOP_INDICES)} 个)")
    print(f"  - 锁定保护队伍模板 ID: {len(locked_pts)} / {len(pts)} (允许换皮的 5 国增援模板: {len(EDITABLE_PT_INDICES)} 个)")
    return 0


def cmd_check(mod_dir):
    if not os.path.exists(BASELINE_PATH):
        cmd_snapshot(mod_dir)
    baseline = json.load(open(BASELINE_PATH, encoding="utf-8"))
    cn_itm = load_csv_map(mod_dir, "item_kinds.csv")
    cn_trp = load_csv_map(mod_dir, "troops.csv")

    dec_itm, items, _ = parse_items(mod_dir)
    dec_trp, troops = parse_troops(mod_dir)
    dec_pt, pts = parse_party_templates(mod_dir)
    counts = gather_counts(mod_dir, len(items), len(troops), len(pts))

    errors = []
    warnings = []

    # 1. 表头声明数与实际数一致 + 不低于基线
    if dec_itm != len(items):
        errors.append(f"item_kinds1.txt 表头声明 ({dec_itm}) != 实际条目数 ({len(items)})")
    if dec_trp != len(troops):
        errors.append(f"troops.txt 表头声明 ({dec_trp}) != 实际条目数 ({len(troops)})")
    if dec_pt != len(pts):
        errors.append(f"party_templates.txt 表头声明 ({dec_pt}) != 实际条目数 ({len(pts)})")

    for k, base_v in baseline["counts"].items():
        if counts[k] < base_v:
            errors.append(f"表容量缩水 [{k}]: 当前 {counts[k]} < 基线 {base_v}（严禁删行导致索引前移！）")

    # 2. 锁定物品 ID 槽位防漂移
    for idx_s, expected_id in baseline["locked_items"].items():
        idx = int(idx_s)
        if idx >= len(items) or items[idx]["id"] != expected_id:
            actual = items[idx]["id"] if idx < len(items) else "MISSING"
            errors.append(f"锁定物品槽位被篡改/错位: itm[{idx}] 期望 {expected_id}, 实际 {actual}")

    # 3. 商店生命线 itp_merchandise (0x00010000) 校验
    for idx in baseline["lifeline_merch_indices"]:
        if idx < len(items):
            if (items[idx]["flags"] & ITP_MERCHANDISE) == 0:
                cn = cn_itm.get(items[idx]["id"], items[idx]["name"])
                errors.append(
                    f"商店生命线物品失去 itp_merchandise(0x10000): itm[{idx}] {items[idx]['id']} ({cn}) — 会导致 S&S 仪式/解剖/海钓材料断供！"
                )

    # 4. 锁定兵种/NPC 槽位防漂移（含高危陷阱 363 堤丰、464..484 亡灵领主、490 黑男爵）
    for idx_s, expected_id in baseline["locked_troops"].items():
        idx = int(idx_s)
        if idx >= len(troops) or troops[idx]["id"] != expected_id:
            actual = troops[idx]["id"] if idx < len(troops) else "MISSING"
            errors.append(f"锁定兵种/NPC 槽位被篡改/错位: trp[{idx}] 期望 {expected_id}, 实际 {actual}")

    # 检查天启三君主 tf_hero 标志与升级目标合法性
    for k_idx in (358, 359, 360, 361, 362):
        if k_idx < len(troops) and (troops[k_idx]["flags"] & TF_HERO) == 0:
            errors.append(f"君主 trp[{k_idx}] ({troops[k_idx]['id']}) 丢失 tf_hero(0x10) 标志！")
    for t in troops:
        for u in (t["up1"], t["up2"]):
            if u < 0 or u >= len(troops):
                errors.append(f"兵种升级目标越界: trp[{t['idx']}] {t['id']} -> trp[{u}] >= {len(troops)}")

    # 5. 锁定队伍模板防漂移
    for idx_s, expected_id in baseline["locked_pts"].items():
        idx = int(idx_s)
        if idx >= len(pts) or pts[idx]["id"] != expected_id:
            actual = pts[idx]["id"] if idx < len(pts) else "MISSING"
            errors.append(f"锁定队伍模板被篡改/错位: pt[{idx}] 期望 {expected_id}, 实际 {actual}")

    # 6. 全量字节码引用越界扫描
    _, oob_errors = collect_bytecode_item_refs_and_oob(mod_dir, counts)
    errors.extend(oob_errors)

    print("=" * 72)
    print(" Carpathian Solid & Shade (1521) — 阶段 4A 换皮安全护栏体检报告")
    print("=" * 72)
    print(f"  物品总数 (item_kinds1)    : {len(items):4d} (基线 902, 新增 {len(items)-902:+d})")
    print(f"  兵种总数 (troops)         : {len(troops):4d} (基线 850, 新增 {len(troops)-850:+d})")
    print(f"  队伍模板 (party_templates): {len(pts):4d} (基线 114, 新增 {len(pts)-114:+d})")
    print(f"  场景总数 (scenes)         : {counts['scn']:4d} | 全局变量 (variables): {counts['var']:4d}")
    print("-" * 72)
    if not errors:
        print("  [全部通过] 0 槽位漂移 | 0 生命线断供 | 0 字节码越界引用！")
        print("  重点高危槽位复核:")
        print(f"    - trp[363] {troops[363]['id']} ({cn_trp.get(troops[363]['id'], '')}) 完好")
        print(f"    - trp[464..484] 亡灵第六国 21 魔神领主完好")
        print(f"    - trp[490] {troops[490]['id']} ({cn_trp.get(troops[490]['id'], '')}) 完好")
        print(f"    - pt[108..113] 亡灵第六国 a..f 六阶增援模板完好")
        print(f"    - {len(baseline['lifeline_merch_indices'])} 件 S&S 商店生命线商品 itp_merchandise(0x10000) 100% 在售")
        return 0
    else:
        print(f"  [体检失败] 共检出 {len(errors)} 项阻断性错误:")
        for e in errors[:40]:
            print(f"    [!] {e}")
        if len(errors) > 40:
            print(f"    ... 其余 {len(errors) - 40} 项已省略")
        return 1


def cmd_list_hideable(mod_dir):
    if not os.path.exists(BASELINE_PATH):
        cmd_snapshot(mod_dir)
    baseline = json.load(open(BASELINE_PATH, encoding="utf-8"))
    cn_itm = load_csv_map(mod_dir, "item_kinds.csv")
    _, items, _ = parse_items(mod_dir)
    hideable = baseline["hideable_native_item_indices"]
    active_merch = [i for i in hideable if (items[i]["flags"] & ITP_MERCHANDISE) != 0]
    print(f"=== 零字节码引用的原版装备槽位: 共 {len(hideable)} 件 (当前仍在商店刷新的有 {len(active_merch)} 件) ===")
    for idx in hideable:
        it = items[idx]
        m = "在售(0x10000)" if (it["flags"] & ITP_MERCHANDISE) else "已隐藏"
        print(f"  [{idx:3d}] {it['id']:34s} | {cn_itm.get(it['id'], it['name']):16s} | {m}")
    return 0


def cmd_strip_unused_merch(mod_dir, apply_changes=False):
    if not os.path.exists(BASELINE_PATH):
        cmd_snapshot(mod_dir)
    baseline = json.load(open(BASELINE_PATH, encoding="utf-8"))
    hideable = set(baseline["hideable_native_item_indices"])
    _, items, raw_lines = parse_items(mod_dir)

    changed = 0
    for it in items:
        if it["idx"] in hideable and (it["flags"] & ITP_MERCHANDISE) != 0:
            ln = it["raw_line_idx"]
            toks = raw_lines[ln].split()
            fi = it["flag_tok_idx"]
            old_f = int(toks[fi])
            new_f = old_f & (~ITP_MERCHANDISE)
            toks[fi] = str(new_f)
            raw_lines[ln] = " " + " ".join(toks)
            changed += 1

    if not apply_changes:
        print(f"[预览模式] 将从 1521 商店下架 {changed} 件零 S&S 引用的原版装备（清除 0x00010000 位，保留槽位与模型不破坏存档）。")
        print("如需真正写入磁盘，请追加参数: --apply")
        return 0

    target = os.path.join(mod_dir, "item_kinds1.txt")
    bak = target + ".bak_pre_strip_merch"
    if not os.path.exists(bak):
        shutil.copy2(target, bak)
    with open(target, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(raw_lines) + "\n")
    print(f"[写入完成] 已下架 {changed} 件原版未引用装备，原文件已备份至: {bak}")
    return cmd_check(mod_dir)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    action = args[0]
    apply_flag = "--apply" in args
    pos_args = [a for a in args[1:] if not a.startswith("--")]
    mod_dir = pos_args[0] if pos_args else DEFAULT_MOD_DIR

    if action == "snapshot":
        return cmd_snapshot(mod_dir)
    elif action == "check":
        return cmd_check(mod_dir)
    elif action == "list-hideable":
        return cmd_list_hideable(mod_dir)
    elif action == "strip-unused-merch":
        return cmd_strip_unused_merch(mod_dir, apply_changes=apply_flag)
    else:
        print(f"未知子命令: {action}\n{__doc__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
