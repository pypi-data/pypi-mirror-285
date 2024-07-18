# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
base.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/23 8:06 下午
"""

import abc

from vistudio.annotation.config.config import Config


class BasePipeline(object):
    """
    base pipeline
    """
    def __init__(self, config: Config, **options):
        """
        init the pipeline
        """
        self.config = config
        self.options = options
        self._stop = True

    def get_options(self):
        """
        get the options
        """
        return self.options

    @abc.abstractmethod
    def run(self):
        """
        run the pipeline
        """

    @classmethod
    def get_all_subclasses(cls):
        """获取所有子类, 注意一定要确保在运行此函数的时候，子类已经被import到

        """
        all_subclasses = {}

        for subclass in cls.__subclasses__():
            all_subclasses[subclass.__name__] = subclass
            all_subclasses.update(subclass.get_all_subclasses())

        return all_subclasses