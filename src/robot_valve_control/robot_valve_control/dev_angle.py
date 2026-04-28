import cv2
import numpy as np
import math
import cmath
import os
from glob import glob

# ======================
# 参数：输入输出文件夹
# ======================
INPUT_DIR = "D:\\Users\\weistbrook\\Desktop\\is_properdataset\\images\\train"      # TODO: 改成你的原始图片文件夹
OUTPUT_DIR = "D:\\Users\\weistbrook\\Desktop\\is_properdataset\\images\\train_detect"    # TODO: 改成你想保存结果的文件夹
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ======================
# 阀门颜色分割：提取蓝色区域
# 返回mask: uint8, 阀门=255, 背景=0
# ======================
def valve_mask(bgr_img):
    hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

    # 这个颜色范围是根据你这个亮蓝色阀门估的，如果你发现有漏，可以稍微放宽
    lower = np.array([80, 80, 80], dtype=np.uint8)
    upper = np.array([140, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower, upper)

    # 闭运算把小裂缝/反光洞补一补，让形状更连续
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

# ======================
# 求阀门的主方向角（度数）
# 思想：
#   - 找到阀门中心
#   - 只看中心附近一圈（大概辐条粗的那一段半径）
#   - 对这一圈里每个白色像素，算它相对中心的极角theta
#   - 因为四条辐条每90°重复，我们把角度theta*4之后平均，
#     再除回4，得到整体的“十字朝向”
#
# 返回 angle_deg: [0,180) 内的角度，单位度
# ======================
def dominant_cross_angle(mask):
    binmask = (mask > 0).astype(np.uint8)
    M = cv2.moments(binmask)

    if M["m00"] == 0:
        raise ValueError("Mask seems empty (no valve detected).")

    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]

    ys, xs = np.nonzero(binmask)
    dx = xs - cx
    dy = ys - cy
    r = np.sqrt(dx * dx + dy * dy)

    rmax = r.max()

    # 选一段半径区间，只保留辐条部分，排除最里方孔和最外圈边框
    r_inner = 0.30 * rmax
    r_outer = 0.65 * rmax
    sel = (r > r_inner) & (r < r_outer)

    dx_sel = dx[sel]
    dy_sel = dy[sel]

    if len(dx_sel) == 0:
        raise ValueError("Not enough pixels in the spoke ring region.")

    theta = np.arctan2(dy_sel, dx_sel)  # [-pi, pi)

    # 四重对称 -> 乘4，把四个辐条折叠到同一方向
    complex_vec = np.exp(1j * 4 * theta).mean()

    # 平均相位 /4 回到原角度
    base_angle_rad = 0.25 * cmath.phase(complex_vec)
    angle_deg = base_angle_rad * 180.0 / math.pi

    # 归一化到 [0,180)
    angle_deg = (angle_deg + 180.0) % 180.0

    return angle_deg, (cx, cy)

# ======================
# 根据主方向角，算相对于“完美正”姿态的偏移角
#
# 定义“完美正”：
#   辐条正好落在水平/竖直方向，也就是 0°, 90°, 180°, 270°。
#
# dominant_cross_angle() 给的是整体旋转角（mod 180），
#   完美正时应该是 ~0°（或 ~90°，但90°其实等价于旋转了90度的同一个十字）。
#
# 我们想要一个最小旋转，把图转回到最近的正位。
# 做法：
#   diff = angle_deg
#   如果 diff > 90，则减 180
#   再把范围压进 [-90,90)
#   然后再决定是否更接近0还是90:
#       计算到0度的距离 d0 = diff
#       计算到90度的距离 d90 = diff-90 (或 diff+90 如果那更近)
#   但其实更简单的就是把dominant角度拉到 [-45,45)：
#       offset = angle_deg
#       while offset >= 90: offset -= 90
#       while offset <   0: offset += 90
#       if offset >= 45: offset -= 90
#
# 这样得到的 offset 是 [-45,45)，
# 表示“这张图相对于最近的正/竖方向还差多少度”，
# 负值≈逆时针，正值≈顺时针。
# ======================
def angle_offset_from_upright(angle_deg):
    offset = angle_deg

    # 压到 [0,90)
    while offset >= 90.0:
        offset -= 90.0
    while offset < 0.0:
        offset += 90.0

    # 变成 [-45,45)
    if offset >= 45.0:
        offset -= 90.0

    return offset  # 例如 -17.3 表示逆时针17.3度

# ======================
# 在图上画出角度并保存
# ======================
def annotate_and_save(img_bgr, angle_offset_deg, out_path, center=None, line_len_ratio=0.3, draw_line=True):
    out_img = img_bgr.copy()

    # 文本框
    text = f"{angle_offset_deg:.2f} deg"
    cv2.putText(
        out_img,
        text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 0, 255),  # 红字
        3,
        cv2.LINE_AA
    )

    # 画一个指示线：展示主方向（可选）
    if draw_line and center is not None:
        cx, cy = center
        h, w = out_img.shape[:2]

        # 从 offset 推出“当前主方向”(= offset相对水平轴)
        # 注意：我们这里用 offset+最近的正位=0来表示主辐条方向
        # 其实 dominant_cross_angle() 的原始角度 angle_deg 更直接
        # 所以这里我们重新画 angle_deg 的方向更直观:
        # 让线朝向 angle_deg 的方向（水平右边为0°,逆时针为+）。
        # 先把主方向角拿出来:
        # 我们无法直接拿到 angle_deg 这里，所以这段需要 angle_deg。
        # 解决：我们就不画方向线也可以。如果你要画，就让函数也传 angle_deg 进来。
        pass

    cv2.imwrite(out_path, out_img)

# ======================
# 主流程：
# 1. 遍历文件夹里的所有图片
# 2. 计算角度偏移
# 3. 画文字并另存
# ======================
def process_folder(input_dir, output_dir):
    # 支持的图片后缀
    exts = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff"]
    files = []
    for ext in exts:
        files.extend(glob(os.path.join(input_dir, ext)))

    if not files:
        print("No images found in", input_dir)

    for path in files:
        img = cv2.imread(path)
        if img is None:
            print(f"[WARN] Cannot read {path}, skipped.")
            continue

        try:
            mask = valve_mask(img)
            angle_deg, center = dominant_cross_angle(mask)
            offset_deg = angle_offset_from_upright(angle_deg)

            # 输出文件名
            base = os.path.basename(path)
            out_path = os.path.join(output_dir, base)

            annotate_and_save(img, offset_deg, out_path, center=center, draw_line=False)

            print(f"[OK] {base}: angle={angle_deg:.2f} deg, offset={offset_deg:.2f} deg")

        except Exception as e:
            print(f"[ERR] {path}: {e}")

# 运行
if __name__ == "__main__":
    process_folder(INPUT_DIR, OUTPUT_DIR)
