# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for different utility operations during object detection evaluation"""

import logging
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from terminaltables import AsciiTable

from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.geometric_classifiction import GeometricClassification
from mlcvzoo_base.api.data.metrics import compute_iou
from mlcvzoo_base.api.data.types import ImageType, PolygonTypeNP
from mlcvzoo_base.evaluation.geometric.data_classes import (
    CONFUSION_MATRIX_DICT_TYPE,
    METRIC_DICT_TYPE,
    METRIC_IMAGE_INFO_TYPE,
    MetricImageInfo,
)
from mlcvzoo_base.evaluation.geometric.structs import GeometricSizeTypes

logger = logging.getLogger(__name__)


def get_bbox_size_type(box: Box, image_shape: Tuple[int, int] = (1080, 1440)) -> str:
    """
    Args:
        box: Box object
        image_shape: Tuple of ints, describing the image shape

    Returns:
        a String, the category of the size of the box (small, medium or large)
    """

    bbox_height = (int(box.ymax) - int(box.ymin)) / image_shape[0] * 480
    bbox_width = (int(box.xmax) - int(box.xmin)) / image_shape[1] * 640

    bbox_sqrt_area = math.sqrt(bbox_height * bbox_width)

    small_sqrt_area_limit = 32
    large_sqrt_area_limit = 96

    if bbox_sqrt_area <= small_sqrt_area_limit:
        return str(GeometricSizeTypes.BBOX_SMALL)

    elif small_sqrt_area_limit < bbox_sqrt_area <= large_sqrt_area_limit:
        return str(GeometricSizeTypes.BBOX_MEDIUM)

    else:
        # Any other case is bbox_sqrt_area > large_sqrt_area_limit:
        return str(GeometricSizeTypes.BBOX_LARGE)


def compute_max_prediction(
    prediction: GeometricClassification,
    gt_predictions: List[GeometricClassification],
) -> Tuple[float, GeometricClassification]:
    """
    Determine the ground truth bounding box that has the highest overlap with
    the given (predicted) bounding box

    Args:
        prediction: BoundingBox object
        gt_predictions: List of BoundingBox objects

    Returns:
        A Tuple containing the ground truth bounding box wit the highest overlap and the
        according maximum overlap score (IOU metric)
    """

    overlaps = []
    for index, gt_object in enumerate(gt_predictions):
        overlaps.append(compute_iou(gt_object, prediction))

    np_overlaps = np.asarray([overlaps])

    # get the index of the gt box with the highest overlap (alongside the correct axis)
    max_gt_bbox_index = int(np.argmax(np_overlaps, axis=1))

    # 0 as index of the first element of 2D-array of shape (1, K)
    max_overlap = float(np_overlaps[0, max_gt_bbox_index])

    assigned_gt_object = gt_predictions[max_gt_bbox_index]

    return max_overlap, assigned_gt_object


