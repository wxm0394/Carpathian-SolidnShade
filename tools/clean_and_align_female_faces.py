import os, sys
from PIL import Image, ImageFilter
import numpy as np

MOD_DIR = "/home/wxm/GOG Games/Mount Blade Warband/game/Modules/Carpathian Solid & Shade"
TEX_DIR = os.path.join(MOD_DIR, "Textures")

# Reference target: womanface_01 (The gold standard perfect face)
REF_PATH = os.path.join(TEX_DIR, "womanface_01.dds")

def purge_chin_artifacts(img):
    """
    Cleans up red lip spills and fake tongue artifacts below the lower lip.
    Ensures mouth is strictly confined to Y in [330, 368] (for 512x512).
    In Y >= 372, any rouge or red lip pigment is smoothly replaced with natural skin tone.
    """
    w, h = img.size
    orig_mode = img.mode
    im = img.convert("RGBA")
    arr = np.array(im, dtype=np.float32)

    scale_y = h / 512.0
    scale_x = w / 512.0

    # Lip bottom line is at Y = 368
    y_lip_end = int(368 * scale_y)
    y_chin_start = int(372 * scale_y)
    y_chin_end = int(420 * scale_y)

    x_left = int(200 * scale_x)
    x_right = int(312 * scale_x)

    # Sample natural chin skin tone from lateral boundaries (x: 180..200 and 312..332, y: 375..410)
    left_sample = arr[y_chin_start:y_chin_end, int(180*scale_x):int(205*scale_x), :3]
    right_sample = arr[y_chin_start:y_chin_end, int(305*scale_x):int(330*scale_x), :3]
    
    mean_skin = (np.mean(left_sample, axis=(0, 1)) + np.mean(right_sample, axis=(0, 1))) / 2.0

    # Purge central chin region
    for y in range(y_lip_end, min(h, y_chin_end + int(10*scale_y))):
        weight = np.clip((y - y_lip_end) / max(1, (y_chin_start - y_lip_end + int(6*scale_y))), 0.0, 1.0)
        for x in range(x_left, x_right):
            # Check if pixel has abnormal red tone: R > (G+B)/2 + 25
            r, g, b = arr[y, x, 0], arr[y, x, 1], arr[y, x, 2]
            redness = r - (g + b) / 2.0
            if redness > 25.0:
                # Lip pigment spill onto chin! Smoothly blend with pure skin tone
                target_r = mean_skin[0]
                target_g = mean_skin[1]
                target_b = mean_skin[2]
                arr[y, x, 0] = r * (1.0 - weight) + target_r * weight
                arr[y, x, 1] = g * (1.0 - weight) + target_g * weight
                arr[y, x, 2] = b * (1.0 - weight) + target_b * weight

    res = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    return res

def process_all_faces():
    # Target faces that showed deformation or warpaint chin spills
    problem_faces = [
        "womanface_04", "womanface_08", "womanface_03", "womanface_05", "womanface_10a4",
        "womanface_10a", "womanface_10aa", "womanface_asia",
        "womanface_youngb", "womanface_bb", "womanface_ab", "womanface_brownb", "womanface_africanb",
        "womanface_b_gaolu", "womanface_c_gaolu", "womanface_a_gaolu",
        "womanface_brown_gaolu", "womanface_african_gaolu", "womanface_young_gaolu",
        "womanface_1_agedb", "womanface_2_agedb", "womanface_3_agedb", "womanface_4_agedb"
    ]

    for name in problem_faces:
        dds_path = os.path.join(TEX_DIR, name + ".dds")
        if os.path.exists(dds_path):
            try:
                im = Image.open(dds_path)
                cleaned = purge_chin_artifacts(im)
                cleaned.save(dds_path)
                print(f"Purged chin rouge artifact on: {name}.dds")
            except Exception as e:
                print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    process_all_faces()
