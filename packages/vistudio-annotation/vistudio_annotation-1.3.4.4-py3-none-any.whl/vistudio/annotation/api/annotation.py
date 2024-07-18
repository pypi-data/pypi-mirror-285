# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
Vistudio Spec
"""
import re
from typing import List, Tuple, Optional
import pyarrow as pa
from pydantic import BaseModel


class Label(BaseModel):
    """Label"""
    id: int
    name: str
    confidence: float

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Label to pyarrow data type"""
        return pa.struct([
            ("id", pa.int32()),
            ("name", pa.string()),
            ("confidence", pa.float32())
        ])


class OCR(BaseModel):
    """OCR"""
    word: str
    direction: str

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """OCR to pyarrow data type"""
        return pa.struct([
            ("word", pa.string()),
            ("direction", pa.string())
        ])


class RLE(BaseModel):
    """RLE"""
    counts: List[float]
    size: Tuple[float, float]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """RLE to pyarrow data type"""
        return pa.struct([
            ("count", pa.list_(pa.float32())),
            ("size", pa.list_(pa.float32()))
        ])


class Annotation(BaseModel):
    """Annotation"""
    id: int
    bbox: List[float]
    segmentation: List[float]
    rle: RLE
    keypoints: List[float]
    ocr: OCR
    area: float
    labels: List[Label]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Annotation to pyarrow data type"""
        return pa.struct([
            ("id", pa.int32()),
            ("bbox", pa.list_(pa.float32())),
            ("segmentation", pa.list_(pa.float32())),
            ("rle", RLE.to_pyarrow_schema()),
            ("keypoints", pa.list_(pa.float32())),
            ("ocr", OCR.to_pyarrow_schema()),
            ("area", pa.float32()),
            ("labels", pa.list_(Label.to_pyarrow_schema()))
        ])


class Annotations(BaseModel):
    """Annotations"""
    image_id: str
    artifact_name: str
    annotations: List[Annotation]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Annotations to pyarrow data type"""
        return pa.struct([
            ("artifact_name", pa.string()),
            ("annotations", pa.list_(Annotation.get_data_type()))
            ("image_id", pa.string()),
        ])


class Image(BaseModel):
    """Image"""
    image_id: str
    image_name: str
    file_uri: str
    width: int
    height: int
    annotations: List[Annotations]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Image to pyarrow data type"""
        return pa.struct([
            ("image_id", pa.string()),
            ("image_name", pa.string()),
            ("file_uri", pa.string()),
            ("width", pa.int32()),
            ("height", pa.int32()),
            ("annotations", pa.list_(Annotations.to_pyarrow_schema()))
        ])


class Vistudio(BaseModel):
    """Vistudio"""
    images: List[Image]
    labels: List[Label]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.Schema:
        """Vistudio to pyarrow schema"""
        return pa.schema([
            pa.field("images", Image.to_pyarrow_schema()),
            pa.field("labels", Label.to_pyarrow_schema()),
        ])


annotation_set_name_regex = re.compile(
    "workspaces/(?P<workspace_id>[^/]+)/projects/(?P<project_name>[^/]+)/annotationsets/" \
    r"(?P<annotationset_local_name>[^/]+)$"
)


class AnnnotationSetName(BaseModel):
    """
    AnnnotationSetName
    """
    workspace_id: str
    project_name: str
    local_name: str


def parse_annotation_set_name(name: str) -> Optional[AnnnotationSetName]:
    """
    Get workspace id, project name and job local name from annotation set name
    """
    m = annotation_set_name_regex.match(name)
    if m is None:
        return None
    return AnnnotationSetName(
        workspace_id=m.group("workspace_id"),
        project_name=m.group("project_name"),
        local_name=m.group("annotationset_local_name"),
    )


if __name__ == "__main__":
    print(Vistudio.to_pyarrow_schema())
