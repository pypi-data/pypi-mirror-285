# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
supervisor.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/22 8:59 下午
"""
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from vistudio.annotation.scheduler.trigger import ExponentialBackoffTrigger
from vistudio.annotation.scheduler.executor import RayExecutor


class Scheduler(object):
    """
    scheduler 调度器
    """
    def __init__(self, **config):
        executor_config = config.get("executor", {})
        job_store_config = config.get("job_store", {})
        self.trigger_config = config.get("trigger", {})
        self._scheduler = AsyncIOScheduler()
        self._scheduler.add_executor(RayExecutor(**executor_config))
        job_store_kind = job_store_config.get("kind", "memory")
        job_store_config.pop("kind", None)
        self._scheduler.add_jobstore(job_store_kind, **job_store_config)
        self._scheduler.start()

    def add_job(self, func, job_id=None, trigger=None, args=None, misfire_grace_time=None):
        """
        add job 添加任务
        """
        if job_id is None:
            job_id = uuid.uuid4()
        if trigger is None:
            trigger = self.default_trigger()
        self._scheduler.add_job(func, trigger=trigger, id=job_id, args=args, misfire_grace_time=misfire_grace_time)

    def list_job(self):
        """
        list job 列出所有任务
        """
        return self._scheduler.get_jobs()

    def get_job(self, job_id):
        """
        get job 获取任务
        """
        return self._scheduler.get_job(job_id)

    def remove_job(self, job_id):
        """
        remove job 移除任务
        """
        self._scheduler.remove_job(job_id)

    def modify_job(self, job_id, func, **changes):
        """
        modify job 修改任务
        """
        self._scheduler.modify_job(job_id, func=func, **changes)

    def reschedule_job(self, job_id, trigger=None):
        """
        reschedule job 重新调度任务
        """
        if trigger is None:
            trigger = self.default_trigger()
        self._scheduler.reschedule_job(job_id, trigger=trigger)

    def default_trigger(self):
        """
        default trigger 默认触发器
        """
        init_interval = self.trigger_config.get("init_interval", 4)
        max_interval = self.trigger_config.get("max_interval", 600)
        init_turns = self.trigger_config.get("init_turns", 30)
        exponential = self.trigger_config.get("exponential", 2)
        return ExponentialBackoffTrigger(init_interval, max_interval, init_turns=init_turns, exponential=exponential)
