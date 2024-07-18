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

from vistudio.annotation.util import string


class PaddleClasFormatter(object):
    """
    ImageNetFormatter
    """

    def __init__(self,
                 labels: Union[Dict] = dict,
                 merge_labels: Union[Dict] = None,
                 ):
        self._labels = labels
        self.merge_labels = merge_labels

    def _get_label_id_map(self):
        """
        _get_label_id_dict
        :return:
        """
        label_id_dict = dict()
        if self._labels is not None:
            for label_id, label_name in self._labels.items():
                label_id_dict[label_id] = len(label_id_dict)

        return label_id_dict

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source: DataFrame
        :return: DataFrame
        """
        label_id_dict = self._get_label_id_map()
        annotation_list = list()
        for source_index, source_row in source.iterrows():
            annotations_total = source_row.get('annotations')
            if annotations_total is None or len(annotations_total) == 0:
                continue
            file_name = source_row['file_uri']
            for image_annotation in annotations_total:
                task_kind = image_annotation['task_kind']
                if task_kind != "Manual":
                    continue
                annotations = image_annotation['annotations']
                if annotations is None or len(annotations) == 0:
                    continue
                for annotation in annotations:
                    labels = annotation['labels']
                    for label in labels:
                        label_id = label['id']
                        if self.merge_labels is not None and label_id in self.merge_labels:
                            label_id = self.merge_labels[label_id]
                        if label_id_dict.get(str(label_id)) is not None:
                            annotation_list.append(("{} {}").format(file_name, label_id_dict.get(str(label_id))))
        item = {"item": annotation_list}
        return pd.DataFrame(item)

    def merge(self, rows: DataFrame) -> DataFrame:
        """
        merge
        :param rows: DataFrame
        :return: DataFrame
        """
        item_list = rows['item'].to_list()
        return pd.DataFrame(item_list)

