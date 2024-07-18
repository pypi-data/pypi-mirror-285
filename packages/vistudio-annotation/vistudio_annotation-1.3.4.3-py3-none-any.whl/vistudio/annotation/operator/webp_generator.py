#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   webp_preprocessor.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""
import os
import pandas as pd
import re
import io
import bcelogger
from PIL import Image
from pandas import DataFrame
from windmillcomputev1.client.compute_client import ComputeClient
from windmillcomputev1.filesystem import blobstore


as_name_pattern = r"workspaces/(?P<workspace_id>[^/]+)/projects/(?P<project_name>[^/]+)/" \
                  r"annotationsets/(?P<annotation_set_name>[^/]+)$"
Boundary_Size = 2 * 1024 * 1024


class WebpGenerator(object):
    """
    WebpGenerator
    """

    def __init__(self, windmill_endpoint):
        self.windmill_endpoint = windmill_endpoint

        self.bs_dict = {}
        self.compute_client_dict = {}

    def generate_webp(self, source: DataFrame) -> DataFrame:
        """
        generate webp
        """
        results = []
        for source_index, source_row in source.iterrows():
            bcelogger.info(f"---generate webp: {source_row}---")

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

                # check size
                size = len(image_bytes)
                if size < Boundary_Size:
                    results.append({
                        "image_id": source_row['image_id'],
                        "annotation_set_id": source_row['annotation_set_id'],
                        "webp_state": "NotNeed",
                    })
                    bcelogger.info("generate webp not need")
                    continue

                # write webp to s3
                file_dir, file_name = os.path.split(file_uri)
                ext = os.path.splitext(file_uri)[1]
                webp_dir = file_dir + "-webp"
                webp_filename = file_name.replace(ext, '.webp')
                webp_uri = os.path.join(webp_dir, webp_filename)

                image = Image.open(io.BytesIO(image_bytes))
                webp_io = io.BytesIO()
                image.save(webp_io, format='WebP')
                webp_io.seek(0)
                bs.write_raw(path=webp_uri, content_type='image/webp', data=webp_io.getvalue())

                results.append({
                    "image_id": source_row['image_id'],
                    "annotation_set_id": source_row['annotation_set_id'],
                    "webp_state": "Completed",
                })
                bcelogger.info("generate webp success")
            except Exception as e:
                results.append({
                    "image_id": source_row['image_id'],
                    "annotation_set_id": source_row['annotation_set_id'],
                    "webp_state": "Error",
                })
                bcelogger.info("generate webp error: {}".format(e))

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


def get_project_name(annotation_set_name):
    """
    get project name
    :return:
    """
    match = re.match(as_name_pattern, annotation_set_name)
    as_name = match.groupdict()
    workspace_id = as_name['workspace_id']
    project_name = as_name['project_name']
    pj_name = f"workspaces/{workspace_id}/projects/{project_name}"
    return pj_name, workspace_id




