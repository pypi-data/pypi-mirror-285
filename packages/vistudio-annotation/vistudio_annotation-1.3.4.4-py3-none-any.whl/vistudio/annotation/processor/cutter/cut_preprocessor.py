#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   cut_preprocessor.py
@Time    :   2024/5/11 16:48
@Author  :   dongling
"""

import sys
import os
import math
import numpy as np
import pandas as pd
import bcelogger
import io
from PIL import Image
from typing import Union, Dict, Any
from ray.data.preprocessor import Preprocessor
from windmillcomputev1.filesystem import blobstore

from vistudio.annotation.util import string
from vistudio.annotation.operator.vistudio_cutter import VistudioCutter
from vistudio.annotation.util.annotation import polygon_area, rle2mask, mask2rle, rle_area, bbox_overlaps


class VistudioCutterPreprocessor(Preprocessor):
    """
    to cut vistudio
    """

    def __init__(self, config, location, split):
        self._is_fittable = True
        self._fitted = True

        self.config = config
        self.location = location
        self.split = split

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 100}

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        operator = VistudioCutter(self.config.filesystem, self.location, self.split)
        return operator.cut_images_and_annotations(source=df)
