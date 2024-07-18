#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   writer.py
"""
from typing import Dict, Any, Optional

from pyarrow._s3fs import S3FileSystem
from ray.data.datasource import FilenameProvider
import ray.data
from ray.data.block import Block
import logit

import s3fs
from pyarrow.fs import PyFileSystem, FSSpecHandler
logit.base_logger.setup_logger({})


class MultiFilenameProvider(FilenameProvider):
    """
    FilenameProvider,Generates filenames when you write a :class:`~ray.data.Dataset
    """

    def get_filename_for_row(self, row: Dict[str, Any], task_index: int, block_index: int, row_index: int) -> str:
        """
        get_filename_for_row
        :param row:
        :param task_index:
        :param block_index:
        :param row_index:
        :return:
        """

        if self.file_name is None:
            row_file_name = row.get('file_name', None)
            if row_file_name is not None:
                return row_file_name
            return (
                f"{task_index:06}_{block_index:06}"
                f"_{row_index:06}.{self.file_format}"
            )
        else:
            if self.is_full_file_name:
                return self.file_name
            return (
                f"{task_index:06}_{block_index:06}"
                f"_{row_index:06}_{self.file_name}"
            )

    def __init__(self, file_format: str=None, file_name: str=None, is_full_file_name: bool=False):
        self.file_format = file_format
        self.file_name = file_name
        self.is_full_file_name = is_full_file_name

    def get_filename_for_block(
            self, block: Block, task_index: int, block_index: int
    ) -> str:
        """
        get_filename_for_block
        :param block:
        :param task_index:
        :param block_index:
        :return:
        """
        if self.file_name is None:
            return (
                f"{task_index:06}_{block_index:06}"
                f".{self.file_format}"
            )
        else:
            if self.is_full_file_name:
                return self.file_name
            return (
                f"{task_index:06}_{block_index:06}"
                f"_{self.file_name}"
            )




