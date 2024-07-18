#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@file: export_vistudio_pipeline.py
"""
import bcelogger
from ray.data.read_api import read_datasource


from windmillcomputev1.filesystem import init_py_filesystem
from windmillartifactv1.client.artifact_client import ArtifactClient
from windmilltrainingv1.client.training_api_dataset import DatasetName

from .base_export_pipeline import BaseExportPipeline
from vistudio.annotation.datasink.filename_provider import MultiFilenameProvider
from vistudio.annotation.config.arg_parser import ArgParser


class ExportVistudioPipeline(BaseExportPipeline):
    """
    exporter vistudio pipeline
    """

    def __init__(self, args):
        super().__init__(args)
        self._py_fs = init_py_filesystem(self.config.filesystem)
        self.artifact_client = ArtifactClient(
            endpoint=self.config.windmill_endpoint,
            ak=self.config.windmill_ak,
            sk=self.config.windmill_sk
        )

    def run(self, parallelism: int = 10):
        """
        :return:
        """

        dataset_name = DatasetName(workspace_id=self.dataset.get('workspaceID'),
                                   project_name=self.dataset.get('projectName'),
                                   local_name=self.dataset.get('localName'))
        object_name = dataset_name.get_name()
        location_resp = self.artifact_client.create_location(
            object_name=object_name
        )
        location = location_resp.location

        # writer labels
        path = location + "/" + "meta.json"
        self.save_vistuido_meta_json_file(file_path=path, labels=self.labels)

        # step 1: datasource
        ds = read_datasource(self.datasource, parallelism=parallelism)
        bcelogger.info("read data from mongo.dataset count = {}".format(ds.count()))
        if ds.count() <= 0:
            return

        path = location[len("s3://"):].strip("/") + "/" + "jsonls"

        # writer
        image_ds = ds.map(lambda row: {k: v for k, v in row.items() if k != "annotations"})
        bcelogger.info("-----image ds count = {}".format(image_ds.count()))
        image_provider = MultiFilenameProvider(file_name="image.jsonl")
        image_ds.write_json(path=path,
                            filesystem=self._py_fs,
                            filename_provider=image_provider)

        anno_ds = ds.flat_map(expand_annotations)
        bcelogger.info("-----annotation ds count = {}".format(anno_ds.count()))
        anno_provider = MultiFilenameProvider(file_name="prediction.jsonl")
        anno_ds.write_json(path=path,
                            filesystem=self._py_fs,
                            filename_provider=anno_provider)


        # 生成dataset
        self.create_dataset(location=location_resp.location,
                            annotation_format=self.annotation_format,
                            dataset=self.dataset)


# 展开labels字段并返回每个label元素
def expand_annotations(row):
    return row["annotations"]


def run(args):
    """
    main
    :param args:
    :return:
    """
    pipeline = ExportVistudioPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)

