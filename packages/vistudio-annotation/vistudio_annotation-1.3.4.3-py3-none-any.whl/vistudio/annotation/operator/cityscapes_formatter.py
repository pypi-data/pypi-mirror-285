#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   imagenet_formatter.py
"""
import time
from typing import Union, Dict, Any
from pandas import DataFrame
import ray.data
import pandas as pd
from ray.data import Dataset, DataContext
from windmillcomputev1.filesystem import init_py_filesystem

from vistudio.annotation.datasource.image_datasource import CityscapesImageDatasource
from vistudio.annotation.util import string, polygon
import numpy as np

ctx = DataContext.get_current();
ctx.enable_tensor_extension_casting = False


class CityscapesFormatter(object):
    """
    CityscapesFormatter
    """

    def __init__(self,
                 labels: Union[Dict] = dict,
                 filesystem: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 user_id: str = None,
                 org_id: str = None,
                 tag: Union[Dict] = None
                 ):
        self._labels = labels
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.user_id = user_id
        self.org_id = org_id
        self._py_fs = init_py_filesystem(filesystem)
        self.tag = tag

    def _fill_image_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_image_info_vistudio
        :param row: dict
        :return: dict
        """
        row['file_uri'] = row['item']
        row['width'] = 0
        row['height'] = 0
        image_full_name = row['item'].split("/")[-1]
        image_name = image_full_name.rsplit('.', 1)[0].replace("_leftImg8bit", "", 1)
        row['image_name'] = image_name
        row['image_id'] = string.generate_md5(image_name)
        row['annotation_set_id'] = self.annotation_set_id
        row['annotation_set_name'] = self.annotation_set_name
        row['user_id'] = self.user_id
        row['org_id'] = self.org_id
        row['created_at'] = time.time_ns()
        row['data_type'] = 'Image'
        if self.tag is not None and len(self.tag) > 0:
            row['tags'] = self.tag
        return row

    @staticmethod
    def _filter_image_uri_fn(row: Dict[str, Any]) -> bool:
        image_uri = row['item']
        gtFine_suffix = ("_gtFine_color.png", "gtFine_instanceIds.png", "_gtFine_labelIds.png", ".txt")
        image_uri_suffix = ('.jpeg', '.jpg', '.png', '.bmp')
        if image_uri.endswith(gtFine_suffix):
            return False
        elif image_uri.endswith(image_uri_suffix):
            return True
        else:
            return False

    @staticmethod
    def _filter_annotation_image_uri_fn(row: Dict[str, Any]) -> bool:
        image_uri = row['item']
        if image_uri.endswith("_gtFine_labelIds.png"):
            return True
        else:
            return False

    def _fill_annotation_fn(self, row: Dict[str, Any], image_name_dict: dict()) -> Dict[str, Any]:
        image_name_prefix = row['image_name'].replace("_gtFine_labelIds.png", "")
        image_name = image_name_dict.get(image_name_prefix)
        if image_name is None:
            image_name = row['image_name'].replace("_gtFine_labelIds.png", ".png")
        print("image_name:{} image_name_dict:{}".format(image_name, image_name_dict))
        image_id = string.generate_md5(image_name_prefix)
        row['image_id'] = image_id
        row['user_id'] = self.user_id
        row['created_at'] = time.time_ns()
        row['data_type'] = 'Annotation'
        row['annotation_set_id'] = self.annotation_set_id
        row['task_kind'] = 'Manual'
        row['artifact_name'] = ''
        row['image_name'] = image_name_prefix

        annotations = []
        array = np.array(row['image'])
        unique_labels = np.unique(array)
        polygons = []

        for label_id in unique_labels:
            from PIL import Image
            if label_id == 0:  # 跳过背景
                continue
            # 将标签图像中当前标签的像素设置为255，其他像素设置为0
            mask = np.where(array == label_id, 255, 0).astype(np.uint8)
            # 使用PIL库的findContours方法找到对象的轮廓
            import cv2
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # contour_image = Image.fromarray(mask)
            # contours = contour_image.findContours(method=1, mode=1)

            # 提取多边形边界
            for contour in contours:
                # 将轮廓坐标转换为浮点数类型，并添加到列表中
                contour_2d = contour.squeeze(axis=1)
                flat_polygon = contour.flatten().astype(float).tolist()
                label = {
                    "id": str(label_id)
                }
                area = polygon.compute_polygon_area(contour_2d)
                bbox = polygon.polygon_to_bbox_cv2(contour_2d)
                annotation = {
                    "id": string.generate_random_digits(6),
                    "segmentation": flat_polygon,
                    "labels": [label],
                    "area": area,
                    "bbox": bbox
                }
                annotations.append(annotation)
                # annotations.append(list())
        import pyarrow as pa
        row['annotations'] = annotations

        return row

    @staticmethod
    def _parse_image_name_map(image_uris: list):
        filename_dict = {}
        for filename in image_uris:
            key = filename.replace("_leftImg8bit", "")
            filename_dict[key.split('.')[0]] = filename
        return filename_dict

    def to_vistudio_v1(self, ds: Dataset) -> Dict[str, Dataset]:
        """
        to_vistudio_v1
        :param ds:
        :return:
        """
        image_uri_ds = ds.filter(lambda x: self._filter_image_uri_fn(row=x))
        image_ds = image_uri_ds.map(lambda row: self._fill_image_info_vistudio(row=row)).drop_columns(cols=['item'])
        image_uris = image_ds.unique(column='image_name')
        annotation_image_uri_ds = ds.filter(lambda x: self._filter_annotation_image_uri_fn(row=x))
        annotation_image_uris = annotation_image_uri_ds.unique(column='item')
        image_name_dict = self._parse_image_name_map(image_uris)

        cityscapes_datasource = CityscapesImageDatasource(paths=annotation_image_uris, filesystem=self._py_fs)
        annotation_ds = ray.data.read_datasource(datasource=cityscapes_datasource) \
            .map(lambda row: self._fill_annotation_fn(row=row, image_name_dict=image_name_dict)) \
            .drop_columns(cols=['image'])

        df = annotation_ds.to_pandas()
        df['annotations'] = df['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        import pyarrow as pa
        annotation_ds = ray.data.from_arrow(pa.Table.from_pandas(df))

        return {"image_ds": image_ds, "annotation_ds": annotation_ds}
