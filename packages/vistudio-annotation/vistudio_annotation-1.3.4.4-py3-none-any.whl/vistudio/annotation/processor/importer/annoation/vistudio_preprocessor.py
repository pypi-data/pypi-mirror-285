#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   formater.py
"""
from typing import Union, Dict, Any, List

import bcelogger
from ray.data.preprocessor import Preprocessor
from ray.data import Dataset
import ray

from windmilltrainingv1.client.training_client import TrainingClient

from vistudio.annotation.config.config import Config
from vistudio.annotation.datasource.sharded_mongo_datasource import get_mongo_collection, _get_exist_images, \
    _get_exist_annoation
from vistudio.annotation.operator.filter import Filter
from vistudio.annotation.operator.vistudio_formatter import VistudioFormatter

image_extensions = ('.jpeg', '.jpg', '.png', '.bmp')
time_pattern = "%Y-%m-%dT%H:%M:%SZ"


class VistudioFormatterPreprocessor(Preprocessor):
    """
    use this Preprocessor to handle dataset
    """

    def __init__(self,
                 config: Config,
                 labels: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 data_uri: str = None,
                 data_type: str = None,
                 tag: Union[Dict] = None
                 ):
        self.config = config
        self._is_fittable = True
        self.labels = {v: int(k) for k, v in labels.items()}
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_type = data_type
        self.tag = tag

        # 初始化train client
        self.train_client = TrainingClient(endpoint=config.windmill_endpoint,
                                           ak=config.windmill_ak,
                                           sk=config.windmill_sk)
        self.exist_images = _get_exist_images(config=self.config,
                                              annotation_set_id=self.annotation_set_id)  # 已经存在的图片，用于过滤
        self.exist_annotations = _get_exist_annoation(config=self.config,
                                                      annotation_set_id=self.annotation_set_id)  # 已经存在的标注，用于过滤

    @staticmethod
    def _flat(row: Dict[str, Any], col: str) -> List[Dict[str, Any]]:
        """
         Expand the col column
        :param col:
        :return: List
        """
        # ray.util.pdb.set_trace()
        return row[col]

    def _fit_images(self, ds: "Dataset") -> "Dataset":
        """
        _fit_images
        :param ds:
        :return:
        """
        ds = ds.filter(lambda row: row["data_type"] == "Image")
        filter = Filter(labels=self.labels)

        df = filter.drop_duplicates(source=ds.to_pandas(), cols=['image_name'])
        ds = ray.data.from_pandas(df)
        vistudio_formatter = VistudioFormatter(
            labels=self.labels,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            data_uri=self.data_uri,
            data_type=self.data_type,
            user_id=self.config.user_id,
            org_id=self.config.org_id,
            tag=self.tag)
        ds = vistudio_formatter.to_vistudio_v1(ds)

        ds = filter.filter_image(source=ds, existed_images=self.exist_images)
        return ds

    def _fit_annotations(self, ds: "Dataset") -> "Dataset":
        """
        _fit_annotations
        :param ds:
        :return:
        """
        ds = ds.filter(lambda row: (row['data_type'] == 'Annotation' and row['image_id'] not in self.exist_annotations))
        vistudio_formatter = VistudioFormatter(
            labels=self.labels,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            data_uri=self.data_uri,
            data_type=self.data_type,
            user_id=self.config.user_id,
            org_id=self.config.org_id,
            tag=self.tag)
        ds = vistudio_formatter.to_vistudio_v1(ds)
        filter = Filter(labels=self.labels)
        source_df = ds.to_pandas()
        filter.drop_duplicates(source=source_df, cols=['image_id', 'data_type', 'artifact_name'], inplace=True)
        ds = ray.data.from_pandas(source_df)
        return ds

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        fit coco dataset
        :param ds:
        :return: Preprocessor
        """
        if self.data_type == 'Image':
            self.stats_ = self._fit_images(ds=ds)
        elif self.data_type == 'Annotation':
            self.stats_ = self._fit_annotations(ds=ds)
        return self
