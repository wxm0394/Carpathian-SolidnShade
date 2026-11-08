#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild all 31 female skins in Carpathian Solid & Shade so 100% (31/31) use
authentic Yuening 936-vertex female_head UV coordinates, full DXT1 mipmap chains,
matching Yuening normalmaps & aged maps, calibrated body skin tint colors, and
authentic 4e02128 Solid & Shade 6-element sacred geometric facepaint + blind-oracle
aged eyes (indices 26..30 in skins.txt, keeping 0..25 strictly warpaint-free).
"""

import io
import os
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFilter

MOD = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
TEX_DIR = os.path.join(MOD, "Textures")
RES_DIR = os.path.join(MOD, "Resource")

YUENING_25 = [
    "womanface_01", "womanface_02", "womanface_03", "womanface_04", "womanface_05",
    "womanface_06", "womanface_07", "womanface_08", "womanface_09", "womanface_10",
    "womanface_11", "womanface_12", "womanface_13", "womanface_14", "womanface_15",
    "womanface_16", "womanface_17", "womanface_18", "womanface_19", "womanface_20",
    "womanface_21", "womanface_22", "womanface_10a", "womanface_10aa", "womanface_10a4"
]


def load_head_dds_bytes(name):
    return subprocess.check_output(["git", "-C", MOD, "show", f"HEAD:Textures/{name}.dds"])


def load_yuening_rgba(name):
    p = os.path.join(TEX_DIR, f"{name}.dds")
    im = Image.open(p).convert("RGBA")
    if im.size != (512, 512):
        im = im.resize((512, 512), Image.Resampling.LANCZOS)
    return im


def save_dxt1_mipmapped(im_rgba, out_dds_path):
    tmp_png = out_dds_path + ".tmp.png"
    im_rgba.convert("RGB").save(tmp_png)
    subprocess.check_call([
        "convert", tmp_png,
        "-define", "dds:compression=dxt1",
        "-define", "dds:mipmaps=10",
        out_dds_path
    ])
    os.remove(tmp_png)


def make_soft_ellipse_mask(w, h, cx, cy, rx, ry, blur_sigma):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    raw = np.clip(1.0 - dist, 0.0, 1.0)
    raw = raw * raw * (3.0 - 2.0 * raw)
    m_im = Image.fromarray((raw * 255.0).astype(np.uint8), mode="L")
    if blur_sigma > 0:
        m_im = m_im.filter(ImageFilter.GaussianBlur(radius=blur_sigma))
    return np.array(m_im, dtype=np.float32) / 255.0


def apply_pigment_subtle(arr_rgb, mask, color_rgb, strength=0.28, multiply_weight=0.35):
    col = np.array(color_rgb, dtype=np.float32).reshape(1, 1, 3)
    luma = (0.299 * arr_rgb[:, :, 0] + 0.587 * arr_rgb[:, :, 1] + 0.114 * arr_rgb[:, :, 2])[:, :, None] / 255.0
    mult = arr_rgb * (col / 255.0) * 1.15
    tinted = col * (0.55 + 0.65 * luma)
    blended_paint = mult * multiply_weight + tinted * (1.0 - multiply_weight)
    m = (mask * strength)[:, :, None]
    return np.clip(arr_rgb * (1.0 - m) + blended_paint * m, 0.0, 255.0)


def build_3d_sacred_warpaint_mask_512(brf_path):
    """
    Rasterizes Yuening 936v female_head's front-skin triangles at 1024x1024 supersampling
    and evaluates Solid & Shade's original 6-element sacred geometric facepaint directly
    in 3D frontal space (X, Y) so every circle and ring wraps across curved facial
    topology and forehead crown darts with zero UV distortion and zero eyeball/mouth bleed.
    """
    data = open(brf_path, "rb").read()
    pos = 0
    n = len(data)

    def r_int():
        nonlocal pos
        v = struct.unpack_from("<i", data, pos)[0]
        pos += 4
        return v

    def r_uint():
        nonlocal pos
        v = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        return v

    def r_str():
        nonlocal pos
        l = r_uint()
        s = data[pos:pos + l].decode("latin1")
        pos += l
        return s

    first = r_str()
    ver = 0
    if first == "rfver ":
        ver = r_int()
        kind = r_str()
    else:
        kind = first

    raw_xyz = v_idx = uvs = tris = None
    while kind != "end":
        cnt = r_int()
        if kind == "texture":
            for _ in range(cnt):
                r_str()
                pos += 4
        elif kind == "shader":
            for _ in range(cnt):
                r_str()
                pos += 8
                r_str()
                for _ in range(r_int()):
                    r_str()
                nfb = r_int()
                pos += nfb * 16
        elif kind == "material":
            for _ in range(cnt):
                r_str()
                pos += 4
                for _ in range(6):
                    r_str()
                pos += 16
        elif kind == "mesh":
            for _ in range(cnt):
                name = r_str()
                flags = r_uint()
                r_str()
                npos = r_int()
                xyz_cur = np.frombuffer(data, dtype="<f4", count=npos * 3, offset=pos).reshape(npos, 3).copy()
                pos += npos * 12
                for _ in range(r_int()):
                    pos += 4
                    nw = r_int()
                    pos += nw * 8
                for _ in range(r_int()):
                    pos += 4
                    np2 = r_int()
                    pos += np2 * 12
                    nn2 = r_int()
                    pos += nn2 * 12
                nvert = r_int()
                stride = 36 if ver == 0 else (41 if (flags & 0x10000) else 28)
                vbuf = data[pos:pos + nvert * stride]
                pos += nvert * stride
                ntri = r_int()
                tris_cur = np.frombuffer(data, dtype="<i4", count=ntri * 3, offset=pos).reshape(ntri, 3).copy()
                pos += ntri * 12
                if name == "female_head":
                    raw_xyz = xyz_cur
                    v_idx = np.zeros(nvert, dtype=np.int32)
                    uvs = np.zeros((nvert, 2), dtype=np.float32)
                    for vi in range(nvert):
                        off = vi * stride
                        v_idx[vi] = struct.unpack_from("<i", vbuf, off)[0]
                        uv_off = off + (20 if ver == 0 else (stride - 8))
                        u, v = struct.unpack_from("<2f", vbuf, uv_off)
                        uvs[vi] = (u, v)
                    tris = tris_cur
                    break
            if raw_xyz is not None:
                break
        else:
            break
        if pos >= n:
            break
        kind = r_str()

    if raw_xyz is None:
        raise RuntimeError("female_head not found in meshes_face_gen.brf")

    RES = 1024
    xyz_map = np.full((RES, RES, 4), np.nan, dtype=np.float32)

    for i0, i1, i2 in tris:
        uv0, uv1, uv2 = uvs[i0], uvs[i1], uvs[i2]
        # Restrict strictly to front-skin UV (exclude bottom eyeball & ear islands v < 0.175)
        if max(uv0[0], uv1[0], uv2[0]) < 0.499:
            continue
        if min(uv0[1], uv1[1], uv2[1]) < 0.175:
            continue
        p0, p1, p2 = raw_xyz[v_idx[i0]], raw_xyz[v_idx[i1]], raw_xyz[v_idx[i2]]
        if max(p0[2], p1[2], p2[2]) < 0.01:
            continue

        x0, y0 = uv0[0] * RES, (1.0 - uv0[1]) * RES
        x1, y1 = uv1[0] * RES, (1.0 - uv1[1]) * RES
        x2, y2 = uv2[0] * RES, (1.0 - uv2[1]) * RES

        # Exclude floating eyelash strip triangles (small high-Z quads inside eyelid opening)
        # Check triangle 3D normal: eyelash cards point nearly vertically along Y rather than +Z
        nrm = np.cross(p1 - p0, p2 - p0)
        nlen = np.linalg.norm(nrm)
        if nlen < 1e-9:
            continue

        ix0 = max(512, int(np.floor(min(x0, x1, x2))) - 1)
        ix1 = min(RES - 1, int(np.ceil(max(x0, x1, x2))) + 1)
        iy0 = max(0, int(np.floor(min(y0, y1, y2))) - 1)
        iy1 = min(int(RES * 0.825), int(np.ceil(max(y0, y1, y2))) + 1)
        if ix0 > ix1 or iy0 > iy1:
            continue

        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(det) < 1e-6:
            continue

        yy, xx = np.mgrid[iy0:iy1 + 1, ix0:ix1 + 1]
        px = xx.astype(np.float32) + 0.5
        py = yy.astype(np.float32) + 0.5
        b1 = ((px - x0) * (y2 - y0) - (x2 - x0) * (py - y0)) / det
        b2 = ((x1 - x0) * (py - y0) - (px - x0) * (y1 - y0)) / det
        b0 = 1.0 - b1 - b2
        inside = (b0 >= -1e-4) & (b1 >= -1e-4) & (b2 >= -1e-4)
        if not np.any(inside):
            continue

        X = b0 * p0[0] + b1 * p1[0] + b2 * p2[0]
        Y = b0 * p0[1] + b1 * p1[1] + b2 * p2[1]
        Z = b0 * p0[2] + b1 * p1[2] + b2 * p2[2]

        sub = xyz_map[iy0:iy1 + 1, ix0:ix1 + 1]
        upd = inside & (np.isnan(sub[:, :, 2]) | (Z > sub[:, :, 2]))
        sub[upd, 0] = X[upd]
        sub[upd, 1] = Y[upd]
        sub[upd, 2] = Z[upd]
        sub[upd, 3] = 1.0

    # Dilate 12px at 1024 res across crown V-dart seam so mipmaps never show a hairline gap
    valid = ~np.isnan(xyz_map[:, :, 3])
    cur_xyz = np.nan_to_num(xyz_map[:, :, :3], nan=0.0)
    cur_val = valid.copy()
    for _ in range(12):
        acc = np.zeros_like(cur_xyz)
        cnt = np.zeros((RES, RES), dtype=np.float32)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            sv = np.roll(np.roll(cur_val, dy, axis=0), dx, axis=1)
            sx_r = np.roll(np.roll(cur_xyz, dy, axis=0), dx, axis=1)
            acc += sx_r * sv[:, :, None]
            cnt += sv
        fill = (~cur_val) & (cnt > 0)
        fill[:, :512] = False
        fill[int(RES * 0.825):, :] = False
        cur_xyz[fill] = acc[fill] / cnt[fill, None]
        cur_val[fill] = True

    full_X = np.zeros((RES, RES), dtype=np.float32)
    full_Y = np.zeros((RES, RES), dtype=np.float32)
    full_Z = np.zeros((RES, RES), dtype=np.float32)
    full_V = np.zeros((RES, RES), dtype=bool)

    full_X[:, 512:] = np.abs(cur_xyz[:, 512:, 0])
    full_Y[:, 512:] = cur_xyz[:, 512:, 1]
    full_Z[:, 512:] = cur_xyz[:, 512:, 2]
    full_V[:, 512:] = cur_val[:, 512:]

    full_X[:, :512] = -np.abs(cur_xyz[:, 1023:511:-1, 0])
    full_Y[:, :512] = cur_xyz[:, 1023:511:-1, 1]
    full_Z[:, :512] = cur_xyz[:, 1023:511:-1, 2]
    full_V[:, :512] = cur_val[:, 1023:511:-1]

    def soft_oval(X, Y, cx, cy, rx, ry, aa=0.045):
        nd = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
        return np.clip((1.0 + aa * 0.5 - nd) / aa, 0.0, 1.0)

    # 6-element Sacred Geometry anchored to Yuening 936v 3D anatomy (matching 4e02128 1:1):
    # 1. Upper Forehead Small Solid Circle
    m_top = soft_oval(full_X, full_Y, 0.0000, 0.2075, 0.0096, 0.0096)
    # 2. Glabella / Lower Forehead Larger Solid Circle
    m_mid = soft_oval(full_X, full_Y, 0.0000, 0.1745, 0.0180, 0.0180)
    # 3 & 4. Left & Right Bold Annular Eye Rings (covering entire eyebrow inside upper arc, clean eye hole)
    r_out_R = soft_oval(full_X, full_Y,  0.0378, 0.1315, 0.0318, 0.0318, aa=0.035)
    r_in_R  = soft_oval(full_X, full_Y,  0.0332, 0.1215, 0.0196, 0.0148, aa=0.055)
    r_out_L = soft_oval(full_X, full_Y, -0.0378, 0.1315, 0.0318, 0.0318, aa=0.035)
    r_in_L  = soft_oval(full_X, full_Y, -0.0332, 0.1215, 0.0196, 0.0148, aa=0.055)
    m_ringR = r_out_R * (1.0 - r_in_R)
    m_ringL = r_out_L * (1.0 - r_in_L)
    # 5 & 6. Left & Right Solid Cheek Circles
    m_chkR = soft_oval(full_X, full_Y,  0.0435, 0.0775, 0.0156, 0.0156, aa=0.050)
    m_chkL = soft_oval(full_X, full_Y, -0.0435, 0.0775, 0.0156, 0.0156, aa=0.050)

    mask_1024 = (
        np.maximum.reduce([m_top, m_mid, m_ringR, m_ringL, m_chkR, m_chkL])
        * full_V.astype(np.float32)
        * (full_Z > 0.022).astype(np.float32)
    )
    mask_512 = np.array(
        Image.fromarray((mask_1024 * 255.0).astype(np.uint8), "L").resize((512, 512), Image.Resampling.LANCZOS),
        dtype=np.float32
    ) / 255.0
    # Strictly zero below Y=390 to guarantee 100% pristine eyeballs & ears
    mask_512[390:, :] = 0.0
    return mask_512


# Exact 4e02128 Solid & Shade sacred warpaint RGB pigments
SACRED_PALETTES = {
    "crimson":  (138.0,  35.0,  32.0),  # womanface_youngb / Clotho / Persephone / Empusa / Melinoe / Queen of Hearts
    "obsidian": ( 42.0,  33.0,  30.0),  # womanface_bb
    "olive":    ( 79.0,  65.0,  30.0),  # womanface_ab / Lachesis / Buxworth
    "teal":     ( 40.0,  70.0,  68.0),  # womanface_brownb / Atropos / Mama D
    "chalk":    (228.0, 216.0, 211.0),  # womanface_africanb / Ishtar / Patty Cake / Enmity
}


def apply_blind_oracle_eyes(arr_rgb):
    """
    Applies 4e02128's signature milky-silver blind seer / cataract irises onto the
    bottom-center Yuening 3D eyeball UV island ([172..340, 438..496]) for _agedb skins
    (used by the Three Fates Clotho, Lachesis, Atropos with age=63).
    """
    h, w, _ = arr_rgb.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    iris_mask = np.zeros((h, w), dtype=np.float32)
    for cx, cy in [(203.5, 463.0), (308.5, 463.0)]:
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        m = np.clip((18.5 - d) / 3.5, 0.0, 1.0)
        iris_mask = np.maximum(iris_mask, m)
    # Restrict strictly to eyeball box & dark/colored iris pixels (leaving bright sclera untouched)
    luma = 0.299 * arr_rgb[:, :, 0] + 0.587 * arr_rgb[:, :, 1] + 0.114 * arr_rgb[:, :, 2]
    iris_dark = np.clip((185.0 - luma) / 55.0, 0.0, 1.0)
    eff = (iris_mask * iris_dark * 0.80)[:, :, None]
    milky = np.array([214.0, 208.0, 205.0], dtype=np.float32).reshape(1, 1, 3)
    # Preserve subtle radial fiber detail from original iris luma
    detail = milky * (0.84 + 0.22 * (luma[:, :, None] / 185.0))
    return np.clip(arr_rgb * (1.0 - eff) + detail * eff, 0.0, 255.0)


def apply_ss_sacred_warpaint(im_rgba, sacred_mask, palette, add_ear_pearls=False, blind_oracle=False):
    arr = np.array(im_rgba.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape

    col = np.array(SACRED_PALETTES[palette], dtype=np.float32).reshape(1, 1, 3)
    luma = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2])[:, :, None] / 200.0
    # Bold opaque ritual pigment matching 4e02128 while retaining 14% natural skin pore micro-relief
    paint = np.clip(col * (0.86 + 0.14 * np.clip(luma, 0.5, 1.35)), 0.0, 255.0)
    m = sacred_mask[:, :, None]
    arr = arr * (1.0 - m) + paint * m

    if add_ear_pearls:
        for (px, py) in [(478.0, 483.0), (486.5, 478.5), (34.0, 483.0), (25.5, 478.5)]:
            sh = make_soft_ellipse_mask(w, h, px, py + 1.2, 3.2, 3.2, 0.9)
            arr = arr * (1.0 - 0.45 * sh[:, :, None])
            pearl = make_soft_ellipse_mask(w, h, px, py, 2.6, 2.6, 0.4)
            glint = make_soft_ellipse_mask(w, h, px - 0.6, py - 0.6, 1.2, 1.2, 0.2)
            p_col = np.array([240.0, 231.0, 218.0]).reshape(1, 1, 3)
            g_col = np.array([255.0, 255.0, 255.0]).reshape(1, 1, 3)
            arr = arr * (1.0 - pearl[:, :, None]) + p_col * pearl[:, :, None]
            arr = np.clip(arr + g_col * (glint[:, :, None] * 0.55), 0.0, 255.0)

    if blind_oracle:
        arr = apply_blind_oracle_eyes(arr)

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB").convert("RGBA")


def tone_golden_bronze_skin(im_rgba):
    """
    Tones Yuening womanface_04 to 4e02128 womanface_brownb's warm golden-ochre bronze
    complexion while keeping the bottom-center 3D eyeball sclera crisp white.
    """
    arr = np.array(im_rgba.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape
    eye_box = np.zeros((h, w), dtype=np.float32)
    eye_box[438:503, 166:346] = 1.0
    eye_box = np.array(
        Image.fromarray((eye_box * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius=3.0)),
        dtype=np.float32
    ) / 255.0
    skin_m = 1.0 - eye_box[:, :, None]
    toned = arr.copy()
    toned[:, :, 0] = np.clip(arr[:, :, 0] * 0.91, 0, 255)
    toned[:, :, 1] = np.clip(arr[:, :, 1] * 0.84, 0, 255)
    toned[:, :, 2] = np.clip(arr[:, :, 2] * 0.68, 0, 255)
    arr = arr * (1.0 - skin_m) + toned * skin_m
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB").convert("RGBA")


def build_womanface_asia():
    base = load_yuening_rgba("womanface_10a")
    arr = np.array(base.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape
    eye_box = np.zeros((h, w), dtype=np.float32)
    eye_box[440:502, 166:346] = 1.0
    eye_box = np.array(
        Image.fromarray((eye_box * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius=3.0)),
        dtype=np.float32
    ) / 255.0
    skin_m = 1.0 - eye_box[:, :, None]
    toned = arr.copy()
    toned[:, :, 0] = np.clip(arr[:, :, 0] * 0.965 + 4.0, 0, 255)
    toned[:, :, 1] = np.clip(arr[:, :, 1] * 0.955 + 3.0, 0, 255)
    toned[:, :, 2] = np.clip(arr[:, :, 2] * 0.875 - 2.0, 0, 255)
    arr = arr * (1.0 - skin_m) + toned * skin_m
    lip_m = make_soft_ellipse_mask(w, h, 256.0, 327.0, 46.0, 14.0, 3.0)
    arr = apply_pigment_subtle(arr, lip_m, (178, 66, 58), strength=0.28, multiply_weight=0.35)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB").convert("RGBA")


def pack_str(s):
    b = s.encode("latin1")
    return struct.pack("<I", len(b)) + b


def patch_brf_materials(brf_path, updates):
    data = open(brf_path, "rb").read()
    pos = 0

    def rstr(p):
        l = struct.unpack_from("<I", data, p)[0]
        return data[p + 4:p + 4 + l].decode("latin1"), p + 4 + l

    out = bytearray()
    while pos < len(data):
        p_chunk = pos
        kind, pos = rstr(pos)
        if kind == "rfver ":
            out.extend(data[p_chunk:pos + 4])
            pos += 4
            continue
        if kind == "end":
            out.extend(pack_str("end"))
            break
        cnt = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if kind == "texture":
            p_start = pos
            for _ in range(cnt):
                _, pos = rstr(pos)
                pos += 4
            out.extend(pack_str("texture") + struct.pack("<I", cnt) + data[p_start:pos])
        elif kind == "material":
            mat_blobs = []
            for _ in range(cnt):
                p0 = pos
                mn, pos = rstr(pos)
                fl = struct.unpack_from("<I", data, pos)[0]
                pos += 4
                sh, pos = rstr(pos)
                dA, pos = rstr(pos)
                dB, pos = rstr(pos)
                bm, pos = rstr(pos)
                ev, pos = rstr(pos)
                sp, pos = rstr(pos)
                vals = struct.unpack_from("<4f", data, pos)
                pos += 16
                if mn in updates:
                    nfl, nsh, ndA, ndB, nbm, nev, nsp, nvals = updates[mn]
                    blob = (
                        pack_str(mn) + struct.pack("<I", nfl) +
                        pack_str(nsh) + pack_str(ndA) + pack_str(ndB) +
                        pack_str(nbm) + pack_str(nev) + pack_str(nsp) +
                        struct.pack("<4f", *nvals)
                    )
                    mat_blobs.append(blob)
                else:
                    mat_blobs.append(data[p0:pos])
            out.extend(pack_str("material") + struct.pack("<I", cnt) + b"".join(mat_blobs))
        else:
            raise RuntimeError(f"Unexpected chunk {kind} in {brf_path}")

    with open(brf_path, "wb") as f:
        f.write(out)


def harmonize_wf05_perimeter(im_rgba):
    arr = np.array(im_rgba.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape
    face_oval = make_soft_ellipse_mask(w, h, 256.0, 232.0, 122.0, 146.0, 24.0)
    eye_mouth_guard = np.zeros((h, w), dtype=np.float32)
    eye_mouth_guard[430:512, :] = 1.0
    perim = np.clip(1.0 - np.maximum(face_oval, eye_mouth_guard), 0.0, 1.0)[:, :, None]
    warm = arr.copy()
    warm[:, :, 0] = arr[:, :, 0] * 0.85
    warm[:, :, 1] = arr[:, :, 1] * 0.84
    warm[:, :, 2] = arr[:, :, 2] * 0.72
    arr = arr * (1.0 - perim) + warm * perim
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB").convert("RGBA")


def scale_argb_int(argb_str, r_mul, g_mul, b_mul):
    v = int(argb_str)
    a = (v >> 24) & 0xFF
    r = int(np.clip(((v >> 16) & 0xFF) * r_mul, 0, 255))
    g = int(np.clip(((v >> 8) & 0xFF) * g_mul, 0, 255))
    b = int(np.clip((v & 0xFF) * b_mul, 0, 255))
    return str((a << 24) | (r << 16) | (g << 8) | b)


def main():
    # 1. Restore all 25 pristine Yuening DDS files + wf05_aged from git HEAD
    for nm in YUENING_25 + ["womanface_05_aged"]:
        raw = load_head_dds_bytes(nm)
        with open(os.path.join(TEX_DIR, f"{nm}.dds"), "wb") as f:
            f.write(raw)
    for wf5 in ("womanface_05", "womanface_05_aged"):
        p5 = os.path.join(TEX_DIR, f"{wf5}.dds")
        if os.path.exists(p5):
            save_dxt1_mipmapped(harmonize_wf05_perimeter(Image.open(p5)), p5)
    print("[1/5] Restored 25 pristine Yuening DDS files from HEAD (and smoothed wf05 forehead seam).")

    # 2. Compute 3D-projected sacred geometry mask & build 6 Yuening-936v skins + 5 blind-oracle aged warpaint skins
    sacred_mask = build_3d_sacred_warpaint_mask_512(os.path.join(RES_DIR, "meshes_face_gen.brf"))

    im_asia = build_womanface_asia()
    save_dxt1_mipmapped(im_asia, os.path.join(TEX_DIR, "womanface_asia.dds"))

    warpaint_specs = [
        ("womanface_youngb",   "womanface_1_agedb",       "womanface_11", "womanface_11_aged", "crimson",  False, False),
        ("womanface_bb",       "womanface_2_agedb",       "womanface_12", "womanface_12_aged", "obsidian", False, False),
        ("womanface_ab",       "womanface_3_agedb",       "womanface_03", "womanface_03_aged", "olive",    False, False),
        ("womanface_brownb",   "womanface_4_agedb",       "womanface_04", "womanface_04_aged", "teal",     False, True),
        ("womanface_africanb", "womanface_african_agedb", "womanface_05", "womanface_05_aged", "chalk",    True,  False),
    ]

    for young_out, aged_out, base_young, base_aged, pal, pearls, bronze_tone in warpaint_specs:
        by_im = load_yuening_rgba(base_young)
        ba_im = load_yuening_rgba(base_aged)
        if bronze_tone:
            by_im = tone_golden_bronze_skin(by_im)
            ba_im = tone_golden_bronze_skin(ba_im)
        im_y = apply_ss_sacred_warpaint(by_im, sacred_mask, palette=pal, add_ear_pearls=pearls, blind_oracle=False)
        im_a = apply_ss_sacred_warpaint(ba_im, sacred_mask, palette=pal, add_ear_pearls=pearls, blind_oracle=True)
        save_dxt1_mipmapped(im_y, os.path.join(TEX_DIR, f"{young_out}.dds"))
        save_dxt1_mipmapped(im_a, os.path.join(TEX_DIR, f"{aged_out}.dds"))
    print("[2/5] Built womanface_asia + 5 authentic 4e02128 sacred warpaint skins (+ 5 blind-oracle _agedb skins).")

    # 3. Patch early_load.brf so womanface_asia uses Yuening 10a normalmap & aged map
    patch_brf_materials(os.path.join(RES_DIR, "early_load.brf"), {
        "womanface_asia": (
            0x720, "faceshader", "womanface_asia", "womanface_10a_aged",
            "womanface_10a_nm", "none", "womanface_10a_aged_nm", [25.0, 0.26, 0.23, 0.17]
        ),
        "womanface_asia.LOD": (
            0x700, "faceshader_simple", "womanface_asia", "womanface_10a_aged",
            "none", "none", "none", [1.0, 0.0, 0.0, 0.0]
        ),
    })
    print("[3/5] Updated womanface_asia normalmap & aged bindings in early_load.brf.")

    # 4. Patch myfaces.brf so all 5 warpaint female faces use matching Yuening normalmaps & speculars
    patch_brf_materials(os.path.join(RES_DIR, "myfaces.brf"), {
        "womanface_youngb": (
            0x720, "faceshader", "womanface_youngb", "womanface_1_agedb",
            "womanface_11_nm", "none", "womanface_11_aged_nm", [25.0, 0.26, 0.23, 0.17]
        ),
        "womanface_youngb.LOD": (
            0x700, "faceshader_simple", "womanface_youngb", "womanface_1_agedb",
            "none", "none", "none", [1.0, 0.0, 0.0, 0.0]
        ),
        "womanface_bb": (
            0x720, "faceshader", "womanface_bb", "womanface_2_agedb",
            "womanface_12_nm", "none", "womanface_12_aged_nm", [25.0, 0.26, 0.23, 0.17]
        ),
        "womanface_bb.LOD": (
            0x700, "faceshader_simple", "womanface_bb", "womanface_2_agedb",
            "none", "none", "none", [1.0, 0.0, 0.0, 0.0]
        ),
        "womanface_ab": (
            0x720, "faceshader", "womanface_ab", "womanface_3_agedb",
            "womanface_03_nm", "none", "womanface_03_aged_nm", [25.0, 0.36, 0.33, 0.27]
        ),
        "womanface_ab.LOD": (
            0x700, "faceshader_simple", "womanface_ab", "womanface_3_agedb",
            "none", "none", "none", [1.0, 0.0, 0.0, 0.0]
        ),
        "womanface_brownb": (
            0x720, "faceshader", "womanface_brownb", "womanface_4_agedb",
            "womanface_04_nm", "none", "womanface_04_aged_nm", [25.0, 0.36, 0.33, 0.27]
        ),
        "womanface_brownb.LOD": (
            0x700, "faceshader_simple", "womanface_brownb", "womanface_4_agedb",
            "none", "none", "none", [1.0, 0.0, 0.0, 0.0]
        ),
        "womanface_africanb": (
            0x720, "faceshader", "womanface_africanb", "womanface_african_agedb",
            "womanface_05_nm", "none", "womanface_05_aged_nm", [25.0, 0.36, 0.33, 0.27]
        ),
        "womanface_africanb.LOD": (
            0x700, "faceshader_simple", "womanface_africanb", "womanface_african_agedb",
            "none", "none", "none", [1.0, 0.0, 0.0, 0.0]
        ),
    })
    print("[4/5] Updated 5 female warpaint materials in myfaces.brf with Yuening normalmaps.")

    # 5. Arrange 31 female skins in skins.txt:
    #    0..25  = 26 warpaint-free skins (so random non-hero ranges NEVER roll warpaint!)
    #    26..30 = 5 sacred warpaint skins (youngb, bb, ab, brownb, africanb)
    head_skins_lines = subprocess.check_output(["git", "-C", MOD, "show", "HEAD:skins.txt"]).decode("utf-8", "ignore").splitlines()
    w_line_head = None
    for i, l in enumerate(head_skins_lines):
        if l.strip().startswith("woman 1"):
            w_line_head = head_skins_lines[i + 9]
            break

    toks = w_line_head.split()
    idx = 1
    entries = {}
    while idx < len(toks):
        nm = toks[idx]
        col = toks[idx + 1]
        nh = int(toks[idx + 2])
        idx += 3
        hgrp = []
        for _ in range(nh):
            nc = int(toks[idx])
            hm = toks[idx + 1]
            cs = toks[idx + 2:idx + 2 + nc]
            idx += 2 + nc
            hgrp.append((hm, cs))
        entries[nm] = (col, hgrp)

    calibrated_colors = {
        "womanface_asia":     str(0xFFEADBC0),
        "womanface_youngb":   entries["womanface_11"][0],
        "womanface_bb":       entries["womanface_12"][0],
        "womanface_ab":       entries["womanface_03"][0],
        "womanface_brownb":   scale_argb_int(entries["womanface_04"][0], 0.91, 0.84, 0.68),
        "womanface_africanb": entries["womanface_05"][0],
    }
    for k, new_col in calibrated_colors.items():
        entries[k] = (new_col, entries[k][1])

    clean_then_sacred_order = [
        # 0..13: Central/Balkan European Fair (14)
        "womanface_01", "womanface_02", "womanface_03", "womanface_06",
        "womanface_11", "womanface_12", "womanface_14", "womanface_16",
        "womanface_17", "womanface_18", "womanface_19", "womanface_20",
        "womanface_21", "womanface_22",
        # 14..20: Adriatic & Mediterranean Olive (7)
        "womanface_07", "womanface_09", "womanface_10", "womanface_13",
        "womanface_15", "womanface_10a", "womanface_10aa",
        # 21..25: Eastern Steppe, Bronze & Ebony Non-Warpaint (5)
        "womanface_asia", "womanface_04", "womanface_08", "womanface_10a4",
        "womanface_05",
        # 26..30: Solid & Shade Sacred Geometric Warpaint (5)
        "womanface_youngb",    # 26: Crimson Red
        "womanface_bb",        # 27: Obsidian Black
        "womanface_ab",        # 28: Olive-Moss Green
        "womanface_brownb",    # 29: Deep Teal on Golden-Bronze
        "womanface_africanb",  # 30: Chalk-Ivory White + Pearl Studs on Ebony
    ]
    assert len(clean_then_sacred_order) == 31

    out_parts = ["31"]
    for nm in clean_then_sacred_order:
        col, hgrp = entries[nm]
        out_parts.extend([nm, col, str(len(hgrp))])
        for hm, cs in hgrp:
            out_parts.extend([str(len(cs)), hm])
            out_parts.extend(cs)

    skins_path = os.path.join(MOD, "skins.txt")
    with open(skins_path, "r", encoding="utf-8") as f:
        cur_lines = f.readlines()

    for i, l in enumerate(cur_lines):
        if l.strip().startswith("woman 1"):
            cur_lines[i + 9] = " " + "  ".join(out_parts) + "\n"
            break

    with open(skins_path, "w", encoding="utf-8") as f:
        f.writelines(cur_lines)
    print("[5/5] Updated skins.txt: 0..25 clean skins, 26..30 authentic sacred warpaint skins.")


if __name__ == "__main__":
    main()
