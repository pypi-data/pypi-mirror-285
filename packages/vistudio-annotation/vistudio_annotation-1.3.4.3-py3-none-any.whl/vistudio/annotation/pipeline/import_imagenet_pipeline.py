#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
import_imagnet_pipeline.py
"""
import pandas as pd
import ray.data
import sys
import os

__work_dir__ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, __work_dir__)
from vistudio.annotation.processor.importer.zip.zip_preprocessor import ZipFormatPreprocessor

from vistudio.annotation.client.annotation_client import AnnotationClient
from vistudio.annotation.processor.importer.annoation.imagenet_preprocessor import ImageNetFormatPreprocessor
from vistudio.annotation.processor.importer.label.label_preprocessor import LabelFormatPreprocessor

from vistudio.annotation.config.arg_parser import ArgParser
from vistudio.annotation.operator.reader import Reader
from vistudio.annotation.processor.importer.annoation.coco_preprocessor import CocoFormatPreprocessor
from vistudio.annotation.processor.importer.image.image_preprocessor import ImageFormatterPreprocessor

from vistudio.annotation.pipeline.base_import_pipeline import BaseImportPipline
import argparse
import bcelogger


class ImportImageNetPipeline(BaseImportPipline):
    """
    ImportImageNetPipeline
    """

    def __init__(self, args):
        super().__init__(args)

    def _import_image(self):
        """
        importer image
        :return:
        """

        # 读取图片
        imagenet_reader = Reader(filesystem=self.config.filesystem, annotation_set_id=self.annotation_set_id)
        if self.file_format == 'zip':
            zip_file_uris = imagenet_reader.get_zip_file_uris(data_uri=self.data_uri)
            if len(zip_file_uris) > 0:
                zip_formatter = ZipFormatPreprocessor(config=self.config)
                self.data_uri = zip_formatter.fit(ds=ray.data.from_items(zip_file_uris)).stats_
        file_uris = imagenet_reader.get_file_uris(data_uri=self.data_uri, data_types=self.data_types)
        ds = ray.data.from_items(file_uris)

        bcelogger.info("import imagenet image from json.dataset count = {}".format(ds.count()))

        image_formater = ImageFormatterPreprocessor(config=self.config,
                                                    annotation_set_id=self.annotation_set_id,
                                                    annotation_set_name=self.annotation_set_name,
                                                    tag=self.tag
                                                    )
        final_ds = image_formater.fit(ds).stats_
        bcelogger.info("format dataset.dataset count = {}".format(final_ds.count()))

        # 写入mongo
        final_ds.write_mongo(uri=self.mongo_uri,
                             database=self.config.mongodb_database,
                             collection=self.config.mongodb_collection)

    def _import_annoation(self):
        """
        导入标注文件
        :return:
        """
        # 读取json 文件
        imagenet_reader = Reader(filesystem=self.config.filesystem, annotation_set_id=self.annotation_set_id)

        zip_file_uris = imagenet_reader.get_zip_file_uris(data_uri=self.data_uri)
        if len(zip_file_uris) > 0:
            zip_formatter = ZipFormatPreprocessor(config=self.config)
            self.data_uri = zip_formatter.fit(ds=ray.data.from_items(zip_file_uris)).stats_

        file_uris = imagenet_reader.get_file_uris(data_uri=self.data_uri,
                                                  data_types=self.data_types,
                                                  import_type='imagenet')
        ds = ray.data.from_pandas(pd.DataFrame(file_uris))
        bcelogger.info("import imagenet annotation .dataset count = {}".format(ds.count()))
        label_formater = LabelFormatPreprocessor(config=self.config,
                                                 labels=self.labels,
                                                 annotation_set_id=self.annotation_set_id,
                                                 annotation_set_name=self.annotation_set_name,
                                                 annotation_format=self.annotation_format)

        # 处理 ds，获取annotation
        need_import_annotation_labels = label_formater.fit(ds).stats_
        self._import_labels(need_import_annotation_labels=need_import_annotation_labels)
        bcelogger.info(
            "format imagenet annotation.nned_import_annotation_labels:{}".format(need_import_annotation_labels))
        self.labels = self._get_labels()
        imagenet_preprocessor = ImageNetFormatPreprocessor(config=self.config,
                                                           annotation_set_id=self.annotation_set_id,
                                                           annotation_set_name=self.annotation_set_name,
                                                           labels=self.labels,
                                                           tag=self.tag)
        final_ds_dict = imagenet_preprocessor.fit(ds).stats_
        image_ds = final_ds_dict.get("image_ds")
        annotation_ds = final_ds_dict.get("annotation_ds")
        # 数据入库
        image_ds.write_mongo(uri=self.mongo_uri,
                             database=self.config.mongodb_database,
                             collection=self.config.mongodb_collection)
        annotation_ds.write_mongo(uri=self.mongo_uri,
                                  database=self.config.mongodb_database,
                                  collection=self.config.mongodb_collection)

    def run(self):
        """
        run this piepline
        :return:
        """

        if len(self.data_types) == 1 and self.data_types[0] == "annotation":
            raise Exception("The data_types: '{}' is not support.".format(self.data_types))

        elif len(self.data_types) == 1 and self.data_types[0] == "image":
            self._import_image()

        elif len(self.data_types) == 2 and "image" in self.data_types and "annotation" in self.data_types:
            self._import_annoation()
        else:
            raise Exception("The data_types: '{}' is not support.".format(self.data_types))


def run(args):
    """
    pipeline run
    :param args:
    :return:
    """
    pipeline = ImportImageNetPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Import')
    args = arg_parser.parse_args()
    run(args)

