# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
pipeline.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/3/5 7:18 下午
"""

import json

import logit

SetResultPrefix = "$lookup:"


def replace_nested_set_strings(value, m):
    """
    替换嵌套的字符串
    :param value:
    :param m:
    :return:
    """
    if isinstance(value, str) and value.startswith(SetResultPrefix):
        key = value[len(SetResultPrefix):]
        return m.get(key, value)
    elif isinstance(value, list):
        return [replace_nested_set_strings(item, m) for item in value]
    elif isinstance(value, dict):
        return {k: replace_nested_set_strings(v, m) for k, v in value.items()}
    return value


class Step:
    """
    查询步骤
    """
    def __init__(self, aggregation, collection, default_query_result, query_result_mapping):
        self.aggregation = aggregation
        self.collection = collection
        self.default_query_result = default_query_result
        self.query_result_mapping = query_result_mapping
        # self.aggregation_json = json.dumps(aggregation)

    def aggregation_doc(self):
        """
        聚合查询文档
        :return:
        """
        return self.aggregation

    def collection_name(self):
        """
        查询集合名称
        :return:
        """
        return self.collection

    def run(self, coll):
        """
        执行查询
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
    Pipeline 查询管道
    """
    def __init__(self, steps):
        self.steps = [step for step in steps if step is not None]
        self.results = {}
        self.index = 0

    def next_step(self):
        """
        获取下一个查询步骤
        :return:
        """
        if self.index >= len(self.steps):
            return None
        query = self.steps[self.index]
        self.index += 1
        transformed_doc = replace_nested_set_strings(query.aggregation, self.results)
        query.aggregation = transformed_doc
        # query.aggregation_json = json.dumps(transformed_doc)
        logit.info("next_step aggregation: {}".format(query.aggregation))
        return query

    def set_query_result(self, result):
        """
        设置查询结果
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
        执行查询
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
    将JSON转换为Pipeline
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


def query_mongo(query_pipeline_json, collection):
    """
    查询Mongo
    :param query_pipeline_json:
    :param collection:
    :return:
    """

    pipeline = json_to_pipeline(query_pipeline_json)
    results = pipeline.run(collection)
    return results


def test_json_to_pipeline():
    """
    测试JSON转换为Pipeline
    :return:
    """
    json_str = """[
        {
            "aggregation": [{"$match":{"name":"example_2.jpg"}}, {"$group":{"id": "", "image_ids": {"$addToSet": "$image_id"}}}],
            "collection": "test"
        }]"""
    json_str_without_space = json_str.replace(" ", "").replace("\n", "").replace('"', '\"')
    logit.info(json_str_without_space)
    pipeline = json_to_pipeline(json.loads(json_str_without_space))
    logit.info("test_json_to_pipeline: {}".format(pipeline))


if __name__ == '__main__':
    test_json_to_pipeline()
