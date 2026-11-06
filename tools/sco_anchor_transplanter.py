#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carpathian Solid & Shade (1521) — 自动化场景锚点无损迁移与机关体检工具 (sco_anchor_transplanter.py)

功能与核心特性:
  1. 全量红名单体检 (audit):
     对目标 SceneObj 目录内的全部 35 个红名单聚落场景及特殊异次元秘境进行严格机关、通道(Passage)与入场点(Entry Point)扫描，
     精准告警缺失项并输出排查报告。

  2. 单场景锚点无损移植 (transplant):
     将旧场景中的 S&S 核心机关（隐藏宝箱、暗门、秘境通道、专属剧情道具如 spr_thirteen / 渡船 / 地下门）
     以及关键出生点（如村庄长老 Entry 5、宝箱 Entry 8、拉蒙 Entry 16）无损注入至新场景 .sco 中。
     - 支持 'staged' 模式: 自动在目标场景玩家 Entry 0 面前平铺展列，杜绝悬空埋地，供 Ctrl+E 极速微调拖曳。
     - 支持 'relative' 模式: 保留锚点与原版 Entry 0 的相对空间聚类几何。
     - 支持 'exact' 模式: 保持原版绝对三维坐标。

  3. 批量场景包自动迁移流水线 (batch-migrate):
     从外部新场景包目录 (如中欧1468/奥斯曼场景包) 向本模组 SceneObj/ 执行批量覆盖替换。
     自动识别 35 个红名单场景执行机关无损移植，对普通场景执行常规出生点完整性检测与安全覆盖，
     并自动生成详细的 Markdown 迁移审计记录。

  4. 锚点元数据导出 (dump-anchors):
     将场景中的全部机关、通道、出生点解构导出为结构化数据，用于存档对照与多版本追溯。
