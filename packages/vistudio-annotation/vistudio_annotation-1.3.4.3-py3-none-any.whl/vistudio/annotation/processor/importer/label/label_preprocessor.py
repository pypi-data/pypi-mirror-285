#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   formater.py
"""
from typing import Union, Dict

import ray.data
from ray.data.preprocessor import Preprocessor
from windmillcomputev1.filesystem import init_py_filesystem
from windmilltrainingv1.client.training_api_job import parse_job_name

from vistudio.annotation.config.config import Config
import logit

from vistudio.annotation.operator.filter import Filter
from vistudio.annotation.operator.label_formatter import LabelFormatter
import numpy as np

logit.base_logger.setup_logger({})


class LabelFormatPreprocessor(Preprocessor):
    """
    LabelFormatPreprocessor
    """

    def __init__(self,
                 config: Config,
                 annotation_format: str,
                 labels: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None

                 ):
        self._is_fittable = True
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.labels = labels
        self.annotation_format = annotation_format




    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return:
        """

        label_formatter = LabelFormatter(labels=self.labels,
                                         annotation_set_id=self.annotation_set_id,
                                         annotation_set_name=self.annotation_set_name,
                                         annotation_format=self.annotation_format,
                                         filesystem=self.config.filesystem)
        need_import_annotation_labels = label_formatter.labels_to_vistudio_v1(ds=ds)

        self.stats_ = need_import_annotation_labels
        return self
