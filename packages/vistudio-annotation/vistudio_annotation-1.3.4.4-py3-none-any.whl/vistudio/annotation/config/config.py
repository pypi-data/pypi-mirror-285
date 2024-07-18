# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
Vistudio Spec
"""
from windmillcomputev1.client.compute_api_filesystem import parse_filesystem_name
from windmillcomputev1.client.compute_client import ComputeClient
from windmilltrainingv1.client.training_api_job import parse_job_name
from windmilltrainingv1.client.training_client import TrainingClient

from pydantic import BaseModel


class Config(BaseModel):
    """
    定义基础变量
    """
    filesystem: dict = None
    mongo_uri: str = ""
    mongodb_database: str = ""
    mongodb_collection: str = ""

    windmill_endpoint: str = ""
    windmill_ak: str = ""
    windmill_sk: str = ""

    vistudio_endpoint: str = ""
    job_name: str = ""

    org_id: str = ""
    user_id: str = ""

    def __init__(self, args: dict()):
        super().__init__(
            job_name=args.get('job_name', ''),
            mongodb_database=args.get('mongo_database', ''),
            mongodb_collection=args.get('mongo_collection', ''),
            windmill_endpoint=args.get('windmill_endpoint', ''),
            windmill_ak=args.get('windmill_ak', ''),
            windmill_sk=args.get('windmill_sk', ''),
            vistudio_endpoint=args.get('vistudio_endpoint', '')
        )

        self.parse_args(args)

    def parse_args(self, args: dict()):
        """
        parse_args
        :param args:
        :return:
        """
        mongo_user = args.get('mongo_user')
        mongo_password = args.get('mongo_password')
        mongo_host = args.get('mongo_host')
        mongo_port = args.get('mongo_port')
        self.mongo_uri = "mongodb://{}:{}@{}:{}".format(
            mongo_user,
            mongo_password,
            mongo_host,
            mongo_port
        )

        if args.get('filesystem_name') is None:
           return

        fsName = parse_filesystem_name(args.get('filesystem_name'))
        compute_client = ComputeClient(endpoint=self.windmill_endpoint,
                                       ak=self.windmill_ak,
                                       sk=self.windmill_sk)

        fs_res = compute_client.get_filesystem_credential(fsName.workspace_id,
                                                          fsName.local_name)
        import json
        self.filesystem = json.loads(fs_res.raw_data)

        train_client = TrainingClient(endpoint=self.windmill_endpoint,
                                      ak=self.windmill_ak,
                                      sk=self.windmill_sk)
        client_job_name = parse_job_name(self.job_name)
        job_res = train_client.get_job(workspace_id=client_job_name.workspace_id,
                                       project_name=client_job_name.project_name,
                                       local_name=client_job_name.local_name)

        self.org_id = job_res.orgID
        self.user_id = job_res.userID