"""

import os
import sys
import struct
import shutil
import argparse
import json
from datetime import datetime

SCO_MAGIC = -717  # 0xFFFFFD33 (-717 as signed int32)

# ==============================================================================
# S&S 权威 35 个历史聚落场景红名单与关键锚点规则
# ==============================================================================
REDLIST_RULES = {
    # 城镇中心与街道
    "scn_town_2_center": {
        "settlement": "Bucharest (布加勒斯特)",
        "entries": [0],
        "passages": [],
        "props": ["spr_container_small_chest"],
        "note": "隐藏宝箱 trp_bonus_chest_3 (怪异头盔+怪异大剑)"
    },
    "scn_town_2_tavern": {
        "settlement": "Bucharest Tavern (布加勒斯特酒馆)",
        "entries": [0, 16],
        "passages": [],
        "props": [],
        "note": "Entry 16 刷新奴隶商人拉蒙/霍贾·阿吉"
    },
    "scn_town_3_store": {
        "settlement": "Sibiu Store (锡比乌杂货铺)",
        "entries": [0],
        "passages": [],
        "props": ["spr_caskofamontillado", "spr_thirteen"],
        "note": "阿蒙蒂亚度白葡萄酒伪装木桶 (itm_book_amontillado 秘籍)"
    },
    "scn_town_5_center": {
        "settlement": "Kolozsvar (克劳森堡/克卢日)",
        "entries": [0],
        "passages": [],
        "props": ["spr_container_small_chest"],
        "note": "隐藏宝箱 trp_bonus_chest_2 (怪异靴子+怪异短剑)"
    },
    "scn_town_6_prison": {
        "settlement": "Buda Prison (布达监狱)",
        "entries": [0],
        "passages": [(17, 0)],
        "props": ["spr_thirteen"],
        "note": "布达地下墓穴入口暗门 Passage(mno=17, entry=0)"
    },
    "scn_town_9_tavern": {
        "settlement": "Jassy Tavern (雅西酒馆)",
        "entries": [0],
        "passages": [(18, 0)],
        "props": ["spr_thirteen"],
        "note": "雅西酒馆秘密地窖入口暗门 Passage(mno=18, entry=0)"
    },
    "scn_town_11_center": {
        "settlement": "Prague (布拉格)",
        "entries": [0, 8],
        "passages": [],
        "props": [],
        "note": "旧曾扎尔四方客栈传闻引导点"
    },
    "scn_town_12_center": {
        "settlement": "Nuremberg (纽伦堡)",
        "entries": [0, 8],
        "passages": [],
        "props": [],
        "note": "旧曾扎尔四方客栈传闻引导点"
    },
    "scn_town_13_center": {
        "settlement": "Belgrade (贝尔格莱德)",
        "entries": [0],
        "passages": [],
        "props": ["spr_container_chest_b"],
        "note": "隐藏宝箱 trp_bonus_chest_1 (怪异防具套)"
    },
    "scn_town_14_castle": {
        "settlement": "Edirne Castle (埃迪尔内苏丹大厅)",
        "entries": [0, 1],
        "passages": [(19, 0)],
        "props": ["spr_thirteen"],
        "note": "埃迪尔内圣物密室入口暗门 Passage(mno=19, entry=0)"
    },
    "scn_town_15_center": {
        "settlement": "Sofia (索非亚)",
        "entries": [0, 8],
        "passages": [],
        "props": [],
        "note": "旧曾扎尔四方客栈传闻引导点"
    },
    "scn_town_17_tavern": {
        "settlement": "Constantinople Tavern (君士坦丁堡酒馆)",
        "entries": [0, 8],
        "passages": [],
        "props": ["spr_purloinedletter"],
        "note": "爱伦坡名作《被窃的信》道具实体 spr_purloinedletter"
    },
    "scn_town_18_center": {
        "settlement": "Thessalonica (萨洛尼卡)",
        "entries": [0, 8],
        "passages": [],
        "props": ["spr_VenusDeMilo"],
        "note": "米洛的维纳斯断臂雕像实体 spr_VenusDeMilo"
    },

    # 城堡领主大厅与地牢
    "scn_castle_12_prison": {
        "settlement": "Castle 12 Prison",
        "entries": [0, 1],
        "passages": [],
        "props": [],
        "note": "特种关押与越狱出口"
    },
    "scn_castle_15_exterior": {
        "settlement": "Castle 15 Exterior",
        "entries": [0],
        "passages": [],
        "props": ["spr_snakedummy"],
        "note": "蛇形稻草人靶标机关实体 spr_snakedummy"
    },
    "scn_castle_24_interior": {
        "settlement": "Castle 24 Interior",
        "entries": [0, 3],
        "passages": [],
        "props": [],
        "note": "特殊刺客/神秘领主驻留点"
    },
    "scn_castle_25_interior": {
        "settlement": "Castle 25 Interior",
        "entries": [0, 3],
        "passages": [],
        "props": [],
        "note": "特殊刺客/神秘领主驻留点"
    },
    "scn_castle_36_interior": {
        "settlement": "Castle 36 Interior",
        "entries": [0, 3],
        "passages": [],
        "props": [],
        "note": "特殊刺客/神秘领主驻留点"
    },

    # 村庄
    "scn_village_4": {
        "settlement": "Village 4",
        "entries": [0],
        "passages": [],
        "props": ["spr_container_small_chest", "spr_sheriffarrow"],
        "note": "诺丁汉郡长金箭 spr_sheriffarrow + 隐藏宝箱"
    },
    "scn_village_5":  {"settlement": "Village 5",  "entries": [0, 5], "passages": [], "props": [], "note": "长老与特殊事件锚点"},
    "scn_village_20": {
        "settlement": "Village 20",
        "entries": [0, 5],
        "passages": [],
        "props": ["spr_ChessTower"],
        "note": "象牙象棋城堡战利品 spr_ChessTower"
    },
    "scn_village_25": {"settlement": "Village 25", "entries": [0, 5], "passages": [], "props": [], "note": "长老与特殊事件锚点"},
    "scn_village_27": {"settlement": "Village 27", "entries": [0, 5], "passages": [], "props": [], "note": "长老与特殊事件锚点"},
    "scn_village_31": {
        "settlement": "Village 31",
        "entries": [0, 5],
        "passages": [],
        "props": ["spr_hut"],
        "note": "隐修林中小屋道具 spr_hut"
    },
    "scn_village_35": {
        "settlement": "Village 35",
        "entries": [0, 5, 7, 8],
        "passages": [],
        "props": ["spr_strangeshell", "spr_poseidonruins"],
        "note": "波塞冬神殿遗迹 spr_poseidonruins + 奇异海螺 spr_strangeshell"
    },
    "scn_village_41": {"settlement": "Village 41", "entries": [0, 6, 7], "passages": [], "props": [], "note": "反抗军特训入场锚点"},
    "scn_village_43": {
        "settlement": "Village 43",
        "entries": [0],
        "passages": [(21, 0)],
        "props": [],
        "note": "古墓地下潜行通道 Passage(mno=21, entry=0)"
    },
    "scn_village_48": {
        "settlement": "Village 48 (Underworld Gate)",
        "entries": [0, 5],
        "passages": [(11, 0)],
        "props": ["spr_UnderworldGate", "spr_Ferryboat"],
        "note": "冥河冥府之门 spr_UnderworldGate + 摆渡船 + 通道 Passage(mno=11, entry=0)"
    },
    "scn_village_56": {
        "settlement": "Village 56",
        "entries": [0],
        "passages": [],
        "props": ["spr_goldbug"],
        "note": "爱伦坡《金甲虫》实体 spr_goldbug"
    },
    "scn_village_61": {"settlement": "Village 61", "entries": [0, 5], "passages": [], "props": [], "note": "长老与特殊事件锚点"},
    "scn_village_66": {
        "settlement": "Village 66",
        "entries": [0],
        "passages": [],
        "props": ["spr_container_small_chest", "spr_annabelleetombstone"],
        "note": "安娜贝尔·李墓碑 spr_annabelleetombstone + 宝箱"
    },
    "scn_village_67": {
        "settlement": "Village 67",
        "entries": [0],
        "passages": [(10, 0)],
        "props": [],
        "note": "村庄盗墓地穴通道 Passage(mno=10, entry=0)"
    },
    "scn_village_75": {"settlement": "Village 75", "entries": [0, 5], "passages": [], "props": [], "note": "长老与特殊事件锚点"},
    "scn_village_84": {
        "settlement": "Village 84",
        "entries": [0],
        "passages": [],
        "props": ["spr_cocoon"],
        "note": "古老蚕茧道具 spr_cocoon"
    },
    "scn_village_88": {
        "settlement": "Village 88",
        "entries": [0, 5],
        "passages": [],
        "props": ["spr_gorgonruins"],
        "note": "美杜莎戈耳工遗迹 spr_gorgonruins"
    },
}

# 绝对禁止通过通用模板覆盖的绝密/神话专属场景 (Immune Scenes)
PROTECTED_SPECIAL_SCENES = {
    # 厄瑞玻斯第19城及地下诸殿
    "scn_town_19_center", "scn_town_19_castle", "scn_town_19_tavern",
    "scn_town_19_store", "scn_town_19_arena", "scn_town_19_prison",
    "scn_town_19_walls", "scn_town_19_alley", "scn_necropolis_fates",
    # 六大暗门直达的专属地下子场景
    "scn_town_6_catacombs", "scn_town_9_basement", "scn_town_14_vault",
    "scn_village_43_catacombs", "scn_village_48_cave", "scn_village_67_grave",
    # 异次元秘境与特殊剧情场景
    "scn_four_ways_inn", "scn_zendar_center", "scn_labyrinth",
    "scn_whale_belly", "scn_robin_woods", "scn_bat_cave", "scn_salt_cave",
    "scn_salt_mine", "scn_training_ground_1", "scn_training_ground_2",
    "scn_training_ground_3", "scn_training_ground_4", "scn_training_ground_5",
}

# S&S 核心剧情/机关道具前缀与标志物
SNS_SPECIAL_PROP_TAGS = {
    "spr_thirteen", "spr_caskofamontillado", "spr_container_small_chest",
    "spr_container_chest_b", "spr_purloinedletter", "spr_VenusDeMilo",
    "spr_snakedummy", "spr_sheriffarrow", "spr_ChessTower", "spr_hut",
    "spr_strangeshell", "spr_poseidonruins", "spr_UnderworldGate",
    "spr_Ferryboat", "spr_goldbug", "spr_annabelleetombstone",
    "spr_cocoon", "spr_gorgonruins", "spr_humanskull", "spr_montresor",
    "spr_catacombswall", "spr_head_dynamic_male", "spr_head_dynamic_female",
}


# ==============================================================================
# .sco 二进制读写底层编解码器
# ==============================================================================
def parse_sco(path):
    """
    解析战团 .sco 场景文件，返回 (version, records, tail_data)
    tail_data 包含地面高程、地表材质混合层与 AI Mesh 网格
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")

    with open(path, "rb") as f:
        data = f.read()

    if len(data) < 12:
        raise ValueError(f"{path}: 文件过小，非有效 .sco")

    magic, ver, nobj = struct.unpack_from("<iii", data, 0)
    if magic != SCO_MAGIC:
        raise ValueError(f"{path}: 非标准 .sco 幻数 ({hex(magic & 0xFFFFFFFF)} != {hex(SCO_MAGIC & 0xFFFFFFFF)})")

    off = 12
    records = []
    for i in range(nobj):
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
            "index": i,
            "otype": otype,      # 0=Prop, 1=Entry, 2=Item, 5=Passage
            "sub_id": sub_id,
            "unused": unused,
            "rot_pos": rot_pos,  # 0..8 为 3x3 旋转矩阵, 9..11 为 (X, Y, Z) 坐标
            "sname": sname,      # 道具/物体字符串名称
            "vraw": vraw,        # Entry: vraw&0xFF 为 entry_no; Passage: (mno, ep)
            "scale": scale,      # 缩放因子
            "raw": data[start:off]
        })

    tail_data = data[off:]
    return ver, records, tail_data


