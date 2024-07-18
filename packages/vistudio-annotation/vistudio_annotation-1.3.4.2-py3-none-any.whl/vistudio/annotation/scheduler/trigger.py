# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
trigger.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/23 4:30 下午
"""
from datetime import timedelta, datetime

from apscheduler.triggers.base import BaseTrigger


class ExponentialBackoffTrigger(BaseTrigger):
    """
    ExponentialBackoffTrigger 指数退避触发器
    """
    def __init__(self, init_interval, max_interval, init_turns=10, exponential=2):
        self.init_interval = init_interval
        self.max_interval = max_interval
        self.init_turns = init_turns
        self.exponential = exponential
        self.interval = init_interval
        self.runs = 0
        self.last_fire_time = None
        super().__init__()

    def get_next_fire_time(self, previous_fire_time, now):
        if previous_fire_time is None:
            self.last_fire_time = now
            return self.last_fire_time

        if self.last_fire_time is not None and now <= self.last_fire_time:
            return self.last_fire_time

        self.runs += 1
        if self.runs > self.init_turns:
            self.interval = min(self.interval * self.exponential, self.max_interval)

        self.last_fire_time = previous_fire_time + timedelta(seconds=self.interval)
        return self.last_fire_time
