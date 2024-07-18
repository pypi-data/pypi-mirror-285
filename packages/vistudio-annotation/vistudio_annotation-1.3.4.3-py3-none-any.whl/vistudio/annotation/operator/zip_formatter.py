#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   label_formatter.py
"""
import os.path
from typing import Union, Dict

from windmillcomputev1.filesystem import blobstore, upload_by_filesystem

from vistudio.annotation.operator.reader import zip_extensions


class ZipFormatter(object):
    """
    LabelFormatter
    """

    def __init__(self,
                 filesystem: Union[Dict] = dict,
                 annotation_format: str = None
                 ):
        self.filesystem = filesystem
        self.bs = blobstore(filesystem)
        self.annotation_format = annotation_format

    def unzip_and_upload(self, file_uris: list()) -> str:
        """
        unzip_and_upload
        :param file_uris:
        :return:
        """
        data_uri = None
        for file_uri in file_uris:
            file_name = file_uri.split("/")[-1]
            if not (file_name.lower().endswith(zip_extensions)):
                return file_uris
            base_name, _ = os.path.splitext(file_name)
            directory_path = "/".join(file_uri.split("/")[:-1]).replace("s3://", "")
            directory_path = os.path.join(directory_path, base_name)

            import shutil
            dest_file = os.path.join(directory_path, file_name)
            if not os.path.exists(os.path.dirname(dest_file)):
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)

            self.bs.download_file(path=file_uri, file_name=dest_file)
            shutil.unpack_archive(dest_file, directory_path)
            os.remove(dest_file)

            file_path = os.path.join(directory_path, file_name).rsplit("/", 1)[0]
            dest_path = os.path.join(("/".join(file_uri.split("/")[:-1])), base_name)

            upload_by_filesystem(filesystem=self.filesystem, file_path=file_path, dest_path=dest_path)
            shutil.rmtree(file_path)
            data_uri = "s3://" + directory_path
            # shutil.rmtree(top_directory)

        return data_uri

