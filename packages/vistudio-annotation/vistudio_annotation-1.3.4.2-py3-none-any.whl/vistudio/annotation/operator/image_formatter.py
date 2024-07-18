#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   image_preprocessor.py
"""
import time
from typing import Union, Dict, Any, List

import numpy as np
import ray.data
from ray.data import Dataset
import pandas as pd
import datetime
import os

import logit

from vistudio.annotation.util import string

logit.base_logger.setup_logger({})


class ImageFormatter:
    """
    ImageFormatter
    """
    def __init__(self,
                 annotation_set_id: str,
                 annotation_set_name: str,
                 user_id: str,
                 org_id: str,
                 tag: Union[Dict] = None
                 ):

        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag


    def _fill_image_info(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_image_info
        :param row:
        :return:
        """
        def parse_image_name(image_name: str):
            image_full_name = image_name.split("/")[-1]
            if "_leftImg8bit" in image_full_name:
                image_name = image_full_name.rsplit('.', 1)[0].replace("_leftImg8bit", "")
            else:
                image_name = image_full_name
            return image_name

        file_uri = row['item']
        row['annotation_set_id'] = self.annotation_set_id
        row['user_id'] = self.user_id
        row['data_type'] = 'Image'
        row['file_uri'] = file_uri
        row['width'] = 0
        row['height'] = 0
        row['image_name'] = parse_image_name(file_uri)
        row['image_id'] = string.generate_md5(row['image_name'])
        row['created_at'] = time.time_ns()
        row['annotation_set_name'] = self.annotation_set_name
        row['org_id'] = self.org_id
        if self.tag is not None and len(self.tag) > 0:
            row['tags'] = self.tag
        return row


    def to_vistudio_v1(self, ds: "Dataset") -> "Dataset":
        """
        to_vistudio_v1
        :param ds: Dataset
        :return: Dataset
        """

        final_ds = ds.map(lambda row: self._fill_image_info(row=row)).drop_columns(cols=['item'])
        return final_ds


