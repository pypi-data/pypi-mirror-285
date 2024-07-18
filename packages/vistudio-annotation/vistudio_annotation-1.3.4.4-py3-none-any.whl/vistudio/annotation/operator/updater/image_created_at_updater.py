#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   image_created_at_updater.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""

import time
import bcelogger
from pandas import DataFrame

from vistudio.annotation.operator.updater.base_mongo_updater import BaseMongoUpdater
from vistudio.annotation.table.annotation import AnnotationData, DATA_TYPE_ANNOTATION
from vistudio.annotation.table.image import ImageData, DATA_TYPE_IMAGE, ANNOTATION_STATE_ANNOTATED, \
    ANNOTATION_STATE_UNANNOTATED


class ImageCreatedAtUpdater(BaseMongoUpdater):
    """
    ImageCreatedAtUpdater
    """
    def update_image_created_at(self, source: DataFrame) -> DataFrame:
        """
        update image_created_at
        """
        for source_index, source_row in source.iterrows():      
            image = ImageData.objects(image_id=source_row['image_id'],
                                      annotation_set_id=source_row['annotation_set_id'],
                                      data_type=DATA_TYPE_IMAGE).first()
            if image is None:
                continue

            if image.annotation_state is None or image.annotation_state == ANNOTATION_STATE_UNANNOTATED:
                ImageData.objects(image_id=source_row['image_id'],
                                  annotation_set_id=source_row['annotation_set_id'],
                                  data_type=DATA_TYPE_IMAGE).update(annotation_state=ANNOTATION_STATE_ANNOTATED)

            AnnotationData.objects(image_id=source_row['image_id'], annotation_set_id=source_row['annotation_set_id'],
                                   data_type=DATA_TYPE_ANNOTATION).update(
                image_created_at=image.created_at, updated_at=time.time_ns())

        return source
