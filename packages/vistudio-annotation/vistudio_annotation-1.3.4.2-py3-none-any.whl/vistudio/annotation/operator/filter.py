#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   filter.py
"""

from typing import Union, Dict, Any, List
from pandas import DataFrame
import pandas as pd


class Filter(object):
    """
    Filter Operator
    """

    def __init__(self, labels: Union[Dict] = dict):
        self.labels = labels

    @staticmethod
    def _filter_image_fn(row: Dict[str, Any], existed_images: set()) -> bool:
        """
        _filter_image_fn
        :param row:
        :param existed_images:
        :return:
        """
        if row['data_type'] == 'Annotation':
            return True
        elif row['data_type'] == 'Image':
            return row['image_id'] not in existed_images

    @staticmethod
    def _filter_annotation_fn(row: Dict[str, Any], existed_annotations: set()):
        """
        _filter_annotation_fn
        :param row:
        :param existed_annotations:
        :return:
        """
        if row['data_type'] == 'Image':
            return True
        elif row['data_type'] == 'Annotation':
            return row['image_id'] not in existed_annotations

    def filter_annotation_df(self, source: DataFrame, existed_annotations: set()) -> DataFrame:
        """
        filter ds not in filter_list
        :param source:
        :param existed_annotations:
        :return:
        """
        if existed_annotations is None or len(existed_annotations) == 0:
            return source

        anno_filtered_df = source[(~source['image_id'].isin(existed_annotations))]
        return anno_filtered_df

    def filter_image(self, source: "Dataset", existed_images: set()) -> "Dataset":
        """
        filter ds not in filter_list
        :param source:
        :param col:
        :param filter_list:
        :return:
        """
        if existed_images is None or len(existed_images) == 0:
            return source

        return source.filter(lambda x: self._filter_image_fn(row=x, existed_images=existed_images))

    def filter_annotation(self, source: "Dataset", existed_annotations: set()) -> "Dataset":
        """
        filter ds not in filter_list
        :param source:
        :param existed_annotations:
        :return:
        """
        if existed_annotations is None or len(existed_annotations) == 0:
            return source

        return source.filter(lambda x: self._filter_annotation_fn(row=x, existed_annotations=existed_annotations))

    def drop_duplicates(self, source: DataFrame, cols: List[str], inplace: bool = False) -> DataFrame:
        """
        drop duplicate rows by cols
        :param source:
        :param cols:
        :return:
        """
        return source.drop_duplicates(subset=cols, inplace=inplace)

    def check_labels(self, source: "Dataset") -> "Dataset":
        """
        check_labels
        :param source:
        :return:
        """
        labels_reverse = {v: int(k) for k, v in self.labels.items()}
        cate_ds = source.flat_map(lambda row: row["categories"])
        filter_label_ds = cate_ds.filter(lambda row: row["name"] not in labels_reverse)
        return filter_label_ds
