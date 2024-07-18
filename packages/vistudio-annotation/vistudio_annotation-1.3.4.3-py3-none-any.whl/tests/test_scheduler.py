# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
scheduler_test.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/30 2:55 下午
"""
import asyncio
import time

import bcelogger

from tests.mock import print_hello, print_world, print_hello2
from vistudio.annotation.scheduler.scheduler import Scheduler


async def test_memory_store():
    scheduler = Scheduler()
    if scheduler.get_job("hello") is None:
        scheduler.add_job(print_hello, job_id="hello")
    if scheduler.get_job("world") is None:
        scheduler.add_job(print_world, job_id="world")

    await asyncio.sleep(20)
    bcelogger.info("reset job trigger")
    scheduler.reschedule_job("hello")
    await asyncio.sleep(20)

    bcelogger.info("modify hello job")
    scheduler.modify_job("hello", print_hello2)
    await asyncio.sleep(20)


async def test_mysql_store():
    mysql_url = "mysql+pymysql://root:windmill2023@10.27.240.45:8436/windmill?charset=utf8mb4"
    config = {
        "job_store": {
            "kind": "sqlalchemy",
            "url": mysql_url,
        },
        "trigger": {
            "init_interval": 1,
            "max_interval": 600,
            "init_turns": 3,
            "exponential": 2,
        }
    }
    scheduler = Scheduler(**config)
    if scheduler.get_job("hello") is None:
        scheduler.add_job(print_hello, job_id="hello")
    await asyncio.sleep(20)


async def test_mongo_store():
    config = {
        "job_store": {
            "kind": "mongodb",
            "host": '10.27.240.45',
            "port": 8719,
            "username": 'root',
            "password": 'mongo123#',
        },
        "trigger": {
            "init_interval": 1,
            "max_interval": 600,
            "init_turns": 3,
            "exponential": 2,
        }
    }
    scheduler = Scheduler(**config)
    if scheduler.get_job("hello") is None:
        scheduler.add_job(print_hello, job_id="hello")
    await asyncio.sleep(20)


if __name__ == '__main__':
    asyncio.run(test_mongo_store())
