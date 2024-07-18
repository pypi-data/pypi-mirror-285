#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Authors: chujianfei
Date:    2024/02/22-11:56 AM
"""

def change_file_ext(file_name: str, file_ext: str):
    """
    change file suffix
    """
    import os
    splitext = os.path.splitext(file_name)
    if len(splitext) == 2:
        return os.path.splitext(file_name)[0] + file_ext
    return file_name