#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
formater.py
"""

from typing import Union, Dict, Any

import pandas as pd
import ray.data
from ray.data.preprocessor import Preprocessor
import os

from vistudio.annotation.operator.imagenet_formatter import ImageNetFormatter
from vistudio.annotation.operator.paddleclas_formatter import PaddleClasFormatter


class PaddleClasFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert  vistudio to paddleclas
    """
    def __init__(self,
                 labels: Union[Dict] = dict,
                 merge_labels: Union[Dict] = dict
                 ):
        self._is_fittable = True
        self._fitted = True
        self.merge_labels = merge_labels
        self.labels = labels

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        paddleclas_operator = PaddleClasFormatter(labels=self.labels, merge_labels=self.merge_labels)
        return paddleclas_operator.from_vistudio_v1(source=df)

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 100}


class PaddleClasMergePreprocessor(Preprocessor):
    """
        use this Preprocessor to gather  every item of dataset and convert list
        The purpose is to write this list to txt file
        for example:
        ds = [
             {"item": ['aaa','bbb'], },
             {"item": ['ccc']}
         ]

        merge_list = ImageNetMerger.fit(ds)
        merge_list= ['aaa','bbb', 'ccc']
        """
    def __init__(self, imagenet_operator: ImageNetFormatter):
        self._is_fittable = True
        self._fitted = True
        self.imagenet_operator = imagenet_operator

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        df = ds.to_pandas()
        self.stats_ = ray.data.from_pandas(self.imagenet_operator.merge(rows=df))
        return self

