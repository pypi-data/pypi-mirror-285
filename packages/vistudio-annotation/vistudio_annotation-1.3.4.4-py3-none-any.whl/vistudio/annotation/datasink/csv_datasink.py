#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Authors: chujianfei
Date:    2024/02/22-11:56 AM
"""

from typing import Dict, Any
from pyarrow import csv


def exclude_csv_header_func() -> Dict[str, Any]:
    """
    exclude_csv_header_func
    :return:
    """
    return {
        "write_options": csv.WriteOptions(
            include_header=False,
        )
    }
