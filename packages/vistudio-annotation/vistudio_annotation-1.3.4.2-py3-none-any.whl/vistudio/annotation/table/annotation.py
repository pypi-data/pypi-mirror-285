# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
annotation.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/4/9 4:11 下午
"""
import time

from mongoengine import *

DATA_TYPE_ANNOTATION = "Annotation"
TASK_KIND_MANUAL = "Manual"
TASK_KIND_MODEL = "Model"

class Label(EmbeddedDocument):
    """
    Label 标签
    """
    id = StringField(required=True)
    confidence = FloatField(required=False)


class RLE(EmbeddedDocument):
    """
    RLE
    """
    size = ListField(required=True)
    counts = ListField(required=True)


class OCR(EmbeddedDocument):
    """
    OCR
    """
    word = StringField(required=True)
    direction = StringField(required=False)


class Annotation(EmbeddedDocument):
    """
    Annotation 标注
    """
    id = StringField(required=True)
    labels = ListField(EmbeddedDocumentField(Label), required=True)

    area = FloatField(required=False)
    bbox = ListField(required=False, default=None)
    segmentation = ListField(required=False, default=None)
    rle = EmbeddedDocumentField(RLE, required=False)
    ocr = EmbeddedDocumentField(OCR, required=False)


class AnnotationData(Document):
    """
    AnnotationData 标注数据
    """
    image_id = StringField(required=True)
    image_created_at = IntField(default=0)
    artifact_name = StringField(required=True)
    annotations = ListField(EmbeddedDocumentField(Annotation), required=False)
    task_kind = StringField(required=True)
    task_id = StringField(required=False)
    data_type = StringField(required=True)

    user_id = StringField(required=True)
    annotation_set_id = StringField(required=True)

    created_at = IntField(default=time.time_ns())
    updated_at = IntField(default=time.time_ns())

    @classmethod
    def _get_collection_name(cls):
        return 'annotation'


