#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   thumbnail_generator.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""
import os
import pandas as pd
import io
import bcelogger
from PIL import Image
from pandas import DataFrame
from vistudio.annotation.operator.webp_generator import get_project_name
from windmillcomputev1.client.compute_client import ComputeClient
from windmillcomputev1.filesystem import blobstore


THUMBNAIL_WIDTH = 158
THUMBNAIL_HEIGHT = 118

as_name_pattern = r"workspaces/(?P<workspace_id>[^/]+)/projects/(?P<project_name>[^/]+)/" \
                  r"annotationsets/(?P<annotation_set_name>[^/]+)$"


class ThumbnailGenerator(object):
    """
    ThumbnailGenerator
    """

    def __init__(self, windmill_endpoint):
        self.windmill_endpoint = windmill_endpoint

        self.bs_dict = {}
        self.compute_client_dict = {}

    def generate_thumbnail(self, source: DataFrame) -> DataFrame:
        """
        generate thumbnail
        """
        results = []
        for source_index, source_row in source.iterrows():
            bcelogger.info(f"---start generate thumb: {source_row}---")

            try:
                # cache blobstore
                pj_name, ws_id = get_project_name(source_row['annotation_set_name'])
                org_id = source_row['org_id']
                user_id = source_row['user_id']
                self._get_bs(pj_name, ws_id, org_id, user_id)
                bs = self.bs_dict[pj_name]

                # read image
                file_uri = source_row['file_uri']
                image_bytes = bs.read_raw(path=file_uri)
                image_bytes_io = io.BytesIO(image_bytes)
                img = Image.open(image_bytes_io)
                width, height = img.size

                # resize image
                resized_img = img.resize((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))

                # write thumbnail_state to s3
                file_dir, file_name = os.path.split(file_uri)
                thumb_dir = file_dir + "-thumbnail"
                thumb_uri = os.path.join(thumb_dir, file_name)
                ext = os.path.splitext(file_uri)[1][1:].lower()
                if ext == 'jpg':
                    ext = 'jpeg'

                byte_arr = io.BytesIO()
                resized_img.save(byte_arr, format=ext)
                resize_img_bytes = byte_arr.getvalue()
                bs.write_raw(path=thumb_uri, content_type=f'image/{ext}', data=resize_img_bytes)

                results.append({
                    "image_id": source_row['image_id'],
                    "annotation_set_id": source_row['annotation_set_id'],
                    "width": width,
                    "height": height,
                })
                bcelogger.info("generate thumbnail success")
            except Exception as e:
                results.append({
                    "image_id": source_row['image_id'],
                    "annotation_set_id": source_row['annotation_set_id'],
                    "width": -1,
                    "height": -1,
                })
                bcelogger.info("generate thumbnail error: {}".format(e))

        return pd.DataFrame(results)

    def _get_bs(self, pj_name, ws_id, org_id, user_id):
        """
        get blob store
        :return:
        """
        if pj_name in self.bs_dict:
            return

        if org_id in self.compute_client_dict:
            compute_client = self.compute_client_dict[org_id]
        else:
            compute_client = ComputeClient(endpoint=self.windmill_endpoint,
                                           context={"OrgID": org_id, "UserID": user_id})
            self.compute_client_dict[org_id] = compute_client

        try:
            fs = compute_client.suggest_first_filesystem(workspace_id=ws_id, guest_name=pj_name)
            self.bs_dict[pj_name] = blobstore(filesystem=fs)
        except Exception as e:
            bcelogger.info(f"suggest filesystem error: {e}")


