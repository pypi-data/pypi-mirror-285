# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 即将废弃，建议使用zhousflib.image
import cv2
import numpy as np
from pathlib import Path

from zhousflib.decorator import interceptor_util


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


def max_connectivity_domain(mask_arr: np.array, connectivity=4) -> np.array:
    """
    返回掩码中最大的连通域
    :param mask_arr: 二维数组，掩码中0表示背景，1表示目标
    :param connectivity: 4|8 4邻接还是8邻接
    :return:
    """
    # 掩码标识转换
    arr_mask = np.where(mask_arr == 1, 255, 0)
    # 掩码类型转换
    arr_mask = arr_mask.astype(dtype=np.uint8)
    """
    connectivity：可选值为4或8，也就是使用4连通还是8连通
    num：所有连通域的数目
    labels：图像上每一像素的标记，用数字1、2、3…表示（不同的数字表示不同的连通域）
    stats：每一个标记的统计信息，是一个5列的矩阵，每一行对应每个连通区域的外接矩形的x、y、width、height和面积，示例：0 0 720 720 291805
    centroids：连通域的中心点
    """
    nums, labels, stats, centroids = cv2.connectedComponentsWithStats(arr_mask, connectivity=connectivity)
    background = 0
    for row in range(stats.shape[0]):
        if stats[row, :][0] == 0 and stats[row, :][1] == 0:
            background = row
    # 删除背景后的连通域列表
    stats_no_bg = np.delete(stats, background, axis=0)
    if len(stats_no_bg) == 0:
        return stats_no_bg
    # 获取连通域最大的索引
    max_idx = stats_no_bg[:, 4].argmax()
    max_region = np.where(labels == max_idx + 1, 1, 0)
    # 保存
    # cv2.imwrite(r'vis.jpg', max_region * 255)
    return max_region


def rotate(image, angle, show=False):
    """
    顺时针旋转图片
    :param image: 图片
    :param angle: 旋转角度
    :param show: 是否显示
    :return: np.array
    """
    if isinstance(image, str):
        image = cv2.imread(image)
    if isinstance(image, np.ndarray):
        # grab the dimensions of the image and then determine the
        # center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # perform the actual rotation and return the image
        rotated = cv2.warpAffine(image, M, (nW, nH))
        if show:
            cv2.imshow("{0} rotated".format(angle), rotated)
            cv2.waitKey(0)
        return rotated
    return None


def _read(chain):
    image, show = chain
    if isinstance(image, str):
        image = cv2.imread(image)
    if image is None:
        return True, image
    return False, (image, show)


def _show(chain):
    title, image, show = chain
    if show:
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return image


@interceptor_util.intercept(before=_read, after=_show)
def img_binary(chain):
    """ 二值化 """
    image, show = chain
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    block_size = 11  # 分割计算的区域大小，取奇数
    binary_ = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, 15)
    return "binary", binary_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_bilateral_filter(chain):
    """ 双边滤波 """
    image, show = chain
    bilateral_filter_ = cv2.bilateralFilter(image, 7, 75, 75)
    return "bilateral_filter", bilateral_filter_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_erosion(chain):
    """ 腐蚀 """
    image, show = chain
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    erosion_ = cv2.erode(image, kernel)
    return "erosion", erosion_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_dilate(chain):
    """ 膨胀 """
    image, show = chain
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    dilate_ = cv2.dilate(image, kernel)
    return "dilate", dilate_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_clahe(chain):
    """ 直方图均衡化 """
    image, show = chain
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(5, 5))
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l2 = clahe.apply(l)
    lab = cv2.merge((l2, a, b))
    clahe_ = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return "clahe", clahe_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_remove_background(chain):
    """ 去除背景 """
    image, show = chain
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    se = cv2.morphologyEx(se, cv2.MORPH_CLOSE, (2, 2))
    mask = cv2.dilate(binary, se)
    mask1 = cv2.bitwise_not(mask)
    binary = cv2.bitwise_and(image, mask)
    result = cv2.add(binary, mask1)
    return "remove_background", result, show


if __name__ == "__main__":
    image_file = r"C:\Users\zhousf-a\Desktop\0\07398c4c-efb238518a73537efa4b212fceaf7a6f_76_ero.jpg"
    image_file = cv2.imread(image_file, 0)
    # binary = img_binary(image_file, False)
    # dilate = img_dilate(binary, True)
    # erosion = img_erosion(dilate, True)
    # cv2.imwrite(r"C:\Users\zhousf-a\Desktop\0\3_vis_erosion.jpg", erosion)