def generate_metric_table(
    metrics_dict: METRIC_DICT_TYPE, iou_threshold: float, reduced: bool = False
) -> AsciiTable:
    """
    Generate a 'AsciiTable' object filled with the metrics of a object detection evaluation.
    The columns display the attributes of dataclass
    the mlcvzoo.evaluation.geometric.data_classes.GeometricMetrics.

    Args:
        metrics_dict: The dictionary containing the metrics that should be formed into a table
        iou_threshold: The iou-threshold for which the table should be generated
        reduced: Whether to use all available metrics, or only the basic ones

    Returns:
        The generated 'AsciiTable'
    """

    table_data = [
        [
            f"{'class':15s}",
            f"{'TP':6s}",
            f"{'FP':6s}",
            f"{'FN':6s}",
            f"{'CP':6s}",
            f"{'Recall':10s}",
            f"{'Precision':10s}",
            f"{'F1':10s}",
            f"{'AP':8s}",
            f"{'AVG_TP_IOU':8s}",
        ]
    ]
    row_data: List[Any]
    for bbox_size_type in GeometricSizeTypes.get_values_as_list(class_type=GeometricSizeTypes):
        if bbox_size_type != GeometricSizeTypes.BBOX_ALL:
            row_data = [f"SIZE: {bbox_size_type}", "", "", "", "", "", ""]
            table_data.append(row_data)

        for class_name, od_metric in metrics_dict[iou_threshold][bbox_size_type].items():
            if od_metric.COUNT > 0:
                row_data = [
                    class_name,
                    f"{od_metric.TP}",
                    f"{od_metric.FP}",
                    f"{od_metric.FN}",
                    f"{od_metric.COUNT}",
                    f"{od_metric.RC:.4f}",
                    f"{od_metric.PR:.4f}",
                    f"{od_metric.F1:.4f}",
                    f"{od_metric.AP:.4f}",
                    f"{od_metric.AVG_TP_IOU:.4f}",
                ]
            else:
                row_data = [
                    class_name,
                    0,
                    0,
                    0,
                    0,
                    f"{0.0:.4f}",
                    f"{0.0:.4f}",
                    f"{0.0:.4f}",
                    f"{0.0:.4f}",
                    f"{0.0:.4f}",
                ]

            table_data.append(row_data)

        if bbox_size_type != "l":
            row_data = ["", "", "", "", "", "", ""]
            table_data.append(row_data)

    table = AsciiTable(table_data)
    table.inner_footing_row_border = False

    return table


def generate_fn_fp_confusion_matrix_table_from_dict(
    confusion_matrix: CONFUSION_MATRIX_DICT_TYPE,
) -> AsciiTable:
    """
    Generate a 'AsciiTable' object that represents the confusion matrix
    of an objection detection evaluation output. The confusion matrix indicates
    which false negative bounding boxes of a certain class could be matches to
    false positive bounding boxes of another class.

    Args:
        confusion_matrix: The confusion Matrix as 2D Dict

    Returns:
        The generated 'AsciiTable'
    """

    table_data = [[""]]

    for class_identifier_str in confusion_matrix.keys():
        table_data[0].append(class_identifier_str)

    row_data: List[Any]
    for row_class_identifier_str in confusion_matrix.keys():
        row_data = [row_class_identifier_str]
        for column_class_identifier_str in confusion_matrix[row_class_identifier_str].keys():
            row_data.append(
                f"{confusion_matrix[row_class_identifier_str][column_class_identifier_str]}"
            )
        table_data.append(row_data)

    table = AsciiTable(table_data)
    table.inner_footing_row_border = False

    return table


def create_fp_fn_images(
    metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
) -> Dict[str, Dict[str, ImageType]]:
    """

    Args:
        metrics_image_info_dict:

    Returns:
        Dict - 1st Key: Image name of the fp-fn image
               2nd Key: Class name of the fp-fn image
               Value: Image as np array
    """
    img_directory_id_dict: Dict[str, int] = dict()

    fp_fn_image_dict: Dict[str, Dict[str, ImageType]] = {}

    for class_identifier_str, image_dict in metrics_image_info_dict.items():
        for image_path, metric_image_info in image_dict.items():
            image_id, img_directory_id_dict = generate_img_id_map(
                image_path=image_path, img_directory_id_dict=img_directory_id_dict
            )

            if metric_image_info.gt_evaluation_entry is not None:
                gt_count = len(metric_image_info.gt_evaluation_entry.evaluation_objects)
            else:
                gt_count = 0

            if metric_image_info.tp_evaluation_entry is not None:
                tp_count = len(metric_image_info.tp_evaluation_entry.evaluation_objects)
            else:
                tp_count = 0

            if metric_image_info.fp_evaluation_entry is not None:
                fp_count = len(metric_image_info.fp_evaluation_entry.evaluation_objects)
            else:
                fp_count = 0

            if metric_image_info.fn_evaluation_entry is not None:
                fn_count = len(metric_image_info.fn_evaluation_entry.evaluation_objects)
            else:
                fn_count = 0

            image_basename, image_ext = os.path.splitext(os.path.basename(image_path))

            # Only create images when something False Positives or False Negatives are present
            # for this image
            if fp_count > 0 or fn_count > 0:
                fp_fn_image_name = (
                    f"metric_image_info_{class_identifier_str}/"
                    f"{image_basename}_"
                    f"ID_{image_id}_"
                    f"GT_{gt_count}_"
                    f"TP_{tp_count}_"
                    f"FP_{fp_count}_"
                    f"FN_{fn_count}_"
                    f"{image_ext}"
                )
                logger.debug(
                    "Create fp-fn image '%s' for image '%s'" % (fp_fn_image_name, image_path)
                )

                image = __create_fp_fn_image(
                    image_path=image_path,
                    metric_image_info=metric_image_info,
                )
                if fp_fn_image_name not in fp_fn_image_dict:
                    fp_fn_image_dict[fp_fn_image_name] = {}

                fp_fn_image_dict[fp_fn_image_name][class_identifier_str] = image

    return fp_fn_image_dict


