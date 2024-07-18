#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   reader.py
"""

from typing import List, Union, Dict

import ray
from ray.data import Dataset
from windmillcomputev1.filesystem import blobstore, init_py_filesystem
import os
from vistudio.annotation.config.config import Config
from vistudio.annotation.datasource.xml_datasource import XMLDatasource

image_extensions = ('.jpeg', '.jpg', '.png', '.bmp')
zip_extensions = ('.zip', '.tar.gz', '.tar', '.tgz')
cityscape_annotation_file_extensions = ('.jpeg', '.jpg', '.png', '.bmp', '.txt')
annotation_extensions = ('.json', '.jsonl', '.xml')
exclude_pkg = ("-thumbnail", "-webp", "_MACOSX")


class Reader(object):
    """
    Reader
    """

    def __init__(self,
                 filesystem: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 ):
        self._filesystem = filesystem
        self.annotation_set_id = annotation_set_id
        self.s3_bucket = filesystem.get('endpoint').split("/")[0]

        self.bs = blobstore(filesystem)
        self.fs = init_py_filesystem(filesystem)

    def _get_filenames(self, file_uri, layer):
        """
        :param file_uri: s3地址
        :param layer: 遍历的层数
        :return: 文件filename列表
        """

        filenames = []
        dest_path = file_uri.split(self.s3_bucket + '/')[1]
        if not dest_path.endswith("/"):
            dest_path += "/"
        dest_parts = dest_path.split('/')[:-1]

        file_list = self.bs.list_meta(dest_path)
        for file in file_list:
            f_path = file.url_path.split(self.s3_bucket + '/')[1]
            f_parts = f_path.split('/')[:-1]
            # 此处表示取文件夹3层内的数据
            if len(f_parts) - len(dest_parts) > layer:
                continue
            filename = "s3://" + os.path.join(self.s3_bucket, f_path)
            filenames.append(filename)

        return filenames

    def get_annoation_fileuris(self, data_uri) -> list():
        """
        get annoation file uris by data_uri
        :param data_uri:
        :return: list
        """
        annotation_file_uri = data_uri
        # 获取全部要处理的标注文件
        ext = os.path.splitext(annotation_file_uri)[1].lower()
        if ext == "":
            filenames = self._get_filenames(annotation_file_uri, 3)
        else:
            filenames = [annotation_file_uri]

        file_uris = list()
        for filename in filenames:
            if not filename.lower().endswith(annotation_extensions) or "._" in filename:
                continue
            file_uris.append(filename)
        print("file_uris========", file_uris)
        return file_uris

    def get_imagenet_annoation_fileuris(self, data_uri) -> list():
        """
        get annoation file uris by data_uri
        :param data_uri:
        :return: list
        """
        file_uris = list()
        image_uris = self._get_filenames(data_uri, 2)
        for image_uri in image_uris:
            if not image_uri.endswith(image_extensions) or "._" in image_uri:
                continue
            # 获取相对路径
            relative_path = os.path.relpath(image_uri, data_uri)

            # 获取下一级目录
            label_name = relative_path.split(os.sep)[0]
            if label_name.endswith(exclude_pkg):
                continue
            print("image_uri===={}".format(image_uri))
            file_uri_dict = {"label": label_name, "image": image_uri}
            file_uris.append(file_uri_dict)

        return file_uris

    def get_image_fileuris(self, data_uri) -> list():
        """
        get image file uris by data_uri
        :param data_uri:
        :return:
        """
        image_uri = data_uri

        ext = os.path.splitext(image_uri)[1].lower()
        if ext == "":
            filenames = self._get_filenames(image_uri, 3)
        else:
            filenames = [image_uri]

        # 插入图像
        file_uris = list()
        for filename in filenames:
            if not filename.lower().endswith(image_extensions) or "._" in filename:
                continue

            _, file_name = os.path.split(filename)
            file_uris.append(filename)

        return file_uris

    def get_cityscapes_annotation_fileuris(self, data_uri) -> list():
        """
        get image file uris by data_uri
        :param data_uri:
        :return:
        """
        image_uri = data_uri

        ext = os.path.splitext(image_uri)[1].lower()
        if ext == "":
            filenames = self._get_filenames(image_uri, 3)
        else:
            filenames = [image_uri]

        # 插入图像
        file_uris = list()
        for filename in filenames:
            if "-thumbnail" in filename or "-webp" in filename or "._" in filename:
                continue
            if not filename.lower().endswith(cityscape_annotation_file_extensions):
                continue

            _, file_name = os.path.split(filename)
            file_uris.append(filename)

        return file_uris

    def get_file_uris(self, data_uri: str, data_types: list(), import_type: str = None) -> list():
        """
        get_file_uris
        :param data_uri:
        :param data_types:
        :param import_type:
        :return:
        """
        annotation_pkg_suffix = 'annotations'
        if import_type == 'vistudio':
            annotation_pkg_suffix = 'jsonls'
        elif import_type == 'imagenet':
            annotation_pkg_suffix = ''
        elif import_type == 'cityscapes':
            annotation_pkg_suffix = ''
        elif import_type == 'cvat':
            annotation_pkg_suffix = ''

        if len(data_types) == 1 and data_types[0] == "annotation":
            if import_type == 'cityscapes':
                file_uris = self.get_cityscapes_annotation_fileuris(data_uri)
            else:
                file_uris = self.get_annoation_fileuris(data_uri)

        elif len(data_types) == 1 and data_types[0] == "image":
            file_uris = self.get_image_fileuris(data_uri)

        elif len(data_types) == 2 and "image" in data_types and "annotation" in data_types:
            anno_uri = os.path.join(data_uri, annotation_pkg_suffix)
            # 获取所有的图片 和文件 uri
            if import_type == 'imagenet':
                file_uris = self.get_imagenet_annoation_fileuris(data_uri=anno_uri)
            elif import_type == 'cityscapes':
                file_uris = self.get_cityscapes_annotation_fileuris(data_uri=anno_uri)
            else:
                file_uris = self.get_annoation_fileuris(data_uri=anno_uri)

        return file_uris

    def get_zip_file_uris(self, data_uri: str) -> list():
        """
        get_zip_file_uris
        :param data_uri:
        :return:
        """
        zip_uri = data_uri

        ext = os.path.splitext(zip_uri)[1].lower()
        if ext == "":
            filenames = self._get_filenames(zip_uri, 0)
        else:
            filenames = [zip_uri]

        # 插入图像
        file_uris = list()
        for filename in filenames:
            if not filename.lower().endswith(zip_extensions):
                continue

            _, file_name = os.path.split(filename)
            file_uris.append(filename)

        return file_uris

    def read_json(self, file_uris: List[str]) -> Dataset:
        """
        read json
        :param file_uris:
        :return: Dataset
        """
        import pyarrow.json as pajson
        block_size = 100 << 20
        ds = ray.data.read_json(paths=file_uris, filesystem=self.fs,
                                read_options=pajson.ReadOptions(block_size=block_size),
                                parse_options=pajson.ParseOptions(newlines_in_values=True))
        return ds

    def read_xml(self, file_uris: List[str]) -> Dataset:
        """
        read xml
        :param file_uris:
        :return: Dataset
        """
        xml_datasource = XMLDatasource(paths=file_uris, filesystem=self.fs)
        ds = ray.data.read_datasource(datasource=xml_datasource)
        return ds