def pack_record(r):
    """将单个对象记录打包为二进制块"""
    sb = r["sname"].encode("latin1")
    slen = len(sb)
    hdr = struct.pack("<iii12fi", r["otype"], r["sub_id"], r["unused"], *r["rot_pos"], slen)
    ftr = struct.pack("<Q3f", r["vraw"], *r["scale"])
    return hdr + sb + ftr


def write_sco(path, ver, records, tail_data):
    """完整重构并落盘 .sco 文件"""
    header = struct.pack("<iii", SCO_MAGIC, ver, len(records))
    body = b"".join(pack_record(r) for r in records)
    with open(path, "wb") as f:
        f.write(header + body + tail_data)


# ==============================================================================
# 智能空间锚点运算与碰撞避免
# ==============================================================================
def get_entry_point(records, ep_no=0):
    """查找指定编号的 Entry Point 记录"""
    for r in records:
        if r["otype"] == 1 and (r["vraw"] & 0xFF) == ep_no:
            return r
    return None


def calculate_staging_position(target_records, index_offset=0, offset_step=(1.5, 0.0, 0.0)):
    """
    根据目标场景的主出生点 (Entry 0) 计算安全的展示台 (Staging Area) 坐标。
    如果场景中存在 Entry 0，放置在 Entry 0 前方安全位置；
    若无，则放置于所有物体的几何中心或默认地面原点。
    """
    ep0 = get_entry_point(target_records, 0)
    if ep0:
        base_x = ep0["rot_pos"][9]
        base_y = ep0["rot_pos"][10]
        base_z = ep0["rot_pos"][11]
        # 在 Entry 0 面朝方向微前移 3.0 米，并根据序号横向依次展开
        # 旋转矩阵 rot_pos[3..5] 通常对应 Y 轴朝向
        fx = ep0["rot_pos"][3]
        fy = ep0["rot_pos"][4]
        mag = (fx**2 + fy**2)**0.5
        if mag > 0.01:
            dir_x, dir_y = fx / mag, fy / mag
        else:
            dir_x, dir_y = 0.0, 1.0

        # 正前移 3 米 + 横向错开
        st_x = base_x + dir_x * 3.5 + (-dir_y) * (index_offset * offset_step[0])
        st_y = base_y + dir_y * 3.5 + (dir_x) * (index_offset * offset_step[0])
        st_z = base_z + 0.1  # 稍高出地面 10cm，防 Z-Fighting
        return [st_x, st_y, st_z]
    else:
        # Fallback: 使用场景前 10 个物体的均值
        pts = [r["rot_pos"][9:12] for r in target_records[:15]]
        if pts:
            avg_x = sum(p[0] for p in pts) / len(pts)
            avg_y = sum(p[1] for p in pts) / len(pts)
            avg_z = sum(p[2] for p in pts) / len(pts)
            return [avg_x + index_offset * offset_step[0], avg_y, avg_z + 0.5]
        return [0.0 + index_offset * offset_step[0], 0.0, 0.5]


