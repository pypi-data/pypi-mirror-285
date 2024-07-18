# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
base_mongo_updater.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/29 9:40 下午
"""
from mongoengine import connect


class BaseMongoUpdater(object):
    """
    基础的mongo数据更新器
    """
    def __init__(self, config):
        self.config = config
        connect(host=config.mongo_uri, db=config.mongodb_database)