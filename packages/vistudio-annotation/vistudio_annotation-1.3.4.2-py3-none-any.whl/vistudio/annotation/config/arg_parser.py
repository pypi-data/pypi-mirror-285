#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Authors: chujianfei
Date:    2024/02/22-11:56 AM
"""
import argparse

class ArgParser:
    """
     arg parser
    """

    def __init__(self, kind: str):
        self._parser = argparse.ArgumentParser()
        self._add_common_args()

        if kind == 'Import':
            self._add_import_args()
        elif kind == 'Export':
            self._add_export_args()
        elif kind == 'Statistic':
            self._add_statistic_args()
        elif kind == 'BatchUpdate':
            self._add_batch_update_args()
        elif kind == 'BatchDelete':
            self._add_batch_delete_args()

    def _add_common_args(self):
        self._parser.add_argument(
            "--mongo-host",
            dest="mongo_host",
            required=True,
            default="10.27.240.45",
            help="mongo host",
        )

        self._parser.add_argument(
            "--mongo-port",
            dest="mongo_port",
            required=True,
            default="8718",
            help="mongo port",
        )

        self._parser.add_argument(
            "--mongo-user",
            dest="mongo_user",
            required=True,
            default="root",
            help="mongo user",
        )

        self._parser.add_argument(
            "--mongo-password",
            dest="mongo_password",
            required=True,
            default="",
            help="mongo password",
        )

        self._parser.add_argument(
            "--mongo-db",
            dest="mongo_database",
            required=True,
            default="",
            help="mongo database",
        )

        self._parser.add_argument(
            "--mongo-collection",
            dest="mongo_collection",
            required=True,
            default="",
            help="mongo collection",
        )

        self._parser.add_argument(
            "--windmill-endpoint",
            dest="windmill_endpoint",
            required=True,
            default="",
            help="windmill endpoint",
        )

        self._parser.add_argument(
            "--windmill-ak",
            dest="windmill_ak",
            required=True,
            default="",
            help="windmill ak",
        )

        self._parser.add_argument(
            "--windmill-sk",
            dest="windmill_sk",
            required=True,
            default="",
            help="windmill sk",
        )

        self._parser.add_argument(
            "--filesystem-name",
            dest="filesystem_name",
            required=True,
            default="",
            help="filesystem name",
        )

        self._parser.add_argument(
            "--job-name",
            dest="job_name",
            required=True,
            default="",
            help="windmill job name",
        )

        self._parser.add_argument(
            "--vistudio-endpoint",
            dest="vistudio_endpoint",
            required=True,
            default="http://10.27.240.49:8322",
            help="vistudio annotation endpoint",
        )

        self._parser.add_argument(
            "--annotation-set-name",
            dest="annotation_set_name",
            required=True,
            default="",
            help="Annotation set id, example: as01",
        )
        self._parser.add_argument(
            "--annotation-format",
            dest="annotation_format",
            required=False,
            default="",
            help="Annotation format. Example: Coco",
        )

    def _add_export_args(self):
        self._parser.add_argument(
            "--q",
            dest="q",
            required=True,
            default="",
            help="Mongo query sql",
        )

        self._parser.add_argument(
            "--export-to",
            dest="export_to",
            required=True,
            default="dataset",
            help="dataset or filesystem",
        )
        self._parser.add_argument(
            "--dataset",
            dest="dataset",
            required=False,
            default="",
            help="create dataset request",
        )

        self._parser.add_argument(
            "--merge-labels",
            dest="merge_labels",
            required=False,
            default="",
            help="need merge label,key is dest label, value is need merge labels",
        )

        self._parser.add_argument(
            "--split",
            dest="split",
            required=False,
            default="",
            help="split image",
        )

    def _add_import_args(self):
        self._parser.add_argument(
            "--data-uri",
            dest="data_uri",
            required=True,
            default="",
            help="Only Image、Only Annotation、Image + Annotation",
        )

        self._parser.add_argument(
            "--data-types",
            dest="data_types",
            required=True,
            default="",
            help="Data type. Example: image,annotation",
        )

        self._parser.add_argument(
            "--file-format",
            dest="file_format",
            required=False,
            default="",
            help="File format. Example: zip,file,folder",
        )

        self._parser.add_argument(
            "--tag",
            dest="tag",
            required=False,
            default="",
            help="tag",
        )

    def _add_statistic_args(self):
        self._parser.add_argument(
            "--q",
            dest="q",
            required=True,
            default="",
            help="Mongo query sql",
        )

    def _add_batch_update_args(self):
        self._parser.add_argument(
            "--q",
            dest="q",
            required=True,
            default='',
            help="Mongo query sql",
        )
        self._parser.add_argument(
            "--object-type",
            dest="object_type",
            required=True,
            default=[],
            help="Exclude image ids",
        )
        self._parser.add_argument(
            "--updates",
            dest="updates",
            required=True,
            default='',
            help="Updates content",
        )

    def _add_batch_delete_args(self):
        self._parser.add_argument(
            "--q",
            dest="q",
            required=True,
            default='',
            help="Mongo query sql",
        )

    def parse_args(self):
        """
        parse args
        :return:
        """
        args = self._parser.parse_args()
        self._args = vars(args)
        return self._args

    def get_args(self):
        """
        get args
        :return:
        """
        return self._args