def __draw_polygon(
    image: ImageType, polygon: PolygonTypeNP, color: Tuple[int, int, int], thickness: int
) -> ImageType:
    pts = np.array(polygon, np.int32)  # type: ignore[var-annotated]
    pts = pts.reshape((-1, 1, 2))

    image = cv2.polylines(img=image, pts=[pts], isClosed=True, color=color, thickness=thickness)

    return image


def __create_fp_fn_image(image_path: str, metric_image_info: MetricImageInfo) -> ImageType:
    image = cv2.imread(image_path)

    tp_color = (0, 255, 0)  # => red color for false positive boxes
    fp_color = (0, 0, 255)  # => red color for false positive boxes
    fn_color = (255, 0, 0)  # => black color for false negative boxes
    gt_color = (255, 255, 255)  # => white color for ground truth data

    if metric_image_info.gt_evaluation_entry is not None:
        for geometric_object in metric_image_info.gt_evaluation_entry.evaluation_objects:
            image = __draw_polygon(
                image=image, polygon=geometric_object.polygon(), color=gt_color, thickness=6
            )
    if metric_image_info.tp_evaluation_entry is not None:
        for geometric_object in metric_image_info.tp_evaluation_entry.evaluation_objects:
            image = __draw_polygon(
                image=image, polygon=geometric_object.polygon(), color=tp_color, thickness=6
            )

    if metric_image_info.fn_evaluation_entry is not None:
        for geometric_object in metric_image_info.fn_evaluation_entry.evaluation_objects:
            image = __draw_polygon(
                image=image, polygon=geometric_object.polygon(), color=fn_color, thickness=3
            )

    if metric_image_info.fp_evaluation_entry is not None:
        for geometric_object in metric_image_info.fp_evaluation_entry.evaluation_objects:
            image = __draw_polygon(
                image=image, polygon=geometric_object.polygon(), color=fp_color, thickness=3
            )

    return image  # type: ignore[no-any-return]


def generate_img_id_map(
    image_path: str, img_directory_id_dict: Dict[str, int]
) -> Tuple[int, Dict[str, int]]:
    """
    Generates an index (id) for the given image_path.

    Args:
        image_path: String, path to an image
        img_directory_id_dict: Dictionary of image paths to index in directory list

    Returns: a Tuple of image index and (updated) img_directory_id_dict
    """
    # TODO: What happens when two images get the same index?
    #  It could be possible that due to an extension of the dict two images could get the same index,
    #  because the indices after the added and sorted image are increased by 1.
    #  Therefore all other entries of the subsequent images (in sorted order) are wrong.

    image_dir = os.path.dirname(image_path)
    file_extension = os.path.splitext(image_path)[1]

    if image_path not in img_directory_id_dict:
        path_generator = Path(image_dir).glob(f"**/*{file_extension}")

        file_list = [str(p) for p in path_generator]

        file_list.sort()

        for index, file_path in enumerate(file_list):
            img_directory_id_dict[file_path] = index

    return img_directory_id_dict[image_path], img_directory_id_dict
