#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   webp_state_updater.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""
import time
from pandas import DataFrame
from pymongo import MongoClient


class WebpStateUpdater(object):
    """
    WebpStateUpdater
    """

    def __init__(self, config):
        self.config = config

    def update_webp_state(self, source: DataFrame) -> DataFrame:
        """
        update webp_state
        """
        mongo_client = MongoClient(self.config.mongo_uri)
        mongo = mongo_client[self.config.mongodb_database][self.config.mongodb_collection]

        for source_index, source_row in source.iterrows():
            update = {
                "$set": {
                    "image_state.webp_state": source_row['webp_state'],
                    "updated_at": time.time_ns(),
                }
            }

            query = {
                "image_id": source_row['image_id'],
                "annotation_set_id": source_row['annotation_set_id'],
                "data_type": "Image"
            }
            _ = mongo.update_many(query, update)

        return source