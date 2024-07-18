# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
image_datasource.py
Authors: chujianfei
Date:    2024/3/5 7:18 下午
"""

from typing import TYPE_CHECKING, Iterator, List

from ray.data._internal.delegating_block_builder import DelegatingBlockBuilder
from ray.data.block import Block
from ray.data.datasource.file_based_datasource import FileBasedDatasource
from ray.util.annotations import PublicAPI

if TYPE_CHECKING:
    import pyarrow


@PublicAPI
class XMLDatasource(FileBasedDatasource):
    """Text datasource, for reading and writing text files."""

    def __init__(
            self,
            paths: List[str],
            *,
            encoding: str = "utf-8",
            **file_based_datasource_kwargs
    ):
        super().__init__(paths, **file_based_datasource_kwargs)

        self.encoding = encoding

    def _parse_labels(self, root):
        labels = []
        for label in root.findall('.//labels/label'):
            label_name = label.find('name').text
            label_color = label.find('color').text if label.find('color') is not None else ''
            label = {"name": label_name, "color": label_color}
            labels.append(label)
        return labels

    def _parse_image_info(self, image_element):
        image_info = {}
        # 解析image标签的属性
        for key, value in image_element.attrib.items():
            image_info[key] = value

        # 解析image标签下的子标签信息
        for child in image_element:
            if child.tag in ['box', 'polygon', 'points', 'tag', 'skeleton', 'mask', 'polyline']:
                # 解析每个子标签的信息并添加到image_info中

                def parse_annotation(annotation_element):
                    return annotation_element.attrib

                annotation_info = parse_annotation(child)
                if 'annotations' not in image_info:
                    image_info['annotations'] = []
                image_info['annotations'].append({child.tag: annotation_info})

        return image_info

    def _parse_annotation(self, root):
        images = []
        for image_element in root.findall('image'):
            image_info = self._parse_image_info(image_element)
            images.append(image_info)

        return images

    def _read_stream(self, f: "pyarrow.NativeFile", path: str) -> Iterator[Block]:
        data = f.readall()

        xml_data = data.decode('utf-8')
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_data)
        labels = self._parse_labels(root=root)
        images = self._parse_annotation(root=root)

        builder = DelegatingBlockBuilder()

        item = {'labels': labels, 'images': images}
        builder.add(item)
        block = builder.build()

        yield block
