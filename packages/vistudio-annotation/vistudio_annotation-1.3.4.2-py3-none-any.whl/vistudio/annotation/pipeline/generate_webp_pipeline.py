#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   generate_webp_pipeline.py
"""
import ray
import pyarrow as pa
import os
import bcelogger
from pymongoarrow.api import Schema
from ray.data.read_api import read_datasource
from vistudio.annotation.config.config import Config
from vistudio.annotation.datasource.sharded_mongo_datasource import get_mongo_datasource
from vistudio.annotation.processor.generator.webp_preprocessor import WebpGeneratorPreprocessor
from vistudio.annotation.processor.updater.webp_state_preprocessor import WebpStateUpdaterPreprocessor
from vistudio.annotation.pipeline.base import BasePipeline


class GenerateWebpPipeline(BasePipeline):
    """
    GenerateWebpPipeline
    """
    def __init__(self, config, **options):
        super().__init__(config, **options)
        self.parallelism = options.get("parallelism", 10)

    def run(self):
        """
        run this piepline
        """
        # 第一步 查找Init的图像

        pipeline = [
            { "$match": {
                "data_type": "Image",
                "image_state.webp_state": { "$exists": False },
            }},
            { "$sort": { "created_at": -1 } },
            { "$limit": 10000 }
        ]
        schema = Schema({
            "image_id": pa.string(),
            "annotation_set_id": pa.string(),
            "annotation_set_name": pa.string(),
            "file_uri": pa.string(),
            "org_id": pa.string(),
            "user_id": pa.string(),
            })

        datasource = get_mongo_datasource(config=self.config, pipeline=pipeline, schema=schema)
        ds = read_datasource(datasource, parallelism=self.parallelism)

        if ds.count() <= 0:
            return

        # 第二步 生成webp
        webp_generator = WebpGeneratorPreprocessor(self.config.windmill_endpoint)
        webp_ds = webp_generator.transform(ds)

        # 第三步 更新mongodb
        webp_updater = WebpStateUpdaterPreprocessor(self.config)
        update_ds = webp_updater.transform(webp_ds)

        bcelogger.info(f"update webp count: {update_ds.count()}")


def test_ppl():
    """
    test ppl
    """
    args = {
        "mongo_user": os.environ.get('MONGO_USER', 'root'),
        "mongo_password": os.environ.get('MONGO_PASSWORD', 'mongo123#'),
        "mongo_host": os.environ.get('MONGO_HOST', '10.27.240.45'),
        "mongo_port": int(os.environ.get('MONGO_PORT', 8719)),
        "mongo_database": os.environ.get('MONGO_DB', 'annotation'),
        "mongo_collection": os.environ.get('MONGO_COLLECTION', 'annotation'),
        "windmill_endpoint": os.environ.get('WINDMILL_ENDPOINT', 'http://10.27.240.45:8340')
    }
    config = Config(args)

    pipeline = GenerateWebpPipeline(config=config, parallelism=10)
    pipeline.run()


if __name__ == '__main__':
    test_ppl()