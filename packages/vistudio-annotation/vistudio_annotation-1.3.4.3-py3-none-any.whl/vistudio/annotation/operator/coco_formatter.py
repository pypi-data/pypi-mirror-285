#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   coco_preprocessor.py
"""
import re
import time
from typing import Union, Dict, Any, List
from pandas import DataFrame
import pandas as pd
import os

from ray.data import Dataset
from windmilltrainingv1.client.training_api_job import parse_job_name
import logit
import numpy as np

from vistudio.annotation.util import string

logit.base_logger.setup_logger({})
import ray


class CocoFormatter(object):
    """
    CocoFormatter
    """

    def __init__(self,
                 labels: Union[Dict],
                 merge_labels: Union[Dict] = None,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 data_uri: str = None,
                 data_types: list() = None,
                 user_id: str = None,
                 org_id: str = None,
                 tag: Union[Dict] = None
                 ):
        self._labels = labels
        self.merge_labels = merge_labels
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_types = data_types
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag

    def images_from_vistudio_v1(self, source: DataFrame) -> list():
        """
        image_from_vistudio_v1
        :param source:
        :return:
        """
        images = list()
        filenames = list()
        for source_index, source_row in source.iterrows():
            file_name = source_row['file_uri']
            image_height = source_row['height']
            image_width = source_row['width']
            filenames.append(file_name)

            image_id = int(source_row['image_id'], 16)
            images.append({
                "file_name": file_name,
                "height": int(image_height),
                "width": int(image_width),
                "id": image_id
            })
        return images

    def annotations_from_vistudio_v1(self, source: DataFrame) -> list:
        """
        annotation_from_vistudio_v1
        :param source:
        :return:
        """
        results = list()
        for source_index, source_row in source.iterrows():
            image_id = int(source_row['image_id'], 16)
            for image_annotation in source_row.get('annotations'):
                task_kind = image_annotation['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = image_annotation['annotations']
                if annotations is None or len(annotations) == 0:
                    continue

                for annotation in annotations:
                    bbox = annotation.get('bbox', [])
                    n_bbox = [int(element) for element in bbox]
                    area = annotation.get('area', 0)
                    seg = annotation.get('segmentation', [])
                    n_seg = [int(element) for element in seg]

                    labels = annotation['labels']
                    if labels is None or len(labels) == 0:
                        continue

                    label_id = str(labels[0]['id'])
                    if label_id not in self._labels:
                        continue
                    if self.merge_labels is not None and label_id in self.merge_labels:
                        label_id = self.merge_labels[label_id]
                    md5_data = {
                        "image_id": image_id,
                        "bbox": bbox,
                        "area": area,
                        "iscrowd": 0,
                        "category_id": int(label_id),
                        "segmentation": seg,
                        "time": time.time_ns()
                    }
                    results.append({
                        "id": int(string.generate_md5(str(md5_data)), 16),
                        "image_id": image_id,
                        "bbox": n_bbox,
                        "area": int(area),
                        "iscrowd": 0,
                        "category_id": int(label_id),
                        "segmentation": n_seg,
                    })

        return results

    def categories_from_vistudio_v1(self):
        """
        categories_from_vistudio_v1
        :return:
        """

        cs = list()
        if self._labels is not None:
            for label_id, label_name in self._labels.items():
                item = {
                    "id": int(label_id),
                    "name": label_name
                }
                cs.append(item)

        return cs

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source: DataFrame
        :return: DataFrame
        """

        results = [{
            "images": self.images_from_vistudio_v1(source=source),
            "annotations": self.annotations_from_vistudio_v1(source=source),
            "categories": self.categories_from_vistudio_v1()
        }]
        return pd.DataFrame(results)

    def merge(self, rows: DataFrame) -> DataFrame:
        """
        merge
        :param rows: DataFrame
        :return: DataFrame
        """
        images = rows['images'].sum()
        annotations = rows['annotations'].sum()
        categories = self.categories_from_vistudio_v1()
        results = [{
            "images": images,
            "annotations": annotations,
            "categories": categories
        }]
        return pd.DataFrame(results)

    def _get_image_uri(self):
        if len(self.data_types) == 2 and "image" in self.data_types and "annotation" in self.data_types:
            image_uri_prefix = os.path.join(self.data_uri, "images")
        else:
            image_uri_prefix = ''
        return image_uri_prefix

    @staticmethod
    def _flat(row: Dict[str, Any], col: str) -> List[Dict[str, Any]]:
        """
         Expand the col column
        :param col:
        :return: List
        """
        # ray.util.pdb.set_trace()
        return row[col]

    def _group_by_image_id(self, group: pd.DataFrame) -> pd.DataFrame:
        """
        group bu image_id
        :param group:
        :return:
        """
        image_id = group["image_id"][0]
        ids = group["id"].tolist()
        annoations = list()
        for i in range(len(ids)):
            id = ids[i]
            bbox = group["bbox"].tolist()[i]
            segmentation = group["segmentation"].tolist()[i]
            import numpy as np
            rle = {}
            seg_arr = []
            is_rle = False
            if type(segmentation) == list:
                seg_arr = np.array(segmentation).flatten()
            elif type(segmentation) == dict:
                rle_counts = segmentation.get('counts', None)
                if rle_counts is not None:
                    rle = segmentation
                    is_rle = True

            area = group["area"].tolist()[i]
            cate = group["category_id"].tolist()[i]
            iscrowd = group["iscrowd"].tolist()[i]
            anno = {
                "id": str(id),
                "bbox": bbox,
                "segmentation": seg_arr,
                "area": area,
                "labels": [{
                    "id": str(cate),
                    "confidence": 1
                }],
                "iscrowd": iscrowd,

            }
            if len(rle) > 0:
                anno['rle'] = rle
            annoations.append(anno)

        annoation_res = {
            "image_id": image_id,
            "user_id": self.user_id,
            "created_at": time.time_ns(),
            "annotations": [annoations],
            "data_type": "Annotation",
            "annotation_set_id": self.annotation_set_id,
            "task_kind": "Manual",
            "artifact_name": ""
        }

        return pd.DataFrame(annoation_res)

    def _fill_image_info_coco(self, row: Dict[str, Any], image_uri_prefix: str):
        """
        fill coco image info
        :param row:
        :param image_ids:
        :return:
        """
        row['image_id'] = string.generate_md5(row['file_name'])
        row['image_name'] = os.path.basename(row['file_name'])
        row['annotation_set_id'] = self.annotation_set_id
        row['annotation_set_name'] = self.annotation_set_name
        row['user_id'] = self.user_id
        row['created_at'] = time.time_ns()
        row['data_type'] = 'Image'
        row['file_uri'] = os.path.join(image_uri_prefix, row['file_name'])
        row['org_id'] = self.org_id
        if self.tag is not None and len(self.tag) > 0:
            row['tags'] = self.tag
        return row

    @staticmethod
    def _fill_data(row: Dict[str, Any]) -> Dict[str, Any]:
        row["segmentation"] = row.get("segmentation", [])
        row["bbox"] = row.get("bbox", [])
        row["area"] = row.get("area", '')
        row["iscrowd"] = row.get("area", '')

        return row

    def to_vistudio_v1(self, ds: Dataset) -> Dict[str, Dataset]:

        """
        _fit_coco
        :param ds: Dataset
        :return: Dataset
        """
        image_uri_prefix = self._get_image_uri()
        # 展开 images
        image_ds = ds.flat_map(lambda row: self._flat(row=row, col="images"))
        logit.info("import coco flat image.original_image_ds count={}".format(image_ds.count()))

        ori_df = image_ds.to_pandas()
        image_drop_duplicates_ds = ray.data.from_pandas(ori_df.drop_duplicates(subset=['file_name']))
        logit.info("import coco flat image.image_drop_duplicates_ds count={}".format(image_drop_duplicates_ds.count()))

        # 展开 annoations
        annoation_ds = ds.flat_map(lambda row: self._flat(row=row, col="annotations")) \
            .map(lambda row: self._fill_data(row=row))
        logit.info("import coco flat annotation.origin_annoation_ds count={}".format(annoation_ds.count()))

        # merge image_ds and annoation_ds on annoation_ds.image_id = image_ds.id
        drop_id_annotaion_ds = annoation_ds.drop_columns(cols=['id'])
        image_df = image_drop_duplicates_ds.to_pandas()
        annotation_df = drop_id_annotaion_ds.to_pandas()
        merged_df = pd.merge(annotation_df, image_df, left_on='image_id', right_on='id')

        bboxs = merged_df['bbox'].tolist()
        segmentation = merged_df['segmentation'].tolist()
        if bboxs is not None:
            normal_bbox_list = [arr.tolist() for arr in bboxs if arr is not None]
            if len(normal_bbox_list) > 0:
                merged_df['bbox'] = normal_bbox_list

        if segmentation is not None:
            normal_segmentation_list = list()
            for seg in segmentation:
                if seg is None:
                    continue
                if type(seg) == list or type(seg) == np.ndarray:
                    normal_segmentation_list.append(seg.tolist())
                elif type(seg) == dict:
                    normal_segmentation_list.append(seg)
            if len(normal_segmentation_list) > 0:
                merged_df['segmentation'] = normal_segmentation_list

        merged_df['image_id'] = merged_df['file_name'].apply(lambda x: string.generate_md5(x))
        merged_df = merged_df.drop(columns=['file_name', 'height', 'width'])

        droped_annoation_ds = ray.data.from_pandas(merged_df)
        # groupby and map_groups
        group_data = droped_annoation_ds.groupby("image_id")
        group_anno_ds = group_data.map_groups(lambda g: self._group_by_image_id(g))
        logit.info("import coco flat annotation.final_annoation_ds count={}".format(group_anno_ds.count()))

        fill_image_ds = image_ds.map(lambda row: self._fill_image_info_coco(row=row,
                                                                            image_uri_prefix=image_uri_prefix)) \
            .drop_columns(cols=['id', 'file_name'])

        df = group_anno_ds.to_pandas()
        df['annotations'] = df['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        import pyarrow as pa
        annotation_ds = ray.data.from_arrow(pa.Table.from_pandas(df))

        logit.info("import coco flat image.final_image_ds count={}".format(fill_image_ds.count()))
        return {"image_ds": fill_image_ds, "annotation_ds": annotation_ds}
