# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
factory.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/23 8:17 下午
"""
from vistudio.annotation.pipeline.base import BasePipeline


class PipelineFactory:
    """
    工厂类，用于创建pipeline实例
    """
    @classmethod
    def get_pipeline_instance(cls, pipeline_name, *args, **kwargs):
        """
        获取pipeline实例
        """
        subclasses = BasePipeline.get_all_subclasses()
        print(f"----subclass-----: {subclasses}")
        return subclasses[pipeline_name](*args, **kwargs)


def test_get_pipeline_instance():
    """
    测试获取pipeline实例
    """
    pipeline_name = 'GenerateThumbnailPipeline'
    constructor_kwargs = ("", {}, )
    instance = PipelineFactory.get_pipeline_instance(pipeline_name, constructor_kwargs)
    print(instance)


if __name__ == '__main__':
    test_get_pipeline_instance()
