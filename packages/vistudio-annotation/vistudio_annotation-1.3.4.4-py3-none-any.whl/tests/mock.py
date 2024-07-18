# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
mock.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/30 3:04 下午
"""
import time

import bcelogger


def print_hello():
    bcelogger.info("hello")
    time.sleep(0.5)


def print_hello2():
    bcelogger.info("hello2")
    time.sleep(0.5)


def print_world():
    bcelogger.info("world")
    time.sleep(1)
