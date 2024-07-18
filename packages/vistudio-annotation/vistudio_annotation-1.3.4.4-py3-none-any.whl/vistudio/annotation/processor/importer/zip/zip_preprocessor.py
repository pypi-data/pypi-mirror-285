#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   preprocessor.py
"""
from typing import Union, Dict

from ray.data.preprocessor import Preprocessor

from vistudio.annotation.config.config import Config

import logit

from vistudio.annotation.operator.zip_formatter import ZipFormatter

logit.base_logger.setup_logger({})


class ZipFormatPreprocessor(Preprocessor):
    """
    ZipFormatPreprocessor
    """
    def __init__(self,
                config: Config,
                annotation_format: str = None
                ):
        self.config = config
        self.annotation_format = annotation_format

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return:
        """
        zip_formatter = ZipFormatter(filesystem=self.config.filesystem, annotation_format=self.annotation_format)
        file_uris = zip_formatter.unzip_and_upload(file_uris=ds.unique(column='item'))
        self.stats_ = file_uris
        return self



