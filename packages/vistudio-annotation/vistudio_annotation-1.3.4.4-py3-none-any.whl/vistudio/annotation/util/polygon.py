#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
polygon.py
"""

import numpy as np
import cv2


def compute_polygon_area(points):
    """
    # 计算任意多边形的面积，顶点按照顺时针或者逆时针方向排列
    :param points:
    :return:
    """
    point_num = len(points)
    if (point_num < 3): return 0.0
    s = points[0][1] * (points[point_num - 1][0] - points[1][0])
    for i in range(1, point_num):
        s += points[i][1] * (points[i - 1][0] - points[(i + 1) % point_num][0])
    return abs(s / 2.0)


def convert_vertices_to_1d_array(vertices_str):
    """
    将表示多边形顶点的字符串转换为一维数组
    :param vertices_str: 表示顶点的字符串，格式为 "x1,y1;x2,y2;...;xn,yn"
    :return: 包含所有顶点坐标的一维数组
    """
    # 拆分成单个顶点对
    vertex_pairs = vertices_str.split(';')

    # 初始化一维数组
    vertices = []

    # 处理每个顶点对
    for pair in vertex_pairs:
        x, y = pair.split(',')
        vertices.append(float(x))
        vertices.append(float(y))

    return vertices


def convert_vertices_to_2d_array(vertices_str):
    """
    将表示多边形顶点的字符串转换为二维数组
    :param vertices_str: 表示顶点的字符串，格式为 "x1,y1;x2,y2;...;xn,yn"
    :return: 包含所有顶点坐标的二维数组
    """
    # 拆分成单个顶点对
    vertex_pairs = vertices_str.split(';')

    # 初始化二维数组
    vertices = []

    # 处理每个顶点对
    for pair in vertex_pairs:
        x, y = pair.split(',')
        vertices.append([float(x), float(y)])

    return vertices


def calculate_bbox(bbox_dict):
    """
    计算并返回边界框的各种表示方式
    :param bbox_dict: 包含边界框信息的字典
    :return: 边界框的四个角坐标和宽高
    """
    # 提取字符串形式的坐标，并转换为浮点数
    xtl = float(bbox_dict['xtl'])
    ytl = float(bbox_dict['ytl'])
    xbr = float(bbox_dict['xbr'])
    ybr = float(bbox_dict['ybr'])

    # 计算宽度和高度
    width = xbr - xtl
    height = ybr - ytl

    return [xtl, ytl, width, height]


def bbox_to_polygon(bbox_dict):
    """
    将边界框转换为多边形（四边形）
    :param bbox_dict: 包含边界框信息的字典
    :return: 多边形的顶点列表
    """
    # 提取字符串形式的坐标，并转换为浮点数
    xtl = float(bbox_dict['xtl'])
    ytl = float(bbox_dict['ytl'])
    xbr = float(bbox_dict['xbr'])
    ybr = float(bbox_dict['ybr'])

    # 构造多边形的四个顶点
    polygon = [xtl, ytl, xbr, ytl, xbr, ybr, xtl, ybr]

    return polygon


def bbox_to_polygon_2d_array(bbox_dict):
    """
    将边界框转换为多边形（四边形），并表示为二维数组
    :param bbox_dict: 包含边界框信息的字典
    :return: 多边形的二维数组
    """
    # 提取字符串形式的坐标，并转换为浮点数
    xtl = float(bbox_dict['xtl'])
    ytl = float(bbox_dict['ytl'])
    xbr = float(bbox_dict['xbr'])
    ybr = float(bbox_dict['ybr'])

    # 构造多边形的四个顶点，作为二维数组
    polygon = [
        [xtl, ytl],  # 左上角
        [xbr, ytl],  # 右上角
        [xbr, ybr],  # 右下角
        [xtl, ybr]  # 左下角
    ]

    return polygon


def polygon_to_bbox_cv2(polygon):
    """
    根据多边形的顶点使用 OpenCV 计算边界框
    :param polygon: 多边形顶点的二维数组，格式为 [[x1, y1], [x2, y2], ..., [xn, yn]]
    :return: 包含边界框信息的字典，格式为 {'xtl': xtl, 'ytl': ytl, 'xbr': xbr, 'ybr': ybr}
    """
    # 将多边形顶点转换为 NumPy 数组，并转换为整数类型（OpenCV 需要整数坐标）

    points = np.array(polygon, dtype=np.float32)

    # 计算边界框
    x, y, w, h = cv2.boundingRect(points)

    return [x, y, w, h]
