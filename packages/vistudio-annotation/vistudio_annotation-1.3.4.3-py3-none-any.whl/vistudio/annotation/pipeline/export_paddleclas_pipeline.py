#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   export_pipeline.py
"""

from ray.data.read_api import read_datasource
import ray
import sys
import os

__work_dir__ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, __work_dir__)
from vistudio.annotation.processor.exporter.paddleclas.paddleclas_preprocessor import PaddleClasFormatPreprocessor

from vistudio.annotation.datasink.filename_provider import MultiFilenameProvider
from windmillartifactv1.client.artifact_client import ArtifactClient
from vistudio.annotation.datasink.csv_datasink import exclude_csv_header_func
from windmilltrainingv1.client.training_api_dataset import DatasetName
from vistudio.annotation.processor.cutter.cut_preprocessor import VistudioCutterPreprocessor
from vistudio.annotation.config.arg_parser import ArgParser
import argparse
from vistudio.annotation.pipeline.base_export_pipeline import BaseExportPipeline
import bcelogger

from windmillcomputev1.filesystem import S3BlobStore, blobstore, init_py_filesystem


class ExportPaddleClasPipeline(BaseExportPipeline):
    """
    exporter PaddleClas pipeline
    """

    def __init__(self, args):

        super().__init__(args)
        self.bs = blobstore(filesystem=self.config.filesystem)
        self.artifact_client = ArtifactClient(
            endpoint=self.config.windmill_endpoint,
            ak=self.config.windmill_ak,
            sk=self.config.windmill_sk
        )
        self._py_fs = init_py_filesystem(self.config.filesystem)


    def run(self, parallelism: int = 10):
        """
        pipeline_imagenet
        :return:
        """
        # 第一步 datasource 算子
        ds = read_datasource(self.datasource, parallelism=parallelism)
        bcelogger.info("read data from mongo.dataset count = {}".format(ds.count()))
        if ds.count() <= 0:
            return

        dataset_name = DatasetName(workspace_id=self.dataset.get('workspaceID'),
                                   project_name=self.dataset.get('projectName'),
                                   local_name=self.dataset.get('localName'))
        object_name = dataset_name.get_name()
        location_resp = self.artifact_client.create_location(
            object_name=object_name
        )
        location = location_resp.location
        bcelogger.info("create windmill location. location= {}".format(location))

        # step 2: split
        if self.split is not None:
            cut_preprocessor = VistudioCutterPreprocessor(self.config, location, self.split)
            ds = cut_preprocessor.transform(ds)


        # 第二步 merger 算子 和 formatter 算子
        paddleclas_format_preprocessor = PaddleClasFormatPreprocessor(labels=self.labels,
                                                                  merge_labels=self.merge_labels)
        formater_ds = paddleclas_format_preprocessor.transform(ds)
        # bcelogger.info("format dataset.dataset count = {}".format(formater_ds.count()))

        # 第三步 writer 算子
        # 写入 annotation.txt
        path = location[len("s3://"):].strip("/")
        bcelogger.info("create windmill location. location= {}".format(path))

        annotation_filename_provider = MultiFilenameProvider(file_name="annotation.txt")

        formater_ds.write_csv(path=path,
                              filesystem=self._py_fs,
                              filename_provider=annotation_filename_provider,
                              arrow_csv_args_fn=lambda: exclude_csv_header_func())

        label_txt_full_path = os.path.join(location_resp.location, "labels.txt")
        self.save_label_file(file_path=label_txt_full_path, labels=self.labels, start_index=0)

        # 第四步 生成dataset
        self.create_dataset(location=location_resp.location,
                              annotation_format=self.annotation_format,
                              dataset=self.dataset)


def run(args):
    """
    main
    :param args:
    :return:
    """
    pipeline = ExportPaddleClasPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)