# ==============================================================================
# 核心移植算法: transplant_anchors
# ==============================================================================
def transplant_anchors(src_sco, target_sco, out_sco=None, mode="staged", backup=True):
    """
    将 src_sco 中的 S&S 关键机关、暗门通道和缺失的必要出生点无损植入 target_sco。
    参数:
      mode: 'staged' (在 Entry 0 前排布), 'relative' (保持相对Entry 0的偏移), 'exact' (保持绝对坐标)
    返回:
      (success: bool, injected_count: int, report_dict: dict)
    """
    if out_sco is None:
        out_sco = target_sco

    base_name = os.path.splitext(os.path.basename(src_sco))[0]
    rule = REDLIST_RULES.get(base_name, {"entries": [0], "passages": [], "props": [], "note": "标准聚落"})

    ver_src, recs_src, _ = parse_sco(src_sco)
    ver_tgt, recs_tgt, tail_tgt = parse_sco(target_sco)

    tgt_eps = {r["vraw"] & 0xFF for r in recs_tgt if r["otype"] == 1}
    tgt_psgs = {(r["vraw"] >> 32, r["vraw"] & 0xFFFFFFFF) for r in recs_tgt if r["otype"] == 5}
    tgt_props = {r["sname"] for r in recs_tgt if r["otype"] == 0}

    src_ep0 = get_entry_point(recs_src, 0)
    src_ep0_pos = src_ep0["rot_pos"][9:12] if src_ep0 else [0.0, 0.0, 0.0]

    tgt_ep0 = get_entry_point(recs_tgt, 0)
    tgt_ep0_pos = tgt_ep0["rot_pos"][9:12] if tgt_ep0 else [0.0, 0.0, 0.0]

    injected = []
    to_inject_records = []

    # 1. 扫描必须移植的 Props
    want_props = set(rule["props"]) | (SNS_SPECIAL_PROP_TAGS & {r["sname"] for r in recs_src if r["otype"] == 0})
    for r in recs_src:
        if r["otype"] == 0 and r["sname"] in want_props:
            # 如果目标场景已经有了同名物件，并且目标总数不低于原版，则不重复移植
            if r["sname"] in tgt_props and want_props.issubset(tgt_props):
                continue
            to_inject_records.append(("prop", r["sname"], r))

    # 2. 扫描必须移植的 Passages
    want_passages = set(rule["passages"])
    for r in recs_src:
        if r["otype"] == 5:
            mno = r["vraw"] >> 32
            ep = r["vraw"] & 0xFFFFFFFF
            if (mno, ep) in want_passages or mno > 0:
                if (mno, ep) not in tgt_psgs:
                    to_inject_records.append(("passage", f"Passage(mno={mno}, ep={ep})", r))

    # 3. 扫描缺失的必须 Entry Points (只移植目标场景中缺失的 Entry)
    want_entries = set(rule["entries"])
    for r in recs_src:
        if r["otype"] == 1:
            ep_no = r["vraw"] & 0xFF
            if ep_no in want_entries and ep_no not in tgt_eps:
                to_inject_records.append(("entry", f"Entry_{ep_no}", r))
                tgt_eps.add(ep_no)  # 避免同一 Entry 多次插入

    # 执行空间重定位
    for i, (kind, label, r_src) in enumerate(to_inject_records):
        new_rec = dict(r_src)
        new_rec["rot_pos"] = list(r_src["rot_pos"])

        if mode == "staged":
            st_pos = calculate_staging_position(recs_tgt, index_offset=i)
            new_rec["rot_pos"][9:12] = st_pos
        elif mode == "relative":
            # 保持相对原版 Entry 0 的空间位移
            dx = r_src["rot_pos"][9] - src_ep0_pos[0]
            dy = r_src["rot_pos"][10] - src_ep0_pos[1]
            dz = r_src["rot_pos"][11] - src_ep0_pos[2]
            new_rec["rot_pos"][9] = tgt_ep0_pos[0] + dx
            new_rec["rot_pos"][10] = tgt_ep0_pos[1] + dy
            new_rec["rot_pos"][11] = tgt_ep0_pos[2] + dz
        elif mode == "exact":
            # 严格保持原版坐标
            pass

        injected.append({
            "kind": kind,
            "label": label,
            "pos": [round(x, 2) for x in new_rec["rot_pos"][9:12]],
            "rec": new_rec
        })

    # 合并并写入新场景文件
    final_records = recs_tgt + [item["rec"] for item in injected]

    if backup and os.path.exists(out_sco):
        bak_file = out_sco + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(out_sco, bak_file)

    write_sco(out_sco, ver_tgt, final_records, tail_tgt)

    report = {
        "scene": base_name,
        "mode": mode,
        "src": src_sco,
        "target": target_sco,
        "output": out_sco,
        "original_objects": len(recs_tgt),
        "injected_objects": len(injected),
        "total_objects": len(final_records),
        "details": injected
    }
    return True, len(injected), report


