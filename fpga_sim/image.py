"""
fpga 图像算法仿真
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    import os
    import sys

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    import functions
else:
    from .. import functions


def rgb_to_gray(img_rgb: np.ndarray) -> np.ndarray:
    """RGB 转 灰度图"""

    if not isinstance(img_rgb, np.ndarray):
        raise ValueError("Input must be a NumPy array")
    if img_rgb.ndim != 3:
        raise ValueError("Input image must be a 3-channel RGB image")
    if img_rgb.shape[2] != 3:
        raise ValueError("Input image must have 3 channels (RGB)")
    if img_rgb.dtype != np.uint8:
        raise ValueError("Input image must be of type uint8")

    r, g, b = cv2.split(img_rgb)

    r = r.astype(np.uint16)
    g = g.astype(np.uint16)
    b = b.astype(np.uint16)

    img_gray = (76 * r + 150 * g + 29 * b) >> 8
    img_gray = img_gray.astype(np.uint8)

    return img_gray


def __lut_bilateral_diff_to_weight(diff: int) -> int:
    """
    双边滤波中像素差值到权重的映射查找表

    基于高斯函数预先计算的权重查找表，用于加速双边滤波计算。
    输入为相邻像素的灰度差值，输出为对应的权重值（范围 0-1023）。
    权重曲线呈高斯分布：差值为 0 时权重最大（1023），随差值增大而递减。

    Args:
        diff (int): 像素灰度差值，预期范围 0-63

    Returns:
        int: 对应的权重值，范围 0-1023。差值越大权重越小，
             当差值>=58 时权重接近 0，差值>63 时返回 0
    """
    match diff:
        case 0:
            return 1023
        case 1:
            return 1021
        case 2:
            return 1015
        case 3:
            return 1006
        case 4:
            return 993
        case 5:
            return 976
        case 6:
            return 957
        case 7:
            return 934
        case 8:
            return 908
        case 9:
            return 880
        case 10:
            return 849
        case 11:
            return 817
        case 12:
            return 782
        case 13:
            return 747
        case 14:
            return 710
        case 15:
            return 673
        case 16:
            return 635
        case 17:
            return 597
        case 18:
            return 559
        case 19:
            return 522
        case 20:
            return 486
        case 21:
            return 450
        case 22:
            return 415
        case 23:
            return 382
        case 24:
            return 350
        case 25:
            return 319
        case 26:
            return 290
        case 27:
            return 263
        case 28:
            return 237
        case 29:
            return 214
        case 30:
            return 191
        case 31:
            return 171
        case 32:
            return 152
        case 33:
            return 135
        case 34:
            return 119
        case 35:
            return 104
        case 36:
            return 91
        case 37:
            return 80
        case 38:
            return 69
        case 39:
            return 60
        case 40:
            return 52
        case 41:
            return 45
        case 42:
            return 38
        case 43:
            return 33
        case 44:
            return 28
        case 45:
            return 24
        case 46:
            return 20
        case 47:
            return 17
        case 48:
            return 14
        case 49:
            return 12
        case 50:
            return 10
        case 51:
            return 8
        case 52:
            return 7
        case 53:
            return 5
        case 54:
            return 4
        case 55:
            return 4
        case 56:
            return 3
        case 57:
            return 2
        case 58:
            return 2
        case 59:
            return 2
        case 60:
            return 1
        case 61:
            return 1
        case 62:
            return 1
        case 63:
            return 1
        case _:
            return 0


def pixel_convolution(window: np.ndarray, kernel: np.ndarray):
    """
    对窗口内的像素值进行卷积计算，返回卷积结果。

    该函数将窗口内的像素值与对应位置的卷积核权重相乘并求和，
    用于实现图像滤波等操作。输入窗口和卷积核必须具有相同的形状。

    Args:
        window (np.ndarray): 输入像素窗口，形状为 (k, k)
        kernel (np.ndarray): 卷积核权重，形状为 (k, k)

    Returns:
        int: 卷积计算结果，范围取决于输入像素值和卷积核权重
    """
    if window.shape != kernel.shape:
        raise ValueError("Window and kernel must have the same shape")

    result = 0
    for i in range(window.shape[0]):
        for j in range(window.shape[1]):
            result += int(window[i, j]) * int(kernel[i, j])
    return result


def bilateral_filt(img_gray: np.ndarray) -> np.ndarray:
    """
    对灰度图像进行双边滤波。(FPGA 实现方案)
    """
    img_out = np.zeros_like(img_gray)
    for (row, col), window in functions.slide_square_window(img_gray, 5):
        kernel = np.array(
            [
                [29, 37, 40, 37, 29],
                [37, 47, 51, 47, 37],
                [40, 51, 55, 51, 40],
                [37, 47, 51, 47, 37],
                [29, 37, 40, 37, 29],
            ],
            dtype=np.uint16,
        )
        for i in range(5):
            for j in range(5):
                diff = abs(int(window[i][j]) - int(window[2][2]))
                weight = __lut_bilateral_diff_to_weight(diff)
                kernel[i, j] = (kernel[i, j] * weight)
        weight_sum = kernel.sum()
        if weight_sum == 0:
            weight_sum = 1
        img_out[row, col] = pixel_convolution(np.array(window, dtype=np.uint16), kernel) // weight_sum
    return img_out.astype(np.uint8)


if __name__ == "__main__":
    img_dir = str(R"C:\MARTIN\华南理工大学\集创赛\2026\plan\lisence_each_colour")
    img_paths: list = [
        os.path.join(img_dir, img_name) for img_name in os.listdir(img_dir)
    ]
    for img_path in img_paths:
        img_name = os.path.basename(img_path).split(".")[0]
        with open(
            img_path, "rb"
        ) as f:
            img_rgb = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
        img_gray = rgb_to_gray(img_rgb)
        img_filtered = bilateral_filt(img_gray)
        img_filtered_opencv = cv2.bilateralFilter(img_gray, 5, 75, 75)
        # print(type(img_gray), img_gray.shape, img_gray.dtype)
        # plt.figure(figsize=(5, 5))
        # plt.subplot(1, 3, 1)
        # plt.imshow(img_gray, cmap='gray')
        # plt.title("Grayscale Image")
        # plt.subplot(1, 3, 2)
        # plt.imshow(img_filtered, cmap='gray')
        # plt.title("Filtered Image")
        # plt.subplot(1, 3, 3)
        # plt.imshow(img_filtered_opencv, cmap='gray')
        # plt.title("OpenCV Filtered Image")
        # plt.show()

        # 存入 __pycache__ 以供后续测试使用
        np.save(os.path.join(os.path.dirname(__file__), "__pycache__", f"{img_name}_img_gray.npy"), img_gray)
        np.save(os.path.join(os.path.dirname(__file__), "__pycache__", f"{img_name}_img_filtered.npy"), img_filtered)
        np.save(os.path.join(os.path.dirname(__file__), "__pycache__", f"{img_name}_img_filtered_opencv.npy"), img_filtered_opencv)
