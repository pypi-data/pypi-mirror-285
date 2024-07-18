# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
image.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/4/9 3:51 下午
"""
import time
from datetime import datetime

from mongoengine import *

DATA_TYPE_IMAGE = 'Image'
ANNOTATION_STATE_ANNOTATED = 'Annotated'
ANNOTATION_STATE_UNANNOTATED = 'Unannotated'

class ImageState(EmbeddedDocument):
    """
    ImageState 图片状态
    """
    webp_state = StringField(required=False)
    thumbnail_state = StringField(required=False)


class ImageData(Document):
    """
    ImageData 图片数据
    """
    image_id = StringField(required=True)
    image_name = StringField(required=True)
    file_uri = StringField(required=True)
    width = IntField(required=True)
    height = IntField(required=True)
    image_state = EmbeddedDocumentField(ImageState, required=False)
    annotation_state = StringField(required=False)
    tags = DictField(required=False)
    task_id = StringField(required=False)
    data_type = StringField(required=True)

    annotation_set_id = StringField(required=True)
    annotation_set_name = StringField(required=True)
    user_id = StringField(required=True)
    org_id = StringField(required=False)

    created_at = IntField(default=time.time_ns())
    updated_at = IntField(default=time.time_ns())

    @classmethod
    def _get_collection_name(cls):
        return 'annotation'


if __name__ == '__main__':
    connect(host="mongodb://root:mongo123#@10.27.240.45:8719", db="annotation")
    image_data = ImageData(
        image_id='123',
        image_name='test.jpg',
        file_uri='/home/xujian/test.jpg',
        width=640,
        height=480,
        annotation_state="complete",
        tags={"mock": "mock"},
        task_id='123',
        data_type='Image',
        annotation_set_id='123',
        annotation_set_name='test',
        user_id='123'
    )
    ImageData.objects(image_id='123', annotation_set_id='123').delete()

    image_data.save()
    print(image_data.to_mongo())

    # ImageData.objects(image_id='123', annotation_set_id='123').delete()

    objs = ImageData.objects(annotation_set_id='annotation_set_1', image_name__regex='example_11', data_type='Image')
    update_tags = {
            'test': '123',
            'test_1': '456'
    }
    update_field = dict()
    for key, value in update_tags.items():
        update_field[f"tags.{key}"] = value
    update = {"$set": update_field}
    objs.update(__raw__=update)

