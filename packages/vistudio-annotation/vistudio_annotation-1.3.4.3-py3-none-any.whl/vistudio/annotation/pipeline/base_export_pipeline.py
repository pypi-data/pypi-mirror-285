#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   base_pipeline.py
"""
import os
import re
import json
import bcelogger
from typing import List, Dict, Any

from windmillcomputev1.filesystem import blobstore
from windmilltrainingv1.client.training_client import TrainingClient

from vistudio.annotation.client.annotation_client import AnnotationClient
from vistudio.annotation.config.config import Config
from ray.data.datasource.datasource import Datasource
from vistudio.annotation.datasource import mongo_query_pipeline
from vistudio.annotation.datasource.sharded_mongo_datasource import ShardedMongoDatasource, parse_mongo_uri, \
    get_mongo_collection
from vistudio.annotation.util import string


annotationset_name_pattern = r"workspaces/(?P<workspace_id>[^/]+)/projects/(?P<project_name>[^/]+)/annotationsets/" \
                             r"(?P<annotationset_local_name>[^/]+)$"

ANNOTATION_FORMAT_COCO = 'COCO'
ANNOTATION_FORMAT_PADDLECLAS = 'PaddleClas'
ANNOTATION_FORMAT_PADDLESEG = 'PaddleSeg'


class BaseExportPipeline(object):
    """
    BaseExportPipeline
    """
    def __init__(self, args):
        self.args = args
        self.config = Config(args=args)
        self.dataset = json.loads(string.decode_from_base64(args.get('dataset')))
        self.merge_labels = self._get_merge_labels()
        self._get_labels()
        self.annotation_format = args.get('annotation_format').lower()
        self.datasource = self._get_datasource()
        self.split = self._get_split()

        self.train_client = TrainingClient(
            endpoint=self.config.windmill_endpoint,
            ak=self.config.windmill_ak,
            sk=self.config.windmill_sk
        )
        self.bs = blobstore(filesystem=self.config.filesystem)

    def _get_datasource(self):
        """
        get datasource
        :return:
        """
        pipeline = self._get_mongo_pipeline()
        func = mongo_query_pipeline.get_pipeline_func(pipeline)

        return ShardedMongoDatasource(uri=self.config.mongo_uri, 
                                      database=self.config.mongodb_database, 
                                      collection=self.config.mongodb_collection, 
                                      pipeline_func=func)

    def _get_merge_labels(self):
        """
        get merge labels
        :return:
        """
        if self.args.get('merge_labels') is not None and self.args.get('merge_labels') != '':
            merge_labels = json.loads(string.decode_from_base64(self.args.get('merge_labels')))
        else:
            merge_labels = None

        return merge_labels

    def _get_mongo_pipeline(self):
        """
        get mongo pipeline
        :return:
        """
        if self.args.get('q') is not None and self.args.get('q') != '':
            mongo_pipeline = json.loads(string.decode_from_base64(self.args.get('q')))
        else:
            mongo_pipeline = None

        bcelogger.info("mongo_pipeline:{}".format(mongo_pipeline))
        return mongo_pipeline

    def _get_labels(self):
        """
        get labels
        :return:
        """
        annotation_set_name = self.args.get('annotation_set_name')
        self.annotation_set_name = annotation_set_name
        try:
            annotation_client = AnnotationClient(endpoint=self.config.vistudio_endpoint,
                                                 ak=self.config.windmill_ak,
                                                 sk=self.config.windmill_sk)
            match = re.match(annotationset_name_pattern, self.annotation_set_name)
            annotationset_name_dict = match.groupdict()
            annotationset_workspace_id = annotationset_name_dict.get("workspace_id")
            annotationset_project_name = annotationset_name_dict.get("project_name")
            annotationset_local_name = annotationset_name_dict.get("annotationset_local_name")
            anno_res = annotation_client.get_annotation_set(workspace_id=annotationset_workspace_id,
                                                            project_name=annotationset_project_name,
                                                            local_name=annotationset_local_name)
        except Exception as e:
            bcelogger.error("get annotation info exception.annotation_name:{}"
                         .format(annotation_set_name), e)
            raise Exception("Get annotation set info exception.annotation_set_name:{}".format(annotation_set_name))

        self.annotation_set_id = anno_res.id
        annotation_labels = anno_res.labels
        labels = {}
        if annotation_labels is not None:
            for label_elem in annotation_labels:
                label_local_name = label_elem.get('localName', None)
                label_display_name = label_elem.get('displayName', None)
                labels[label_local_name] = label_display_name

        sorted_labels = {k: v for k, v in sorted(labels.items(), key=lambda x: int(x[0]))}

        self.labels = sorted_labels

    def _get_split(self):
        """
        get split
        :return:
        """
        if self.args.get('split') is not None and self.args.get('split') != '':
            split = json.loads(string.decode_from_base64(self.args.get('split')))
        else:
            split = None

        bcelogger.info("split:{}".format(split))
        return split

    def create_dataset(self, location,
                       annotation_format,
                       dataset):
        """
        create dataset
        :param location:
        :param annotation_format:
        :param dataset:
        :param workspace_id:
        :param project_name:
        :return:
        """
        # 创建数据集
        artifact = dataset.get('artifact', {})
        if annotation_format == 'coco':
            annotation_format = ANNOTATION_FORMAT_COCO
        elif annotation_format == 'paddleseg':
            annotation_format = ANNOTATION_FORMAT_PADDLESEG
        elif annotation_format == 'paddleclas':
            annotation_format = ANNOTATION_FORMAT_PADDLECLAS
        dataset_resp = self.train_client.create_dataset(
            workspace_id=dataset.get("workspaceID"),
            project_name=dataset.get("projectName"),
            category=dataset.get("category", "Image/ObjectDetecton"),
            local_name=dataset.get("localName"),
            artifact_uri=location,
            description=dataset.get('description', ''),
            display_name=dataset.get('displayName', ''),
            data_type=dataset.get('dataType', 'Image'),
            annotation_format=annotation_format,
            artifact_description=artifact.get('description', ''),
            artifact_alias=artifact.get('alias', []),
            artifact_tags=artifact.get('tags', []),
            artifact_metadata={'paths': [location + "/"]},
        )
        bcelogger.info("create dataset resp is {}".format(dataset_resp))

    def save_label_file(self, file_path: str, labels: dict(), start_index: int = 0):
        """
        save_label_file
        :param file_path:
        :param labels:
        :param start_index:
        :return:
        """
        labels_list = list()
        label_id_dict = dict()
        for label_id, label_name in labels.items():
            label_index = len(label_id_dict) + start_index
            labels_list.append("{} {}".format(label_name, label_index) + os.linesep)
            label_id_dict[label_id] = label_index
        self.bs.write_raw(path=file_path, content_type="text/plain", data=''.join(labels_list))

    def save_json_file(self, file_path: str, json_data: List[Dict[str, Any]]):
        """
        save_label_file
        :param file_path:
        :param labels:
        :param start_index:
        :return:
        """
        self.bs.write_raw(path=file_path, content_type="application/json", data=''.join(json_data))

    def save_vistuido_meta_json_file(self, file_path: str, labels: dict()):
        """
        save_vistuido_meta_json_file
        :param file_path:
        :return:
        """
        bcelogger.info("----save_vistuido_meta_json_file path:{}".format(file_path))
        vs_labels = list()
        if labels is not None:
            for label_id, label_name in labels.items():
                item = {
                    "id": label_id,
                    "name": label_name
                }
                vs_labels.append(item)

        meta = {
            "data_type": "Label",
            "annotation_set_name": self.annotation_set_name,
            "labels": vs_labels
        }

        # 将字典转换为JSON字符串
        data_json = json.dumps(meta)
        self.bs.write_raw(path=file_path, content_type="application/json", data=data_json)
