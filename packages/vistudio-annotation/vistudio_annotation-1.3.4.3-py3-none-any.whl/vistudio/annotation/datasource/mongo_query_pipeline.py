# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
export_pipeline.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/3/5 7:18 下午
"""
import json

import pandas as pd
import pyarrow as pa
import pymongo

LOOKUP = "$lookup:"


def replace_nested_set_strings(value, m):
    """
    replace_nested_set_strings
    :param value:
    :param m:
    :return:
    """
    if isinstance(value, str) and value.startswith(LOOKUP):
        key = value[len(LOOKUP):]
        return m.get(key, value)
    elif isinstance(value, list):
        return [replace_nested_set_strings(item, m) for item in value]
    elif isinstance(value, dict):
        return {k: replace_nested_set_strings(v, m) for k, v in value.items()}
    return value


class Step:
    """
    Step
    """

    def __init__(self, aggregation, collection, default_query_result, query_result_mapping):
        self.aggregation = aggregation
        self.collection = collection
        self.default_query_result = default_query_result
        self.query_result_mapping = query_result_mapping
        # self.aggregation_json = json.dumps(aggregation)

    def append_shard_match(self, shard_match):
        """
        append_shard_match
        :param shard_match:
        :return:
        """
        new_aggregation = shard_match.copy()
        new_aggregation.extend(self.aggregation)
        self.aggregation = new_aggregation

    def aggregation_doc(self):
        """
        aggregation_doc
        :return:
        """
        return self.aggregation

    def collection_name(self):
        """
        collection_name
        :return:
        """
        return self.collection

    def run(self, coll):
        """
        run
        :param coll:
        :return:
        """
        cursor = coll.aggregate(self.aggregation_doc(), allowDiskUse=True)
        result = dict()
        for doc in cursor:
            # 查询结果映射
            for k, v in self.query_result_mapping.items():
                if v not in result:
                    result[v] = []

                if k == "":
                    result[v].append(doc)
                    continue

                if k in doc:
                    result[v].append(doc[k])
        return result


class Pipeline:
    """
    Pipeline
    """

    def __init__(self, steps):
        self.steps = [step for step in steps if step is not None]
        self.results = {}
        self.index = 0

    def append_shard_match(self, shard_match):
        """
        append_shard_match
        :param shard_match:
        :return:
        """
        for step in self.steps:
            step.append_shard_match(shard_match)

    def next_step(self):
        """
        next_step
        :return:
        """
        if self.index >= len(self.steps):
            return None
        query = self.steps[self.index]
        self.index += 1
        transformed_doc = replace_nested_set_strings(query.aggregation, self.results)
        query.aggregation = transformed_doc
        # query.aggregation_json = json.dumps(transformed_doc)
        # print("next_step aggregation: {}".format(query.aggregation))
        return query

    def set_query_result(self, result):
        """
        set_query_result
        :param result:
        :return:
        """
        default_query_result = self.steps[self.index - 1].default_query_result
        if default_query_result is None:
            default_query_result = {}
        if result is not None:
            default_query_result.update(result)
        self.results.update(default_query_result)

    def run(self, coll):
        """
        run
        :param coll:
        :return:
        """
        for i in range(len(self.steps)):
            step = self.next_step()
            step_result = step.run(coll)
            self.set_query_result(step_result)
        return self.results


def json_to_pipeline(steps_json):
    """
    json_to_pipeline
    :param steps_json:
    :return:
    """
    pipe_steps = []
    for s in steps_json:
        aggregation = s.get("aggregation", [])
        collection = s.get("collection", "")
        default_query_result = s.get("default_query_result", None)
        query_result_mapping = s.get("query_result_mapping", {})
        pipe_steps.append(Step(aggregation, collection, default_query_result, query_result_mapping))
    return Pipeline(pipe_steps)


def get_pipeline_func(query_json):
    """
    get_pipeline_func
    :param query_json:
    :return:
    """
    pipe = json_to_pipeline(query_json)

    def list_image_annotation(coll, shard_match=None, schema=None, **kwargs):
        """
        list_image_annotation
        :param coll:
        :param shard_match:
        :param schema:
        :param kwargs:
        :return:
        """
        print(f"pipeline steps num: {len(pipe.steps)}")
        pipe.append_shard_match(shard_match)
        print(f"pipeline steps num: {len(pipe.steps)}")
        results = pipe.run(coll)
        if 'images' not in results:
            df = pd.DataFrame()

            table = pa.Table.from_pandas(df)
            return table
        images = results['images']
        annotations = results.get('annotations', [])
        image_list = []
        image_id2index = {}
        for image in images:
            image_id = image['image_id']
            image_id2index[image_id] = len(image_list)
            image['annotations'] = []
            # image.pop('tags')
            image.pop('_id')
            image['height'] = int(image['height'])
            image['width'] = int(image['width'])
            image_list.append(image)
        for annotation in annotations:
            print("annotation:{} type:{}".format(annotation, type(annotation)))
            annotation.pop('_id')
            if "task_id" in annotation:
                annotation.pop('task_id')
            if 'label_count' in annotation:
                annotation.pop('label_count')
            annotations_inner = annotation.get("annotations", [])
            annotation.pop("annotations")
            n_annotations_inner = []
            for annotation_inner in annotations_inner:
                area = annotation_inner.get("area", 0)
                annotation_inner['area'] = int(area)
                bbox = annotation_inner.get("bbox", [])
                n_bbox = [int(element) for element in bbox]
                annotation_inner['bbox'] = n_bbox
                segmentation = annotation_inner.get("segmentation", [])
                n_seg = [int(element) for element in segmentation]
                annotation_inner['segmentation'] = n_seg
                n_annotations_inner.append(annotation_inner)
            annotation['annotations'] = n_annotations_inner

            image_id = annotation['image_id']
            image_list[image_id2index[image_id]]['annotations'].append(annotation)

        df = pd.DataFrame(image_list)

        table = pa.Table.from_pandas(df)
        print("list_image_annotation result count: ", table.num_rows)
        return table

    return list_image_annotation


def test_json_to_pipeline():
    """
    test_json_to_pipeline
    :return:
    """
    json_str = """
        """
    json_str_without_space = json_str.replace(" ", "").replace("\n", "").replace('"', '\"')
    print(json_str_without_space)
    pipe_json = json.loads(json_str)
    pipeline = json_to_pipeline(pipe_json)
    print("test_json_to_pipeline: {}".format(pipeline))

    uri = "mongodb://root:mongo123#@10.27.240.45:8719"
    db_name = "annotation_dev_tiny"
    collection_name = "annotation"
    client = pymongo.MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    res = pipeline.run(collection)
    print("res", res)


if __name__ == '__main__':
    test_json_to_pipeline()
