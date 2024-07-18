#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   update_annotation_state_pipeline.py
"""
import os
import pyarrow as pa
import ray
import bcelogger
from pymongoarrow.api import Schema
from ray.data.read_api import read_datasource
from vistudio.annotation.config.config import Config
from vistudio.annotation.datasource.sharded_mongo_datasource import get_mongo_datasource
from vistudio.annotation.processor.updater.annotation_state_preprocessor import AnnotationStateUpdaterPreprocessor
from vistudio.annotation.pipeline.base import BasePipeline


class UpdateAnnotationStatePipeline(BasePipeline):
    """
    update annotation state
    """
    def __init__(self, config, **options):
        super().__init__(config, **options)
        self.parallelism = options.get("parallelism", 10)

    def run(self):
        """
        run this piepline
        """
        # 第1步 拿到Init的数据
        pipeline = [
            {"$match": {
                "data_type": "Image",
                "annotation_state": {"$exists": False},
            }},
            {"$sort": {"created_at": 1}},
            {"$limit": 10000}
        ]
        schema = Schema({
            "data_type": pa.string(),
            "image_id": pa.string(),
            "annotation_set_id": pa.string(),
            "annotation_state": pa.string(),
        })

        datasource = get_mongo_datasource(config=self.config, pipeline=pipeline, schema=schema)
        ds = read_datasource(datasource, parallelism=self.parallelism)

        if ds.count() <= 0:
            bcelogger.info(f"update annotation state count zero")
            return

        # 第2步 查找task_kind为Manual的数据，并更新annotation_state
        update_anno_status = AnnotationStateUpdaterPreprocessor(config=self.config)
        u_ds = update_anno_status.transform(ds)

        bcelogger.info(f"update annotation state count: {u_ds.count()}")


def test_ppl():
    """
    main function
    :return:
    """
    args = {
        "mongo_user": os.environ.get('MONGO_USER', 'root'),
        "mongo_password": os.environ.get('MONGO_PASSWORD', 'mongo123#'),
        "mongo_host": os.environ.get('MONGO_HOST', '10.27.240.45'),
        "mongo_port": int(os.environ.get('MONGO_PORT', 8719)),
        "mongo_database": os.environ.get('MONGO_DB', 'annotation'),
        "mongo_collection": os.environ.get('MONGO_COLLECTION', 'annotation'),
    }
    config = Config(args)

    pipeline = UpdateAnnotationStatePipeline(config=config, parallelism=10, args=None)
    pipeline.run()


if __name__ == '__main__':
    test_ppl()