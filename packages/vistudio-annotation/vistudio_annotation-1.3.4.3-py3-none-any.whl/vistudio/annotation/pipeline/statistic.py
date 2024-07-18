# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
statistic.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/3/23 2:37 下午
"""

import argparse
import base64
import json
import os
import random

import logit
import pymongo
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from gaea_operator.metric import LabelStatisticMetricAnalysis, InferenceMetricAnalysis, EvalMetricAnalysis, Metric
from windmillcomputev1.client.compute_client import ComputeClient
from windmillcomputev1.filesystem import blobstore

from vistudio.annotation.client.annotation_client import AnnotationClient
from vistudio.annotation.config.config import Config
from vistudio.annotation.pipeline.query_pipeline import query_mongo
from vistudio.annotation.client.annotation_api_annotationset import parse_annotation_set_name
from vistudio.annotation.config.arg_parser import ArgParser


logit.base_logger.setup_logger({})


def parse_filesystem_name(filesystem_name):
    """
    解析 filesystem_name
    :param filesystem_name:
    :return:
    """
    workspace_id, local_name = filesystem_name.split("/")[1], filesystem_name.split("/")[-1]
    return workspace_id, local_name


def generate_output_json_path(name=None):
    """
    生成输出文件路径
    :return:
    """
    output_dir = "./output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if name is None:
        name = str(random.randint(0, 2 ** 16))
    output_json = output_dir + "/" + name + ".json"
    return output_json


def statistic(base_conf: Config, annotation_set_name, query_pipeline):
    """
    指标统计分析
    :param base_conf:
    :param annotation_set_name:
    :param query_pipeline:
    :return:
    """
    # 获取 s3 配置
    bs = blobstore(filesystem=base_conf.filesystem)
    location = "s3://" + base_conf.filesystem['endpoint'] + "/" + base_conf.job_name
    logit.info(f"upload location: {location}")

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
    cate = annotation_set.category
    annotation_set_category = cate.get("category", "Image/ObjectDetection")
    logit.info("annotation_set_category: {}".format(annotation_set_category))

    labels = annotation_set.labels
    if labels is None:
        logit.info("No label")
        return

    new_labels = []
    for label in labels:
        new_label = dict()
        new_label["name"] = label.get('displayName', "")
        new_label["id"] = label.get('localName', "")
        new_labels.append(new_label)
    labels = new_labels
    logit.info("labels: {}".format(labels))

    # 获取需要统计的图片及标注
    results = query_mongo(query_pipeline, collection)
    images = results.get("images", [])
    annotations = results.get("annotations", [])

    if len(images) == 0:
        logit.info("No images to statistic")
        return

    # 分组不同的模型结果
    annotation_map = {}
    for annotation in annotations:
        artifact_name = annotation.get("artifact_name", "")
        if artifact_name not in annotation_map:
            annotation_map[artifact_name] = []
        annotation_map[artifact_name].append(annotation)

    ## TODO 用于调试，保存原始查询结果
    ori_data_location = location + "/ori_data/"
    # 保存图片和标签
    for image in images:
        image.pop("_id")
    image_json = generate_output_json_path("images")
    with open(image_json, "w") as f:
        json.dump(images, f)
    bs.upload_file(image_json, ori_data_location + os.path.basename(image_json))
    labels_json = generate_output_json_path("labels")
    with open(labels_json, "w") as f:
        json.dump(labels, f)
    bs.upload_file(labels_json, ori_data_location + os.path.basename(labels_json))
    # 保存人工和模型标注结果
    for artifact_name, annotations in annotation_map.items():
        for anno in annotations:
            anno.pop("_id")
        annotation_json = generate_output_json_path("annotations-" + artifact_name.replace("/", "-"))
        with open(annotation_json, "w") as f:
            json.dump(annotations, f)
        bs.upload_file(annotation_json, ori_data_location + os.path.basename(annotation_json))

    # 统计不同模型的指标
    eval_metric = EvalMetricAnalysis(category=annotation_set_category, labels=labels, images=images)
    label_statistics = LabelStatisticMetricAnalysis(category=annotation_set_category, labels=labels)
    metric = Metric(metric=[eval_metric, label_statistics], annotation_set_name=annotation_set_name)
    for artifact_name, annotations in annotation_map.items():
        if artifact_name == "":
            manual_json = generate_output_json_path()
            metric(references=annotations, output_uri=manual_json, task_kind="Manual")
            bs.upload_file(manual_json, location + "/metric-manual.json")
            os.remove(manual_json)
            continue

        artifact_file_name = "metric-" + artifact_name.replace("/", "-") + ".json"
        output_url = generate_output_json_path()
        manual_annotations = annotation_map.get("", None)
        metric(predictions=annotations, references=manual_annotations, output_uri=output_url,
               task_kind="Model", artifact_name=artifact_name)
        bs.upload_file(output_url, location + "/" + artifact_file_name)
        os.remove(output_url)


if __name__ == '__main__':
    logit.info("start statistic")
    arg_parser = ArgParser(kind='Statistic')
    args = arg_parser.parse_args()
    config = Config(args)
    q = args.get("q")
    q = base64.b64decode(q)
    logit.info(f"query: {q}")
    q = json.loads(q)

    statistic(config, args.get("annotation_set_name"), q)

