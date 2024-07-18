# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
executor.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/23 10:10 下午
"""
import asyncio

import ray
from apscheduler.executors.base import BaseExecutor, run_job
from apscheduler.executors.asyncio import AsyncIOExecutor


@ray.remote(num_cpus=1)
def func_with_ray_task(func, args):
    """
    Ray task function.
    """
    return func(*args)


class RayExecutor(AsyncIOExecutor):
    """
    RayExecutor 使用Ray作为执行器，支持分布式执行任务。
    """
    def __init__(self, **config):
        super().__init__()
        ray_address = config.get('ray_address', None)
        #ray.init(address=ray_address)

    def _do_submit_job(self, job, run_times):
        """
        提交任务到Ray执行器中执行。
        """
        def callback(f):
            """
            回调函数，用于处理任务执行完成后的结果。
            """
            exc, tb = (f.exception_info() if hasattr(f, 'exception_info') else
                       (f.exception(), getattr(f.exception(), '__traceback__', None)))
            if exc:
                self._run_job_error(job.id, exc, tb)
            else:
                self._run_job_success(job.id, f.result())
                pass

        f = func_with_ray_task.remote(run_job, (job, job._jobstore_alias, run_times, self._logger.name, ))

        asyncio.wrap_future(f.future()).add_done_callback(callback)

    def shutdown(self, wait=True):
        self._logger.info('RayExecutor shutdown')
        if wait:
            ray.shutdown()
        else:
            ray.shutdown(block=False)