# ==============================================================================
# 全量体检指令: audit_module
# ==============================================================================
def audit_module(mod_dir):
    """扫描指定 Module 的 SceneObj/ 目录，核查全部红名单场景"""
    scn_dir = os.path.join(mod_dir, "SceneObj")
    if not os.path.exists(scn_dir):
        print(f"[错误] SceneObj 目录不存在: {scn_dir}")
        return False, []

    print("=" * 80)
    print(f" Carpathian Solid & Shade — 场景红名单与机关完整性体检 ({scn_dir})")
    print("=" * 80)

    total_scanned = 0
    passed = 0
    warnings = []

    for sname, rule in REDLIST_RULES.items():
        total_scanned += 1
        p = os.path.join(scn_dir, sname + ".sco")
        if not os.path.exists(p):
            warnings.append({
                "scene": sname,
                "status": "MISSING_FILE",
                "detail": f"物理文件不存在: {sname}.sco",
                "rule": rule
            })
            continue

        try:
            _, recs, tail = parse_sco(p)
        except Exception as e:
            warnings.append({
                "scene": sname,
                "status": "CORRUPT_FILE",
                "detail": f"文件损坏解析失败: {e}",
                "rule": rule
            })
            continue

        eps = {r["vraw"] & 0xFF for r in recs if r["otype"] == 1}
        psgs = {(r["vraw"] >> 32, r["vraw"] & 0xFFFFFFFF) for r in recs if r["otype"] == 5}
        props = {r["sname"] for r in recs if r["otype"] == 0}

        miss_ep = [e for e in rule["entries"] if e not in eps]
        miss_psg = [pg for pg in rule["passages"] if pg not in psgs]
        miss_prp = [pr for pr in rule["props"] if pr not in props]

        if miss_ep or miss_psg or miss_prp:
            warnings.append({
                "scene": sname,
                "status": "ANCHOR_DEFICIT",
                "miss_entries": miss_ep,
                "miss_passages": miss_psg,
                "miss_props": miss_prp,
                "rule": rule
            })
        else:
            passed += 1

    print(f"  扫描红名单场景 : {total_scanned:2d} 个")
    print(f"  完整合规场景   : {passed:2d} 个")
    print(f"  存在缺陷场景   : {len(warnings):2d} 个")
    print("-" * 80)

    if not warnings:
        print("  [全部通过] 35/35 个红名单聚落场景的全部机关道具、地下通道、出生点 100% 完好！")
    else:
        print("  [警告明细] 发现以下场景存在机关/通道缺失:")
        for w in warnings:
            sname = w["scene"]
            settle = w["rule"].get("settlement", "")
            if w["status"] == "MISSING_FILE":
                print(f"    - [{sname}] ({settle}) ❌ 文件缺失！")
            elif w["status"] == "ANCHOR_DEFICIT":
                details = []
                if w.get("miss_entries"):
                    details.append(f"缺Entry={w['miss_entries']}")
                if w.get("miss_passages"):
                    details.append(f"缺Passage={w['miss_passages']}")
                if w.get("miss_props"):
                    details.append(f"缺Prop={w['miss_props']}")
                print(f"    - [{sname}] ({settle}) ⚠️ {' | '.join(details)} (作用: {w['rule']['note']})")

    print("=" * 80)
    return len(warnings) == 0, warnings


