# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
batch_delete.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/3/18 3:55 下午
"""

import argparse
import base64
import json

import logit
import pymongo
from mongoengine import connect
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

from vistudio.annotation.config.arg_parser import ArgParser
from vistudio.annotation.table.image import ImageData
from vistudio.annotation.pipeline.query_pipeline import query_mongo
from vistudio.annotation.config.config import Config
from vistudio.annotation.client.annotation_client import AnnotationClient
from vistudio.annotation.client.annotation_api_annotationset import parse_annotation_set_name


logit.base_logger.setup_logger({})


def batch_delete(base_conf: Config, annotation_set_name, query_pipeline):
    """
    批量删除
    :param base_conf:
    :param annotation_set_name:
    :param query_pipeline
    :return:
    """
    # 连接Mongo
    client = pymongo.MongoClient(base_conf.mongo_uri)
    db = client[base_conf.mongodb_database]
    collection = db[base_conf.mongodb_collection]

    # 获取 annotation_set_id
    windmill = AnnotationClient(
        BceClientConfiguration(credentials=BceCredentials(base_conf.windmill_ak, base_conf.windmill_sk),
                               endpoint=base_conf.vistudio_endpoint))

    set_name = parse_annotation_set_name(annotation_set_name)
    annotation_set = windmill.get_annotation_set(set_name.workspace_id, set_name.project_name, set_name.local_name)
    logit.info("annotation_set: {}".format(annotation_set))
    annotation_set_id = annotation_set.id
    logit.info("annotation_set_id: {}".format(annotation_set_id))

    # 获取需要更新的 image_id
    results = query_mongo(query_pipeline, collection)
    delete_image_ids = results.get("image_ids", [])
    logit.info("delete_image_ids: {}".format(delete_image_ids))

    # 通过 mongo 删除
    ImageData.objects(annotation_set_id=annotation_set_id, image_id__in=delete_image_ids).delete()


if __name__ == '__main__':
    logit.info("start batch delete")
    arg_parser = ArgParser(kind='BatchDelete')
    args = arg_parser.parse_args()
    config = Config(args)
    logit.info(f"args: {args}")
    q = args.get("q")
    q = base64.b64decode(q)
    logit.info(f"query: {q}")
    q = json.loads(q)

    connect(host=config.mongo_uri, db=args.get("mongo_database"))

    batch_delete(config, args.get("annotation_set_name"), q)

