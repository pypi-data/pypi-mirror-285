#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   webp_state_preprocessor.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""
import pandas as pd
from typing import Dict, Any
from ray.data.preprocessor import Preprocessor
from vistudio.annotation.operator.updater.webp_state_updater import WebpStateUpdater


class WebpStateUpdaterPreprocessor(Preprocessor):
    """
    to update webp_state
    """

    def __init__(self, config):
        self._is_fittable = True
        self._fitted = True

        self.config = config

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
        operator = WebpStateUpdater(config=self.config)
        return operator.update_webp_state(source=df)