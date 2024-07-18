#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   thumbnail_generator.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""
import pandas as pd
from typing import Union, Dict, Any
from ray.data.preprocessor import Preprocessor
from vistudio.annotation.operator.thumbnail_generator import ThumbnailGenerator


class ThumbnailGeneratorPreprocessor(Preprocessor):
    """
    to generate thumbnail
    """

    def __init__(self, windmill_endpoint):
        self._is_fittable = True
        self._fitted = True

        self.windmill_endpoint = windmill_endpoint

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
        operator = ThumbnailGenerator(windmill_endpoint=self.windmill_endpoint)
        return operator.generate_thumbnail(source=df)




