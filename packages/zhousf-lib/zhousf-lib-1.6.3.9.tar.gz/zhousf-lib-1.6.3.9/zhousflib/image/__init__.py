# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
import cv2
import numpy as np
from pathlib import Path

"""
图像的高频信息、低频信息
低频信息：代表着图像中亮度/灰度值/颜色变化很缓慢的区域，描述了图像的主要部分，是对整幅图像强度的综合度量
高频信息：对应着图像变化剧烈的部分，也就是图像的边缘/轮廓、噪声以及细节部分，主要是对图像边缘/轮廓的度量，而人眼对高频分量比较敏感
"""


def read(img_path: Path):
    """
    读图片-兼容图片路径包含中文
    :param img_path:
    :return: np.ndarray
    """
    if isinstance(img_path, str):
        img_path = Path(img_path)
    if isinstance(img_path, Path):
        img_path = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    return img_path


def write(image: np.ndarray, img_write_path: Path):
    """
    写图片-兼容图片路径包含中文
    :param image:
    :param img_write_path:
    :return:
    """
    cv2.imencode(img_write_path.suffix, image[:, :, ::-1])[1].tofile(str(img_write_path))

