#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
formater.py
"""

from typing import Union, Dict, Any

import pandas as pd
import ray.data
from ray.data.preprocessor import Preprocessor

from vistudio.annotation.config.config import Config
import logit

from vistudio.annotation.operator.paddleseg_formatter import PaddleSegFormatter

logit.base_logger.setup_logger({})


class PaddleSegFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert vistudio_v1 to paddleseg
    """

    def __init__(self,
                 config: Config,
                 merge_labels: Union[Dict] = dict,
                 location: str = None,
                 labels: Union[Dict] = dict,
                 ):
        self._is_fittable = True
        self._fitted = True
        self.merge_labels = merge_labels
        self.location = location
        self.config = config
        self.labels = labels

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        operator = PaddleSegFormatter(filesystem=self.config.filesystem,
                                      labels=self.labels,
                                      location=self.location,
                                      merge_labels=self.merge_labels)
        return operator.from_vistudio_v1(source=df)

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 1, "concurrency": 16}


class PaddleSegMergePreprocessor(Preprocessor):
    """
    use this Preprocessor to merge  every item of dataset  and convert list
    The purpose is to write this list to txt file
    for example:
    ds = [
         {"item": 'aaa' },
         {"item": 'bbb'}
     ]

    merge_list = CityscapeMerger.fit(ds)
    merge_list= ['aaa','bbb']
    """

    def __init__(self, operator: PaddleSegFormatter):
        self._is_fittable = True
        self._fitted = True
        self.operator = operator

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        df = ds.to_pandas()
        self.stats_ = ray.data.from_pandas(self.operator.merge(rows=df))
        return self

