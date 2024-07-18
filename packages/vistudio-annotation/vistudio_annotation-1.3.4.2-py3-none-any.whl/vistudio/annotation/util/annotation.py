#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   annotation.py
"""
from typing import List, Union, Iterator, Dict, Tuple
import numpy as np
import sys


def polygon_area(polygon: List[float]) -> float:
    """
    计算polygon的面积
    """
    x, y = np.array(polygon[::2]), np.array(polygon[1::2])
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def rle_area(rle):
    """
    计算rle的面积
    """
    area = 0
    for i in range(1, len(rle), 2):
        area += rle[i]
    return area


def rle2mask(height, width, rle, gray=255):
    """
    Args:
        -rle: numpy array, 连续0或1的个数， 从0开始
        -height: 图片height
        -width: 图片width
    Returns:
        -mask: rle对应的mask
    """
    mask = np.zeros(height * width).astype(np.uint8)
    start = 0
    pixel = 0
    for num in rle:
        stop = start + num
        mask[start:stop] = pixel
        pixel = gray - pixel
        start = stop
    return mask.reshape(height, width)


def mask2rle(img):
    '''
    Args:
        -img: numpy array, 1 - mask, 0 - background, mask位置的值可以不是1，但必须完全相同
    Returns:
        -rle.txt
    该函数返回单个图片的标注信息，所有的标注视为整体，因此适用于单个标注的图片
    例如: img  1 0 0 1 1 1 0      rle.txt 0 1 2 3 1
    '''
    pixels = img.flatten()
    pixels = np.concatenate([[0], pixels, [0]])
    # 获取像素变化的坐标
    runs = np.where(pixels[1:] != pixels[:-1])[0]
    # 计算0 1 连续出现的数量
    runs = np.concatenate([[0], runs, [pixels.shape[0] - 2]])
    runs[1:] -= runs[:-1]
    # 如果最后一位为0， 去除
    if runs[-1] == 0:
        runs = runs[:-1]
    return runs[1:].tolist()


def polygon_bbox_with_wh(polygon):
    """
    获取polygon的外接框。
    params:  polygon: 多边形。
    return:  bbox: 边界框 x, y, w, h
    """
    ymin, ymax, xmin, xmax = polygon_bbox(polygon)
    return xmin, ymin, xmax - xmin, ymax - ymin


def polygon_bbox(polygon):
    """
    获取polygon的外接框
    """
    xmin, ymin = sys.maxsize, sys.maxsize
    xmax, ymax = 0, 0
    for i in range(0, len(polygon), 2):
        x, y = int(polygon[i]), int(polygon[i + 1])
        xmin = min(xmin, x)
        xmax = max(xmax, x)
        ymin = min(ymin, y)
        ymax = max(ymax, y)
    return ymin, ymax, xmin, xmax


def bbox_overlaps(bboxes1, bboxes2, mode='iou'):
    """Calculate the ious between each bbox of bboxes1 and bboxes2.

    Args:
        bboxes1(ndarray): shape (n, 4)
        bboxes2(ndarray): shape (k, 4)
        mode(str): iou (intersection over union) or iof (intersection
            over foreground)

    Returns:
        ious(ndarray): shape (n, k)
    """

    assert mode in ['iou', 'iof']

    bboxes1 = bboxes1.astype(np.float32)
    bboxes2 = bboxes2.astype(np.float32)
    rows = bboxes1.shape[0]
    cols = bboxes2.shape[0]
    ious = np.zeros((rows, cols), dtype=np.float32)
    if rows * cols == 0:
        return ious
    exchange = False
    if bboxes1.shape[0] > bboxes2.shape[0]:
        bboxes1, bboxes2 = bboxes2, bboxes1
        ious = np.zeros((cols, rows), dtype=np.float32)
        exchange = True
    area1 = (bboxes1[:, 2] - bboxes1[:, 0] + 1) * (
            bboxes1[:, 3] - bboxes1[:, 1] + 1)
    area2 = (bboxes2[:, 2] - bboxes2[:, 0] + 1) * (
            bboxes2[:, 3] - bboxes2[:, 1] + 1)
    for i in range(bboxes1.shape[0]):
        x_start = np.maximum(bboxes1[i, 0], bboxes2[:, 0])
        y_start = np.maximum(bboxes1[i, 1], bboxes2[:, 1])
        x_end = np.minimum(bboxes1[i, 2], bboxes2[:, 2])
        y_end = np.minimum(bboxes1[i, 3], bboxes2[:, 3])
        overlap = np.maximum(x_end - x_start + 1, 0) * np.maximum(
            y_end - y_start + 1, 0)
        if mode == 'iou':
            union = area1[i] + area2 - overlap
        else:
            union = area2 if not exchange else area1[i]
        ious[i, :] = overlap / union
    if exchange:
        ious = ious.T
    return ious