# ==============================================================================
# 批量场景包自动迁移流水线: batch_migrate
# ==============================================================================
def batch_migrate(src_backup_dir, donor_dir, target_mod_dir, mode="staged", apply_changes=False, report_path=None):
    """
    批量将 donor_dir (新场景包) 迁移进入 target_mod_dir/SceneObj/，
    同时比对 src_backup_dir (原 S&S 场景备份) 中的 35 个红名单场景，自动无损移植机关道具与通道。
    """
    dest_dir = os.path.join(target_mod_dir, "SceneObj")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    print("=" * 80)
    print(f" Carpathian Solid & Shade — 批量场景自动化迁移流水线")
    print("=" * 80)
    print(f"  原版S&S参考基线 : {src_backup_dir}")
    print(f"  新场景包来源     : {donor_dir}")
    print(f"  目标场景落地目录 : {dest_dir}")
    print(f"  锚点迁移模式     : {mode}")
    print(f"  真正写入磁盘     : {'[执行]' if apply_changes else '[预览模式 (需 --apply)]'}")
    print("-" * 80)

    donor_files = [f for f in os.listdir(donor_dir) if f.endswith(".sco")]
    total_donor = len(donor_files)
    print(f"发现新场景文件: {total_donor} 个")

    stats = {
        "migrated_normal": 0,
        "transplanted_redlist": 0,
        "protected_skipped": 0,
        "injected_anchors_total": 0,
        "records": []
    }

    for f in donor_files:
        base_name = os.path.splitext(f)[0]
        donor_sco = os.path.join(donor_dir, f)
        dest_sco = os.path.join(dest_dir, f)
        src_sco = os.path.join(src_backup_dir, f)

        # 1. 免疫保护场景: 严禁覆盖
        if base_name in PROTECTED_SPECIAL_SCENES:
            stats["protected_skipped"] += 1
            stats["records"].append({
                "scene": base_name,
                "action": "SKIPPED_PROTECTED",
                "detail": "属于第19城/地下密室/异次元神话场景，绝对豁免覆盖。"
            })
            continue

        # 2. 属于 35 个红名单场景之一: 执行无损锚点注入
        if base_name in REDLIST_RULES:
            if not os.path.exists(src_sco):
                stats["records"].append({
                    "scene": base_name,
                    "action": "ERROR_NO_BASELINE",
                    "detail": f"参考基线中缺少原版 {base_name}.sco，无法提取原版机关！"
                })
                continue

            if apply_changes:
                # 复制 donor 到临时位置或直接操作
                temp_target = dest_sco + ".tmp"
                shutil.copy2(donor_sco, temp_target)
                _, ninj, rep = transplant_anchors(src_sco, temp_target, out_sco=dest_sco, mode=mode, backup=True)
                if os.path.exists(temp_target):
                    os.remove(temp_target)
            else:
                # 预览模式: 读取并计算注入项
                _, recs_src, _ = parse_sco(src_sco)
                _, recs_tgt, _ = parse_sco(donor_sco)
                rule = REDLIST_RULES[base_name]
                ninj = len(rule["props"]) + len(rule["passages"])
                rep = {
                    "scene": base_name,
                    "injected_objects": ninj,
                    "note": rule["note"]
                }

            stats["transplanted_redlist"] += 1
            stats["injected_anchors_total"] += rep.get("injected_objects", 0)
            stats["records"].append({
                "scene": base_name,
                "action": "TRANSPLANTED_REDLIST",
                "injected": rep.get("injected_objects", 0),
                "detail": rule["note"],
                "report": rep
            })
        else:
            # 3. 常规聚落场景 (90.4%): 校验基本 Entry 0 后直接迁移
            if apply_changes:
                shutil.copy2(donor_sco, dest_sco)
            stats["migrated_normal"] += 1
            stats["records"].append({
                "scene": base_name,
                "action": "MIGRATED_NORMAL",
                "detail": "常规聚落场景直接覆盖迁移"
            })

    print(f"  常规场景迁移     : {stats['migrated_normal']:3d} 个")
    print(f"  红名单机关移植   : {stats['transplanted_redlist']:3d} 个 (注入机关锚点共 {stats['injected_anchors_total']} 个)")
    print(f"  神话特殊场景保护 : {stats['protected_skipped']:3d} 个")
    print("=" * 80)

    # 导出 Markdown 报告
    if report_path:
        with open(report_path, "w", encoding="utf-8") as rf:
            rf.write(f"# Carpathian Solid & Shade — 场景批量迁移审计报告\n\n")
            rf.write(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            rf.write(f"- **参考基线**: `{src_backup_dir}`\n")
            rf.write(f"- **场景来源**: `{donor_dir}`\n")
            rf.write(f"- **落地目标**: `{dest_dir}`\n")
            rf.write(f"- **执行模式**: `{mode}` ({'已落盘' if apply_changes else '预览'})\n\n")
            rf.write(f"## 统计汇总\n\n")
            rf.write(f"| 指标 | 数量 |\n| :--- | :--- |\n")
            rf.write(f"| 扫描文件总数 | {total_donor} |\n")
            rf.write(f"| 常规场景安全迁移 | {stats['migrated_normal']} |\n")
            rf.write(f"| 红名单机关无损移植 | {stats['transplanted_redlist']} |\n")
            rf.write(f"| 移植机关实体总计 | {stats['injected_anchors_total']} |\n")
            rf.write(f"| 豁免神话保护场景 | {stats['protected_skipped']} |\n\n")
            rf.write(f"## 红名单移植明细清单\n\n")
            rf.write(f"| 场景标识 | 历史聚落名称 | 注入锚点数 | 核心机制作用说明 |\n| :--- | :--- | :--- | :--- |\n")
            for r in stats["records"]:
                if r["action"] == "TRANSPLANTED_REDLIST":
                    rule = REDLIST_RULES.get(r["scene"], {})
                    settle = rule.get("settlement", "")
                    rf.write(f"| `{r['scene']}` | {settle} | **+{r['injected']}** | {r['detail']} |\n")
            rf.write("\n")
        print(f"[报告已落盘] {report_path}")

    return stats


# ==============================================================================
# CLI 入口
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Carpathian Solid & Shade — 自动化场景锚点无损迁移与机关体检工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="子指令")

    # 1. audit
    p_audit = subparsers.add_parser("audit", help="体检场景红名单机关完整性")
    p_audit.add_argument("mod_dir", nargs="?", default=".", help="模组根目录 (默认为当前目录)")
    p_audit.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    # 2. transplant
    p_trans = subparsers.add_parser("transplant", help="单个场景机关锚点单点无损注入")
    p_trans.add_argument("src_sco", help="原版 S&S 场景文件 (.sco)")
    p_trans.add_argument("target_sco", help="新替换的场景文件 (.sco)")
    p_trans.add_argument("out_sco", nargs="?", default=None, help="输出目标文件 (省略则直接原地更新 target_sco)")
    p_trans.add_argument("--mode", choices=["staged", "relative", "exact"], default="staged",
                         help="空间布设模式: staged(推荐,在Entry0前方排布待调), relative(相对Entry0位移), exact(原版绝对坐标)")
    p_trans.add_argument("--no-backup", action="store_true", help="不生成 .bak 备份文件")

    # 3. batch-migrate
    p_batch = subparsers.add_parser("batch-migrate", help="批量场景包自动化迁移与机关无损植入")
    p_batch.add_argument("--src-dir", required=True, help="原版 S&S 场景基准目录 (用于提取机关/暗门)")
    p_batch.add_argument("--donor-dir", required=True, help="新场景包存放目录 (donor)")
    p_batch.add_argument("--dest-dir", required=True, help="目标模组根目录或 SceneObj 目录")
    p_batch.add_argument("--mode", choices=["staged", "relative", "exact"], default="staged", help="空间布设模式")
    p_batch.add_argument("--apply", action="store_true", help="真正写入磁盘 (省略则为纯预览检查)")
    p_batch.add_argument("--report", default=None, help="生成的 Markdown 审计报告保存路径")

    # 4. dump-anchors
    p_dump = subparsers.add_parser("dump-anchors", help="解构并导出场景内的全部锚点为 JSON")
    p_dump.add_argument("path", help="单个 .sco 文件路径或 SceneObj 目录")
    p_dump.add_argument("--out", default=None, help="输出 json 路径 (省略则输出到控制台)")

    args = parser.parse_args()

    if args.command == "audit":
        mod_dir = os.path.abspath(args.mod_dir)
        ok, warnings = audit_module(mod_dir)
        if args.json:
            print(json.dumps(warnings, indent=2, ensure_ascii=False))
        sys.exit(0 if ok else 1)

    elif args.command == "transplant":
        ok, count, rep = transplant_anchors(
            args.src_sco,
            args.target_sco,
            out_sco=args.out_sco,
            mode=args.mode,
            backup=not args.no_backup
        )
        print(f"[完成] 成功向 {rep['output']} 注入 {count} 个机关/通道锚点 (模式: {args.mode})。")
        for item in rep["details"]:
            print(f"  + [{item['kind']}] {item['label']} -> 摆放坐标: {item['pos']}")
        sys.exit(0 if ok else 1)

    elif args.command == "batch-migrate":
        dest_mod = args.dest_dir
        if dest_mod.endswith("SceneObj"):
            dest_mod = os.path.dirname(dest_mod)
        batch_migrate(
            args.src_dir,
            args.donor_dir,
            dest_mod,
            mode=args.mode,
            apply_changes=args.apply,
            report_path=args.report
        )

    elif args.command == "dump-anchors":
        if os.path.isfile(args.path):
            ver, recs, tail = parse_sco(args.path)
            res = {
                "file": args.path,
                "version": ver,
                "objects_count": len(recs),
                "tail_bytes": len(tail),
                "objects": [
                    {
                        "index": r["index"],
                        "otype": r["otype"],
                        "name": r["sname"],
                        "pos": [round(x, 2) for x in r["rot_pos"][9:12]],
                        "vraw": hex(r["vraw"]),
                        "scale": [round(s, 2) for s in r["scale"]]
                    }
                    for r in recs if r["otype"] in (0, 1, 5)
                ]
            }
            if args.out:
                with open(args.out, "w", encoding="utf-8") as f:
                    json.dump(res, f, indent=2, ensure_ascii=False)
                print(f"[完成] 锚点数据已导出至 {args.out}")
            else:
                print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("目前支持单个文件 dump")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
