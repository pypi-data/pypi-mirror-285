#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   ImageUriFormatter.py
"""
import time
from typing import Union, Dict, Any, List

import ray.data
from ray.data.preprocessor import Preprocessor
from ray.data import Dataset

from vistudio.annotation.config.config import Config
from vistudio.annotation.datasource.sharded_mongo_datasource import _get_exist_images
from vistudio.annotation.operator.filter import Filter
from vistudio.annotation.operator.image_formatter import ImageFormatter

import logit

logit.base_logger.setup_logger({})

time_pattern = "%Y-%m-%dT%H:%M:%SZ"


class ImageFormatterPreprocessor(Preprocessor):
    """
    ImageUriFormater , use this Preprocessor to add column
    """

    def __init__(self,
                 config: Config,
                 annotation_set_id: str,
                 annotation_set_name: str,
                 tag: Union[Dict] = None):
        self._is_fittable = True
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.tag = tag

        self.exist_images = _get_exist_images(config=self.config,
                                              annotation_set_id=self.annotation_set_id)  # 已经存在的图片，用于过滤

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return: Preprocessor
        """
        logit.info("only import image. original_image_ds_count:{} ".format(ds.count()))
        image_formatter = ImageFormatter(
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            user_id=self.config.user_id,
            org_id=self.config.org_id,
            tag=self.tag)
        format_ds = image_formatter.to_vistudio_v1(ds)
        logit.info("only import image. format_ds count:{} ".format(format_ds.count()))
        filter = Filter(labels=None)
        filter_image_ds = filter.filter_image(source=format_ds, existed_images=self.exist_images)
        logit.info("filter  image ds.filter_image_ds count={}".format(filter_image_ds.count()))

        self.stats_ = filter_image_ds
        return self
