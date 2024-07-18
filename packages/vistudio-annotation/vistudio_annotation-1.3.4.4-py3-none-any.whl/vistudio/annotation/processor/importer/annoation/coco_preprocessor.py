#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   formater.py
"""
from typing import Union, Dict, Any

from ray.data.preprocessor import Preprocessor
from windmilltrainingv1.client.training_api_job import parse_job_name

from vistudio.annotation.config.config import Config
from vistudio.annotation.datasource.sharded_mongo_datasource import get_mongo_collection, _get_exist_images, \
    _get_exist_annoation
from vistudio.annotation.operator.coco_formatter import CocoFormatter
from windmilltrainingv1.client.training_client import TrainingClient
import logit

from vistudio.annotation.operator.filter import Filter

logit.base_logger.setup_logger({})

image_extensions = ('.jpeg', '.jpg', '.png', '.bmp')
job_name_pattern = r"workspaces/(?P<workspace_id>[^/]+)/projects/(?P<project_name>[^/]+)/jobs/(?P<job_name>[^/]+)$"
time_pattern = "%Y-%m-%dT%H:%M:%SZ"


class CocoFormatPreprocessor(Preprocessor):
    """
    CocoFormatPreprocessor
    """

    def __init__(self,
                 config: Config,
                 labels: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 data_uri: str = "",
                 data_types: list() = None,
                 tag: Union[Dict] = None
                 ):
        self._is_fittable = True
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_types = data_types
        self.labels = labels
        self.tag = tag
        self.train_client = TrainingClient(endpoint=config.windmill_endpoint,
                                           ak=config.windmill_ak,
                                           sk=config.windmill_sk)
        self.exist_images = _get_exist_images(config=self.config,
                                              annotation_set_id=self.annotation_set_id)  # 已经存在的图片，用于过滤
        self.exist_annotations = _get_exist_annoation(config=self.config,
                                                      annotation_set_id=self.annotation_set_id)  # 已经存在的标注，用于过滤

    def _update_annotation_job(self, err_msg):
        """
        更新标注任务状态
        """
        job_name = self.config.job_name
        logit.info("update job name is {}".format(job_name))
        client_job_name = parse_job_name(self.config.job_name)
        update_job_resp = self.train_client.update_job(
            workspace_id=client_job_name.workspace_id,
            project_name=client_job_name.project_name,
            local_name=client_job_name.local_name,
            tags={"errMsg": err_msg},
        )
        logit.info("update job resp is {}".format(update_job_resp))

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return:
        """
        filter = Filter(labels=self.labels)

        coco_formatter = CocoFormatter(
            labels=self.labels,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            data_uri=self.data_uri,
            data_types=self.data_types,
            user_id=self.config.user_id,
            org_id=self.config.org_id,
            tag=self.tag

        )
        format_ds_dict = coco_formatter.to_vistudio_v1(ds=ds)
        image_ds = format_ds_dict.get("image_ds")
        annotation_ds = format_ds_dict.get("annotation_ds")
        filter = Filter(labels=self.labels)
        filter_image_ds = filter.filter_image(source=image_ds, existed_images=self.exist_images)
        logit.info("filter coco image ds.filter_image_ds count={}".format(filter_image_ds.count()))
        filter_annotation_ds = filter.filter_annotation(source=annotation_ds,
                                                        existed_annotations=self.exist_annotations)
        logit.info("filter coco annotation ds.filter_annotation_ds count={}".format(filter_annotation_ds.count()))
        self.stats_ = {"image_ds": filter_image_ds, "annotation_ds": filter_annotation_ds}
        return self


