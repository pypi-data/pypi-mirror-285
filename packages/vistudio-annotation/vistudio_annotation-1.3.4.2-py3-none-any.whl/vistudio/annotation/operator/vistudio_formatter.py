#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   reader.py
"""
import os
import bcelogger
import time
import pandas as pd
from typing import Union, Dict, Any, List
from ray.data import DataContext

from vistudio.annotation.util import string

annotation_schemas = [
    'artifact_name',
    'data_type',
    'task_kind',
    'annotations',
    'image_id',
    'user_id',
    'created_at',
    'annotation_set_id'
]

image_schemas = [
    'annotation_set_id',
    'user_id',
    'created_at',
    'data_type',
    'annotation_set_name',
    'file_uri',
    'image_id',
    'image_name',
    'org_id',
    'height',
    'width',
    'tags'
]
ctx = DataContext.get_current()
ctx.enable_tensor_extension_casting = False


class VistudioFormatter(object):
    """
    VistudioFormatter
    """
    def __init__(self,
                 labels: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 data_uri: str = None,
                 data_type: str = None,
                 user_id: str = None,
                 org_id: str = None,
                 tag: Union[Dict] = None
                 ):
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_type = data_type
        self.labels = labels
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag

    @staticmethod
    def _flat(row: Dict[str, Any], col: str) -> List[Dict[str, Any]]:
        """
         Expand the col column
        :param col:
        :return: List
        """
        # ray.util.pdb.set_trace()
        return row[col]

    def _fill_image_info_vistudio(self, row: Dict[str, Any]):
        """
        fill vistudio image info
        :param row:
        :return:
        """
        file_uri = row.get("file_uri", None)
        if file_uri is None:
            file_uri = os.path.join(self.data_uri, "images", row['image_name'])
        else:
            if "s3://" in row['file_uri']:
                file_uri = row['file_uri']
            else:
                file_uri = os.path.join(self.data_uri, "images", row['image_name'])

        image_id = row.get("image_id", None)
        if image_id is None or image_id == "":
            image_id = string.generate_md5(row['image_name'])

        tags = row.get("tags", {})

        item = {
            "annotation_set_id": self.annotation_set_id,
            "user_id": self.user_id,
            "created_at": time.time_ns(),
            "data_type": "Image",
            "annotation_set_name": self.annotation_set_name,
            "file_uri": file_uri,
            "image_id": image_id,
            "image_name": row['image_name'],
            "org_id": self.org_id,
            "height": 0,
            "width": 0,
            "tags": tags
        }
        if self.tag is not None and len(self.tag) > 0:
            item['tags'] = self.tag
        return item

    def images_to_vistudio_v1(self, ds: "Dataset") -> "Dataset":
        """
        images_to_vistudio_v1
        :param ds: Dataset
        :return: Dataset
        """

        bcelogger.info("import vistudio flat image.original_image_ds count={}".format(ds.count()))
        image_cols = ds.columns()
        not_in_cols = [col for col in image_cols if col not in image_schemas] if image_cols is not None else []
        if len(not_in_cols) > 0:
            image_ds = ds.drop_columns(cols=not_in_cols)
        else:
            image_ds = ds
        image_ds = image_ds.map(lambda row: self._fill_image_info_vistudio(row=row))
        bcelogger.info("import vistudio flat image.final_image_ds count={}".format(image_ds.count()))
        return image_ds

    @staticmethod
    def _fill_image_id(df: pd.DataFrame):
        df['image_id'] = df['image_name'].apply(string.generate_md5)
        return df['image_id']

    def annotations_to_vistudio_v1(self, ds: "Dataset") -> "Dataset":
        """
        annotations_to_vistudio_v1
        :param ds: Dataset
        :return: Dataset
        """
        bcelogger.info("import vistudio annotation.original_annotation_ds count={}".format(ds.count()))
        anno_cols = ds.columns()
        not_in_cols = [col for col in anno_cols if col not in annotation_schemas] if anno_cols is not None else []
        if len(not_in_cols) > 0:
            anno_ds = ds.drop_columns(cols=not_in_cols)
        else:
            anno_ds = ds
        now = time.time_ns()
        anno_ds = anno_ds.add_column('annotation_set_id', lambda df: self.annotation_set_id) \
            .add_column('created_at', lambda df: now) \
            .add_column('user_id', lambda df: self.user_id)
        bcelogger.info("import vistudio annotation.final_annotation_ds count={}".format(anno_ds.count()))
        return anno_ds

    def to_vistudio_v1(self, ds: "Dataset") -> "Dataset":
        """
        to_vistudio_v1
        :param ds: Dataset
        :return: Dataset
        """
        if self.data_type == "Image":
            return self.images_to_vistudio_v1(ds=ds)
        else:
            return self.annotations_to_vistudio_v1(ds=ds)



