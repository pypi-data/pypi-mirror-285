#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   base_pipeline.py
"""

import re
import bcelogger
from windmilltrainingv1.client.training_api_job import parse_job_name
from windmilltrainingv1.client.training_client import TrainingClient

from vistudio.annotation.client.annotation_client import AnnotationClient
from vistudio.annotation.config.config import Config
from vistudio.annotation.datasource.sharded_mongo_datasource import parse_mongo_uri, get_mongo_collection
from vistudio.annotation.util import string
import json


annotationset_name_pattern = r"workspaces/(?P<workspace_id>[^/]+)/projects/(?P<project_name>[^/]+)/annotationsets/" \
                             r"(?P<annotationset_local_name>[^/]+)$"


class BaseImportPipline(object):
    """
    BaseImportPipline
    """

    def __init__(self, args: dict()):
        bcelogger.info("BaseImportPipline Init Start!")
        self.args = args
        self.data_uri = args.get('data_uri')
        self.data_types = args.get('data_types').split(",")
        self.annotation_set_name = args.get('annotation_set_name')
        self.file_format = args.get('file_format').lower()
        self.config = Config(args)
        self.mongo_uri = self._get_mongo_uri()
        self._get_labels()
        self.annotation_format = args.get('annotation_format').lower()
        self.mongodb = get_mongo_collection(config=self.config)
        self.annotation_client = AnnotationClient(endpoint=self.config.vistudio_endpoint,
                                                  ak=self.config.windmill_ak,
                                                  sk=self.config.windmill_sk)
        self.tag = self._get_tag()
        self.train_client = TrainingClient(endpoint=self.config.windmill_endpoint,
                                           ak=self.config.windmill_ak,
                                           sk=self.config.windmill_sk)
        bcelogger.info("BaseImportPipline Init End!")

    def _get_mongo_uri(self):
        """
        get mongo uri
        :return:
        """
        uri = "mongodb://{}:{}@{}:{}".format(self.args.get('mongo_user'),
                                             self.args.get('mongo_password'),
                                             self.args.get('mongo_host'),
                                             self.args.get('mongo_port'))
        return uri

    def _get_tag(self):
        """
        get merge labels
        :return:
        """
        if self.args.get('tag') is not None and self.args.get('tag') != '':
            tag = json.loads(string.decode_from_base64(self.args.get('tag')))
        else:
            tag = None

        return tag

    def _get_labels(self):
        """
        get annotation labels
        :return:
        """

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
            bcelogger.info("get_annotation_set anno_res={}".format(anno_res))
        except Exception as e:
            bcelogger.error("get annotation info exception.annotation_name:{}"
                        .format(self.annotation_set_name), e)
            raise Exception("Get annotation set info exception.annotation_set_name:{}".format(self.annotation_set_name))

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
        return sorted_labels

    def _import_labels(self, need_import_annotation_labels: dict()):
        """
        import labels
        :param need_import_annotation_labels:
        :return:
        """
        if len(need_import_annotation_labels) == 0:
            return
        for label in need_import_annotation_labels:
            try:
                resp = self.annotation_client.create_annotation_label(
                    workspace_id=label.get("workspace_id"),
                    project_name=label.get("project_name"),
                    annotation_set_name=label.get("annotation_set_name"),
                    local_name=label.get("local_name"),
                    display_name=label.get("display_name"),
                    color=label.get("color")
                    )
                bcelogger.info("import label resp:{}".format(resp))
            except Exception as e:
                bcelogger.error("import label exception.label:{}".format(label), e)
                err_msg = "标注集标签导入错误({})，请检查标注信息".format(label.get("display_name"))
                self.update_annotation_job(err_msg=err_msg)
                raise Exception("import label exception." + err_msg)


    def update_annotation_job(self, err_msg):
        """
                更新标注任务状态
                """
        job_name = self.config.job_name
        bcelogger.info("update job name is {}".format(job_name))
        client_job_name = parse_job_name(self.config.job_name)
        update_job_resp = self.train_client.update_job(
            workspace_id=client_job_name.workspace_id,
            project_name=client_job_name.project_name,
            local_name=client_job_name.local_name,
            tags={"errMsg": err_msg},
        )
        bcelogger.info("update job resp is {}".format(update_job_resp))

