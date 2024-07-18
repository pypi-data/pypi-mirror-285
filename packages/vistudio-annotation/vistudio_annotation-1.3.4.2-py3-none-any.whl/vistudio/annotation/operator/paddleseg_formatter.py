#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   paddleseg_formatter.py
"""

from typing import Union, Dict, Any, List
from pandas import DataFrame
import ray.data
from ray.data.preprocessor import Preprocessor
import numpy as np
import os
import logit
import pandas as pd
from windmillcomputev1.filesystem import init_py_filesystem

from vistudio.annotation.config.config import Config
from vistudio.annotation.datasink.filename_provider import MultiFilenameProvider
from vistudio.annotation.util import file
import pycocotools.mask as mask_utils


logit.base_logger.setup_logger({})


class PaddleSegFormatter(object):
    """
    PaddleSegFormatter
    """

    def __init__(self,
                 filesystem: Union[Dict] = dict,
                 labels: Union[Dict] = dict,
                 location: str = None,
                 merge_labels: Union[Dict] = None,
                 ):

        self._labels = labels
        self._filesystem = filesystem
        self._py_fs = init_py_filesystem(filesystem)
        self.merge_labels = merge_labels
        self.location = location

    def _get_label_id_map(self):
        label_id_dict = dict()
        if self._labels is not None:
            for label_id, label_name in self._labels.items():
                label_index = len(label_id_dict) + 1
                label_id_dict[label_id] = label_index
        return label_id_dict

    @staticmethod
    def _rle2mask(height, width, rle, gray=255):
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

    def mask_bg_from_vistudio_v1(self, source: DataFrame):
        """
        mask_bg_from_vistudio_v1
        :param source:
        :return:
        """
        height = source['height'][0]
        width = source['width'][0]
        image_mask = np.zeros(shape=(height, width), dtype=np.uint8)
        return image_mask
    def mask_from_vistudio_v1(self, source: DataFrame):
        """
        Convert annotations from Vistudio to Mask.
        """
        height = source['height'][0]
        width = source['width'][0]
        annotations = source['annotations'][0]
        label_id_dict = self._get_label_id_map()
        image_mask = np.zeros(shape=(height, width), dtype=np.uint8)
        for annotation in annotations:
            points = annotation.get('segmentation', [])

            labels = annotation['labels']
            for label in labels:
                label_id = label['id']
                if self.merge_labels is not None and label_id in self.merge_labels:
                    label_id = self.merge_labels[label_id]
                label_index = label_id_dict.get(str(label_id))
                if label_index is None:
                    logit.warning("label_id: {} not found".format(label_id))
                    print("label_id: {} not found".format(label_id))
                    continue
                rle = annotation.get('rle', None)
                if rle is not None:
                    # rle_obj = mask_utils.frPyObjects(rle, height, height)
                    # mask = mask_utils.decode(rle_obj)

                    rle_counts = rle.get('counts', None)
                    mask = self._rle2mask(height=height, width=width, rle=rle_counts,
                                                    gray=label_index)
                    index = mask == label_index
                    image_mask[index] = mask[index]
                else:
                    polygon = annotation.get('segmentation', [])
                    if len(polygon) < 6:
                        continue
                    polygon_obj = mask_utils.frPyObjects([polygon], height, width)
                    mask = mask_utils.decode(mask_utils.merge(polygon_obj))
                    index = mask == 1
                    image_mask[index] = label_index



        return image_mask

    def images_from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        images_from_vistudio_v1
        :param source:
        :return:
        """
        images = list()
        for source_index, source_row in source.iterrows():
            file_uri = source_row['file_uri']
            annotations_total = source_row.get('annotations')
            print("file_uri======{},annotations_total====={}".format(file_uri, annotations_total))
            if annotations_total is None:
                continue
            if len(annotations_total) == 0:
                mask_data = {
                    "height": source_row['height'],
                    "width": source_row['width'],
                }
                mask = self.mask_bg_from_vistudio_v1(source=pd.DataFrame([mask_data]))
                png_file_name = file.change_file_ext(file_name=os.path.basename(file_uri), file_ext=".png")
                image_data = {"image": mask, "file_name": png_file_name}
                images.append(image_data)
                
            for image_annotation in annotations_total:
                task_kind = image_annotation['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = image_annotation['annotations']
                if annotations is None or len(annotations) == 0:
                    continue

                mask_data = {
                    "height": source_row['height'],
                    "width": source_row['width'],
                    "annotations": [annotations]
                }
                mask = self.mask_from_vistudio_v1(source=pd.DataFrame(mask_data))
                png_file_name = file.change_file_ext(file_name=os.path.basename(file_uri), file_ext=".png")
                image_data = {"image": mask, "file_name": png_file_name}
                images.append(image_data)

        return pd.DataFrame(images)

    def labels_from_vistudio_v1(self, source: DataFrame) -> DataFrame():
        """
        labels_from_vistudio_v1
        :param source:
        :return:
        """
        labels = []
        for source_index, source_row in source.iterrows():
            file_uri = source_row['file_uri']
            png_file_name = file.change_file_ext(file_name=os.path.basename(file_uri), file_ext=".png")
            item_value = '{} {}'.format(file_uri, "labels/" + png_file_name)
            item = {"item": item_value}
            labels.append(item)

        return pd.DataFrame(labels)

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source:
        :param merge_labels:
        :param location:
        :return:
        """
        image_df = self.images_from_vistudio_v1(source=source)
        ds = ray.data.from_pandas(image_df)

        filename_provider = MultiFilenameProvider(is_full_file_name=False)
        logit.info("paddleseg formatter.upload mask.location={}".format(self.location))
        #self._py_fs.create_dir(self.location + "/labels/")
        if ds.count() > 0:
            ds.write_images(path=self.location + "/labels/",
                            filesystem=self._py_fs,
                            column="image",
                            filename_provider=filename_provider)

        return self.labels_from_vistudio_v1(source=source)

    def merge(self, rows: DataFrame) -> DataFrame:
        """
        merge
        :param rows:  DataFrame
        :return: DataFrame
        """
        item_list = rows['item'].to_list()
        return pd.DataFrame(item_list)
