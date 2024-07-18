#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   imagenet_formatter.py
"""
import os.path
import time
from typing import Union, Dict, Any

import numpy as np
from pandas import DataFrame
import ray.data
import pandas as pd
from ray.data import DataContext, Dataset

from vistudio.annotation.util import string, polygon

ctx = DataContext.get_current()
ctx.enable_tensor_extension_casting = False


class CVATFormatter(object):
    """
    CVATFormatter
    """

    def __init__(self,
                 labels: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 user_id: str = None,
                 org_id: str = None,
                 data_uri: str = None,
                 tag: Union[Dict] = None
                 ):
        self._labels = labels
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.user_id = user_id
        self.org_id = org_id
        self.data_uri = data_uri
        self.label_name_id_map = self._get_label_name_id_map()
        self.tag = tag

    def _get_label_name_id_map(self):
        """
        _get_label_id_dict
        :return:
        """
        label_name_dict = dict()
        if self._labels is not None:
            for label_id, label_name in self._labels.items():
                label_name_dict[label_name] = label_id

        return label_name_dict

    def _fill_image_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_image_info_vistudio
        :param row: dict
        :return: dict
        """
        image_name = row['name']
        row['file_uri'] = os.path.join(self.data_uri, "images", image_name)
        row['width'] = 0
        row['height'] = 0
        row['image_name'] = image_name
        row['image_id'] = string.generate_md5(row['image_name'])
        row['annotation_set_id'] = self.annotation_set_id
        row['annotation_set_name'] = self.annotation_set_name
        row['user_id'] = self.user_id
        row['org_id'] = self.org_id
        row['created_at'] = time.time_ns()
        row['data_type'] = 'Image'
        if self.tag is not None and len(self.tag) > 0:
            row['tags'] = self.tag
        return row

    def _fill_annotation_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_annotation_info_vistudio
        :param row:
        :return:
        """
        image_name = row['name']
        row['image_id'] = string.generate_md5(image_name)
        row['user_id'] = self.user_id
        row['created_at'] = time.time_ns()
        row['data_type'] = 'Annotation'
        row['annotation_set_id'] = self.annotation_set_id
        row['task_kind'] = "Manual"
        row['artifact_name'] = ""

        annotations = list()
        annotations_cvat = row.get('annotations', [])
        if annotations_cvat is None or len(annotations_cvat) == 0:
            return row

        for annotation_cvat in annotations_cvat:
            box_cvat_dict = annotation_cvat.get("box", None)
            polygon_cvat_dict = annotation_cvat.get("polygon", None)
            mask_cvat = annotation_cvat.get("mask", None)
            polyline_cvat_dict = annotation_cvat.get("polyline", None)
            points = annotation_cvat.get("points", None)
            tag_dict = annotation_cvat.get("tag", None)
            if box_cvat_dict is not None:
                bbox = polygon.calculate_bbox(box_cvat_dict)
                seg = polygon.bbox_to_polygon(box_cvat_dict)
                area = polygon.compute_polygon_area(polygon.bbox_to_polygon_2d_array(box_cvat_dict))
                label_name = box_cvat_dict.get("label")
                label_id = self.label_name_id_map.get(label_name)
                label = {
                    "id": str(label_id)
                }
                md5_data = {"time": time.time_ns()}
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "area": area,
                    "segmentation": seg,
                    "bbox": bbox,
                    "labels": [label],

                })
            elif polygon_cvat_dict is not None:
                seg = polygon.convert_vertices_to_1d_array(polygon_cvat_dict.get('points', ''))
                polygon_2d = polygon.convert_vertices_to_2d_array(polygon_cvat_dict.get('points', ''))
                bbox = polygon.polygon_to_bbox_cv2(polygon_2d)
                area = polygon.compute_polygon_area(polygon_2d)
                label_name = polygon_cvat_dict.get("label")
                label_id = self.label_name_id_map.get(label_name)
                label = {
                    "id": str(label_id)
                }
                md5_data = {"time": time.time_ns()}
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "area": area,
                    "segmentation": seg,
                    "bbox": bbox,
                    "labels": [label],

                })

            elif mask_cvat is not None:
                rle_str = mask_cvat.get('rle', '')
                left = mask_cvat.get('left', '0')
                top = mask_cvat.get('top', '0')
                width = mask_cvat.get('width', '0')
                height = mask_cvat.get('height', '0')
                bbox = [int(left), int[top], int(width), int[height]]
                rle_list = [int(x.strip()) for x in rle_str.split(',')]
                size = [int(row['width']), int(row['height'])]
                bbox = [int]
                rle = {
                    "counts": rle_list,
                    'size': size
                }
                label_name = mask_cvat.get("label")
                label_id = self.label_name_id_map.get(label_name)
                label = {
                    "id": str(label_id)
                }
                md5_data = {"time": time.time_ns()}
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "bbox": bbox,
                    "labels": [label],
                    "rle": rle

                })
            elif polyline_cvat_dict is not None:
                seg = polygon.convert_vertices_to_1d_array(polyline_cvat_dict.get('points', ''))
                polyline_2d = polygon.convert_vertices_to_2d_array(polyline_cvat_dict.get('points', ''))
                bbox = polygon.polygon_to_bbox_cv2(polyline_2d)
                area = polygon.compute_polygon_area(polyline_2d)
                label_name = polyline_cvat_dict.get("label")
                label_id = self.label_name_id_map.get(label_name)
                label = {
                    "id": str(label_id)
                }
                md5_data = {"time": time.time_ns()}
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "area": area,
                    "segmentation": seg,
                    "bbox": bbox,
                    "labels": [label],

                })
            elif tag_dict is not None:
                label_name = tag_dict.get('label')
                label_id = self.label_name_id_map.get(label_name)
                label = {
                    "id": str(label_id)
                }
                md5_data = {"time": time.time_ns()}
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "labels": [label],

                })

        row['annotations'] = annotations
        return row

    def to_vistudio_v1(self, ds: Dataset) -> Dict[str, Dataset]:
        """
        to_vistudio_v1
        :param ds:
        :return:
        """
        image_info_ds = ds.flat_map(lambda row: row['images'])
        image_ds = image_info_ds.map(lambda row: self._fill_image_info_vistudio(row=row)) \
            .drop_columns(cols=['annotations', 'id', 'name'])
        annotation_ds = image_info_ds.map(lambda row: self._fill_annotation_info_vistudio(row=row)) \
            .drop_columns(cols=['id', 'name'])
        return {"image_ds": image_ds, "annotation_ds": annotation_ds}
