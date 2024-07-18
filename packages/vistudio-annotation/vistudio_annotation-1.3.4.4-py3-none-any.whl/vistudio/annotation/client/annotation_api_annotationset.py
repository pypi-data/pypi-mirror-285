# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
annotation_api_annotationset.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/4/9 7:44 下午
"""


import re

from typing import Optional
from pydantic import BaseModel

annotation_set_name_regex = re.compile(
    "^workspaces/(?P<workspace_id>.+?)/projects/(?P<project_name>.+?)/annotationsets/(?P<local_name>.+?)$"
)


class AnnotationSetName(BaseModel):
    """
    The name of annotation set.
    """

    workspace_id: str
    project_name: str
    local_name: str

    def get_name(self):
        """
        get name
        :return:
        """
        return f"workspaces/{self.workspace_id}/projects/{self.project_name}/annotationsets/{self.local_name}"


def parse_annotation_set_name(name: str) -> Optional[AnnotationSetName]:
    """
    Get workspace id, project name and job local name from job name.
    """
    m = annotation_set_name_regex.match(name)
    if m is None:
        return None
    return AnnotationSetName(
        workspace_id=m.group("workspace_id"),
        project_name=m.group("project_name"),
        local_name=m.group("local_name"),
    )

