#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   vistudio_cutter.py
@Time    :   2024/5/11 16:48
@Author  :   dongling
"""
import os
import numpy as np
import pandas as pd
import bcelogger
import io
import math
import hashlib
from PIL import Image
from pandas import DataFrame
from shapely.geometry import Polygon, MultiPolygon

from windmillcomputev1.filesystem import blobstore

from vistudio.annotation.util import string
from vistudio.annotation.util import annotation


class VistudioCutter(object):
    """
    to cut vistudio
    """

    def __init__(self, filesystem, location, split):
        self.filesystem = filesystem
        self.location = location
        self.split = split

        self.cut_width = split['width']
        self.cut_height = split['height']
        self.overlapW = split['overlap']
        self.overlapH = split['overlap']
        self.padding = split['padding']

    def cut_images_and_annotations(self, source: DataFrame) -> DataFrame:
        """
        cut images and annotations
        """
        df_images = self._cut_images(source)
        df_annotations = self._cut_annotations(source)
        df = pd.concat([df_images, df_annotations], axis=1)
        return df

    def _cut_images(self, source: DataFrame):
        """
        cut images
        """
        bs = blobstore(filesystem=self.filesystem)
        results = []

        for source_index, source_row in source.iterrows():

            # 读图像
            file_uri = source_row['file_uri']
            image_bytes = bs.read_raw(path=file_uri)
            image = Image.open(io.BytesIO(image_bytes))

            # 获取划窗的所有左上角坐标
            imgH = source_row['height']
            imgW = source_row['width']
            offsets = self._get_offset(imgH, imgW)

            for (offset_h, offset_w) in offsets:
                crop_x1, crop_x2 = offset_w, min(offset_w + self.cut_width, imgW)
                crop_y1, crop_y2 = offset_h, min(offset_h + self.cut_height, imgH)
                box = (crop_x1, crop_y1, crop_x2, crop_y2)

                # ------切图像块-------
                crop_img = image.crop(box)

                # 不足的填充0像素值
                if self.padding and crop_img.size != (self.cut_width, self.cut_height):
                    new_crop_img = Image.new("RGB", (self.cut_width, self.cut_height), color=(0, 0, 0))
                    new_crop_img.paste(crop_img, (0, 0))
                    crop_img = new_crop_img

                # 图像块上传到s3
                _, file_name = os.path.split(file_uri)
                name = file_name.rsplit(".", 1)
                crop_img_name = "%s_%d_%d.%s" % (name[0], offset_h, offset_w, name[1])
                crop_img_dir = os.path.join(self.location, "images")
                crop_img_uri = os.path.join(crop_img_dir, crop_img_name)

                ext = name[1]
                if ext == 'jpg':
                    ext = 'jpeg'

                byte_arr = io.BytesIO()
                crop_img.save(byte_arr, format=ext)
                crop_img_bytes = byte_arr.getvalue()
                bs.write_raw(path=crop_img_uri, content_type=f'image/{ext}', data=crop_img_bytes)

                # 返回图像块信息
                crop_img_id = hashlib.md5(crop_img_name.encode('utf-8')).hexdigest()
                results.append({
                    "file_uri": crop_img_uri,
                    "height": self.cut_height,
                    "width": self.cut_width,
                    "image_id": crop_img_id,
                })

        return pd.DataFrame(results)

    def _cut_annotations(self, source: DataFrame):
        """
        cut annotations
        """
        results = []

        for source_index, source_row in source.iterrows():

            # 读标注
            all_anno_records = source_row.get('annotations', [])

            # 获取划窗的所有左上角坐标
            imgH = source_row['height']
            imgW = source_row['width']
            offsets = self._get_offset(imgH, imgW)

            for (offset_h, offset_w) in offsets:
                crop_x1, crop_x2 = offset_w, min(offset_w + self.cut_width, imgW)
                crop_y1, crop_y2 = offset_h, min(offset_h + self.cut_height, imgH)
                patch = np.array((int(crop_x1), int(crop_y1), int(crop_x2), int(crop_y2)))

                # ------切标注-------
                crop_all_anno_records = []

                for anno_record in all_anno_records:
                    annos = anno_record.get("annotations")
                    if annos is None or len(annos) == 0:
                        continue

                    bboxes = np.array([[anno["bbox"][0], anno["bbox"][1],
                                        anno["bbox"][0] + anno["bbox"][2], anno["bbox"][1] + anno["bbox"][3]] for anno
                                       in annos])

                    # 计算重叠度
                    overlaps = annotation.bbox_overlaps(patch.reshape(-1, 4), bboxes.reshape(-1, 4), mode="iof")
                    overlaps = overlaps.reshape(-1)
                    if overlaps.size <= 0 or overlaps.max() <= 0:
                        continue

                    # 获取有效标注的索引
                    indx = np.where(overlaps > 0.2)[0]
                    if len(indx) == 0:
                        continue

                    # bboxes偏移、剪裁
                    bbox_offset = np.array([offset_w, offset_h, offset_w, offset_h], dtype=np.float32)
                    bboxes = bboxes - bbox_offset
                    bboxes[:, 0::2] = np.clip(bboxes[:, 0::2], 0, crop_x2 - crop_x1 - 1)
                    bboxes[:, 1::2] = np.clip(bboxes[:, 1::2], 0, crop_y2 - crop_y1 - 1)

                    crop_annos = []
                    for ix in indx:
                        bbox = bboxes[ix, ...]
                        crop_bbox = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]
                        if crop_bbox[2] <= 0 or crop_bbox[3] <= 0:
                            continue

                        labels = annos[ix].get("labels")
                        if labels is None or len(labels) == 0:
                            continue

                        # 先判断标注类型，再进行相应的切割处理
                        seg = annos[ix].get("segmentation")
                        rle = annos[ix].get("rle")

                        # case1: 多边形
                        if seg is not None and len(seg) >= 6:
                            seg_annos = self._process_polygon(seg, crop_x1, crop_y1, crop_x2, crop_y2, labels)
                            crop_annos.extend(seg_annos)
                            continue

                        # case2: 涂抹
                        if isinstance(rle, dict) and len(rle.keys()) == 2:
                            rle_annos = self._process_rle(rle, crop_x1, crop_y1, crop_x2, crop_y2, crop_bbox, labels)
                            crop_annos.extend(rle_annos)
                            continue

                        # case3: 矩形框
                        rectangle_anno = {
                            "id": string.generate_random_digits(6),
                            "bbox": crop_bbox,
                            "area": crop_bbox[2] * crop_bbox[3],
                            "labels": labels,
                        }
                        crop_annos.append(rectangle_anno)

                    if len(crop_annos) == 0:
                        continue

                    crop_all_anno_records.append({
                        "task_kind": anno_record['task_kind'],
                        "annotations": crop_annos,
                    })

                results.append({
                    "annotations": crop_all_anno_records
                })

        return pd.DataFrame(results)

    @staticmethod
    def _process_polygon(seg, crop_x1, crop_y1, crop_x2, crop_y2, labels):
        annos = []

        seg_pairs = [(seg[i], seg[i + 1]) for i in range(0, len(seg) - 1, 2)]
        crop_pairs = [(crop_x1, crop_y1), (crop_x1, crop_y2), (crop_x2, crop_y2), (crop_x2, crop_y1)]

        polygon = Polygon(seg_pairs)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        crop_polygon = Polygon(crop_pairs)
        intersection = polygon.intersection(crop_polygon)

        if intersection.is_empty:
            return annos

        if isinstance(intersection, MultiPolygon):
            polys = [poly for poly in intersection.geoms]
        elif isinstance(intersection, Polygon):
            polys = [intersection]
        else:
            return annos

        for p in polys:
            polygon_coords = list(p.exterior.coords)
            if len(polygon_coords) == 0:
                continue

            if polygon_coords[0] == polygon_coords[-1]:
                polygon_coords = polygon_coords[:-1]

            crop_seg = np.array(polygon_coords) - np.array([crop_x1, crop_y1])
            crop_seg[:, 0::2] = np.clip(crop_seg[:, 0::2], 0, crop_x2 - crop_x1 - 1)
            crop_seg[:, 1::2] = np.clip(crop_seg[:, 1::2], 0, crop_y2 - crop_y1 - 1)
            crop_seg = crop_seg.reshape(1, -1).tolist()[0]

            seg_anno = {
                "id": string.generate_random_digits(6),
                "segmentation": crop_seg,
                "bbox": list(annotation.polygon_bbox_with_wh(crop_seg)),
                "area": annotation.polygon_area(crop_seg),
                "labels": labels,
            }
            annos.append(seg_anno)
        return annos
    
    def _process_rle(self, rle, crop_x1, crop_y1, crop_x2, crop_y2, crop_bbox, labels):
        annos = []
        counts = rle.get("counts")
        size = rle.get("size")

        if counts is None or len(counts) == 0:
            return annos

        if size is None or len(size) != 2:
            return annos

        mask = annotation.rle2mask(size[0], size[1], counts)
        crop_mask = mask[crop_y1:crop_y2, crop_x1:crop_x2]

        # 不足的需要填充0像素
        pad_h = self.cut_height - crop_mask.shape[0] if crop_mask.shape[0] < self.cut_height else 0
        pad_w = self.cut_width - crop_mask.shape[1] if crop_mask.shape[1] < self.cut_width else 0
        crop_mask_padded = np.pad(crop_mask, ((0, pad_h), (0, pad_w)), mode='constant', constant_values=0)
        crop_rle = annotation.mask2rle(crop_mask_padded)

        rle_anno = {
            "id": string.generate_random_digits(6),
            "rle": {
                "counts": crop_rle,
                "size": [self.cut_height, self.cut_width],
            },
            "bbox": crop_bbox,
            "area": annotation.rle_area(crop_rle),
            "labels": labels,
        }
        annos.append(rle_anno)
        return annos

    def _get_offset(self, imgH, imgW):
        """
        获取划窗的全部左上角坐标
        """
        if imgH <= self.cut_height and imgW <= self.cut_width:
            offsets = [(0, 0)]
        else:
            max_offset_h = int(
                math.floor(imgH / (self.cut_height - self.overlapH)) * (self.cut_height - self.overlapH) + 1)
            max_offset_w = int(
                math.floor(imgW / (self.cut_width - self.overlapW)) * (self.cut_width - self.overlapW) + 1)

            offsets = [(int(oh), int(ow)) for ow in list(range(0, max_offset_w, int(self.cut_width - self.overlapW)))
                       for oh in list(range(0, max_offset_h, int(self.cut_height - self.overlapH)))]
        return offsets









