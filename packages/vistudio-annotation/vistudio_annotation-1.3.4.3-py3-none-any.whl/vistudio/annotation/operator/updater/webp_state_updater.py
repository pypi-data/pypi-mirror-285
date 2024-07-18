#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   webp_state_updater.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""
import time

from pandas import DataFrame

from vistudio.annotation.operator.updater.base_mongo_updater import BaseMongoUpdater
from vistudio.annotation.table.image import ImageData, DATA_TYPE_IMAGE


class WebpStateUpdater(BaseMongoUpdater):
    """
    WebpStateUpdater
    """
    def update_webp_state(self, source: DataFrame) -> DataFrame:
        """
        update webp_state
        """
        for source_index, source_row in source.iterrows():
            ImageData.objects(image_id=source_row['image_id'],
                              annotation_set_id=source_row['annotation_set_id'],
                              data_type=DATA_TYPE_IMAGE).\
                update_one(set__image_state__webp_state=source_row['webp_state'],
                           set__updated_at=time.time_ns())

        return source
