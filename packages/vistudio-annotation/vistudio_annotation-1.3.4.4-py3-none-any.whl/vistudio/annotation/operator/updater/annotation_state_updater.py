#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   annotation_state_updater.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""
import time

from pandas import DataFrame

from vistudio.annotation.operator.updater.base_mongo_updater import BaseMongoUpdater
from vistudio.annotation.table.annotation import AnnotationData, DATA_TYPE_ANNOTATION, TASK_KIND_MANUAL
from vistudio.annotation.table.image import ImageData, DATA_TYPE_IMAGE, ANNOTATION_STATE_ANNOTATED, \
    ANNOTATION_STATE_UNANNOTATED


class AnnotationStateUpdater(BaseMongoUpdater):
    """
    AnnotationStateUpdater
    """
    def update_annotation_state(self, source: DataFrame) -> DataFrame:
        """
        update annotation_state
        """
        for source_index, source_row in source.iterrows():
            annotation_count = AnnotationData.objects(
                image_id=source_row['image_id'],
                annotation_set_id=source_row['annotation_set_id'],
                data_type=DATA_TYPE_ANNOTATION,
                task_kind=TASK_KIND_MANUAL
            ).count()
            if annotation_count == 0:
                ImageData.objects(
                    image_id=source_row['image_id'],
                    annotation_set_id=source_row['annotation_set_id'],
                    data_type=DATA_TYPE_IMAGE,
                ).update_one(
                    __raw__={"$set": {"annotation_state": ANNOTATION_STATE_UNANNOTATED, "updated_at": time.time_ns()}}
                )
            else:
                ImageData.objects(
                    image_id=source_row['image_id'],
                    annotation_set_id=source_row['annotation_set_id'],
                    data_type=DATA_TYPE_IMAGE,
                ).update_one(
                    __raw__={"$set": {"annotation_state": ANNOTATION_STATE_ANNOTATED, "updated_at": time.time_ns()}}
                )

        return source