# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""

"""
from inspect import ismethod, isclass

import yaml
import argparse
import bcelogger
from ray import serve

from vistudio.annotation.config.config import Config
from vistudio.annotation.scheduler.scheduler import Scheduler
from vistudio.annotation.pipeline.factory import PipelineFactory


@serve.deployment(num_replicas=1, ray_actor_options={"num_cpus": 1})
class Supervisor:
    """
    Supervisor：管理pipeline的调度器
    """
    def __init__(self, config):
        self.global_config = Config(config['global'])
        # initial scheduler
        scheduler_config = config.get('scheduler', {})
        self._scheduler = Scheduler(**scheduler_config)
        # initial pipelines
        init_pipelines = config.get('init_pipelines', [])
        for pipe in init_pipelines:
            pipeline_name = pipe['name']
            options = pipe.get('options', {})
            self.reconfigure_pipeline(pipeline_name, **options)

    async def __call__(self, http_request):
        request = await http_request.json()
        bcelogger.info(f"request: {request}")

        pipelines = request.get('pipelines', None)
        action = request.get('action', "reset")
        if pipelines is None:
            return "pipelines is None, check the param"

        for pipeline in pipelines:
            pipeline_name = pipeline.get('name', None)
            if pipeline_name is None:
                return "pipeline.name is None, check the param"

            options = pipeline.get('options', {})

            try:
                pipeline_instance = PipelineFactory.get_pipeline_instance(
                    pipeline_name, self.global_config, **options)
            except Exception as e:
                bcelogger.error(f"Error creating pipeline instance: {e}")
                return "Error creating pipeline instance: {}".format(e)

            if action == "reschedule":
                self._scheduler.reschedule_job(pipeline_name)
            elif action == "add":
                self._scheduler.add_job(pipeline_instance.run, job_id=pipeline_name)
            elif action == "remove":
                self._scheduler.remove_job(pipeline_name)
            elif action == "modify":
                self.reconfigure_pipeline(pipeline_name, replace_options=True, **options)
            else:
                return "action is not support"

        return "Action success"

    def reconfigure_pipeline(self, pipeline_name, replace_options=False, **options):
        """
        重新配置pipeline
        """
        pipeline_job = self._scheduler.get_job(pipeline_name)
        if pipeline_job is None:
            bcelogger.info(f"pipeline {pipeline_name} is not exist, just add")
            pipeline_instance = PipelineFactory.get_pipeline_instance(pipeline_name, self.global_config, **options)
            self._scheduler.add_job(pipeline_instance.run, job_id=pipeline_name)
            return

        bcelogger.info(f"pipeline {pipeline_name} is already exist, just modify")
        func = pipeline_job.func
        if ismethod(func):
            old_options = func.__self__.get_options()
        else:
            old_options = pipeline_job.args[0].get_options()
        new_options = options if replace_options else old_options
        pipeline_instance = PipelineFactory.get_pipeline_instance(pipeline_name, self.global_config, **new_options)
        self._scheduler.modify_job(pipeline_name, pipeline_instance.run, args=())


def main(args):
    """
    启动serve
    """
    file_path = args.file_path
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        bcelogger.error(f"Error reading file or parsing YAML: {e}")
        return

    app = Supervisor.bind(config)
    serve.run(app, route_prefix="/v2/imageaggregation", name="pipeline_app")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--f",
        dest="file_path",
        required=True,
        default="",
        help="background pipelines",
    )

    args = parser.parse_args()
    main(args)
