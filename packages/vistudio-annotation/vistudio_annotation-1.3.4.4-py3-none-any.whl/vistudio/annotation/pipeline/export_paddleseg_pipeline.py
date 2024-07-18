#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   export_pipeline.py
"""
import sys
import os

from ray.data import read_datasource
__work_dir__ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, __work_dir__)
from windmillcomputev1.filesystem import S3BlobStore, blobstore, init_py_filesystem
from windmilltrainingv1.client.training_api_dataset import DatasetName
from windmillartifactv1.client.artifact_client import ArtifactClient

from vistudio.annotation.datasink.filename_provider import MultiFilenameProvider
from vistudio.annotation.datasink.csv_datasink import exclude_csv_header_func
from vistudio.annotation.config.arg_parser import ArgParser
from vistudio.annotation.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio.annotation.processor.exporter.paddleseg.cityscape_preprocessor import PaddleSegFormatPreprocessor
from vistudio.annotation.processor.cutter.cut_preprocessor import VistudioCutterPreprocessor
import bcelogger



class ExportPaddleSegPipeline(BaseExportPipeline):
    """
    exporter PaddleClas pipeline
    """

    def __init__(self, args: dict()):
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
        pipeline_cityscape
        :return:
        """
        # step 1: datasource
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
        path = location[len("s3://"):].strip("/")
        bcelogger.info("create windmill location. location= {}".format(location))

        # step 2: split
        if self.split is not None:
            cut_preprocessor = VistudioCutterPreprocessor(self.config, location, self.split)
            ds = cut_preprocessor.transform(ds)
            # ds_list = ds.take_all()
            # print("-----ds split:----", ds_list)      
        # step 3: transform
        paddleseg_format_preprocessor = PaddleSegFormatPreprocessor(config=self.config,
                                                                      merge_labels=self.merge_labels,
                                                                      location=path,
                                                                      labels=self.labels)
        format_ds = paddleseg_format_preprocessor.transform(ds)
        # bcelogger.info("format dataset.dataset count = {}".format(format_ds.count()))

        # 第三步 写入文件
        # 写入 annotation.txt
        annotation_filename_provider = MultiFilenameProvider(file_name="annotation.txt")
        path = location[len("s3://"):].strip("/")

        format_ds.write_csv(path=path,
                            filesystem=self._py_fs,
                            filename_provider=annotation_filename_provider,
                            arrow_csv_args_fn=lambda: exclude_csv_header_func())

        label_txt_full_path = os.path.join(location_resp.location, "labels.txt")
        self.save_label_file(file_path=label_txt_full_path, labels=self.labels, start_index=1)
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
    pipeline = ExportPaddleSegPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)


