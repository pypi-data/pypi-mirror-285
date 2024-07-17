# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for different utility operations regarding drawing on images"""

import colorsys
import copy
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.geometric_classifiction import GeometricClassification
from mlcvzoo_base.api.data.segmentation import Segmentation
from mlcvzoo_base.api.data.types import ImageType, Point2f, PolygonTypeNP


def generate_detector_colors(num_classes: int):  # type: ignore
    """Generates a color palette for object detector.

    Args:
        num_classes: int, the number of classes to distinguish

    Returns:
        List[Tuples(int, int, int)] specifying bounding box color
        with len(List) == number of classes

    """

    # Generate colors for drawing bounding boxes.
    hsv_tuples = [(x / num_classes, 1.0, 1.0) for x in range(num_classes)]

    hsv_colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))

    rgb_colors = list(
        map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), hsv_colors)
    )

    np.random.seed(10101)  # Fixed seed for consistent colors across runs.
    np.random.shuffle(rgb_colors)  # Shuffle colors to decorrelate adjacent classes.
    np.random.seed(None)  # Reset seed to default.

    return rgb_colors


def draw_on_image(
    frame: ImageType,
    rgb_colors: List[Tuple[int, int, int]],
    cv2_font: int = cv2.FONT_HERSHEY_COMPLEX,
    bounding_boxes: Optional[List[BoundingBox]] = None,
    segmentations: Optional[List[Segmentation]] = None,
    predictions: Optional[List[GeometricClassification]] = None,
    flip_image: bool = False,
    draw_caption: Optional[bool] = True,
    thickness: Optional[int] = None,
    font_scale: float = 0.9,
    draw_score: Optional[bool] = True,
) -> ImageType:
    """Draws annotations on the given image

    Args:
        frame: Numpy array, the image
        rgb_colors: List of colors, for matching a class-name to an index of the rgb-color list
        cv2_font: int, font of cv2 textual annotations
        bounding_boxes: Optional List of BoundingBox objects
        segmentations: Optional List of Segmentation objects
        predictions: Optional List of GeometricClassification objects
        flip_image: Bool, whether to flip the image or not
        draw_caption: Optional bool, whether to draw a caption text or not
        thickness: Optional int, defines the thickness of the annotation lines
        font_scale: float, defines the size of a font
        draw_score: Whether to draw the score of the bounding boxes or segmentations

    Returns:
        Numpy array, the given image decorated with annotations
    """

    frame = copy.deepcopy(frame)

    _predictions: List[GeometricClassification] = []

    if bounding_boxes is not None:
        _predictions.extend(bounding_boxes)

    if segmentations is not None:
        _predictions.extend(segmentations)

    if predictions is not None:
        _predictions.extend(predictions)

    for prediction in _predictions:
        frame = draw_polygon_cv2(
            frame=frame,
            polygon=prediction.polygon(),
            color=rgb_colors[prediction.class_id],
            flip_image=flip_image,
            cv2_font=cv2_font,
            label=prediction.class_name,
            draw_caption=draw_caption,
            thickness=thickness,
            font_scale=font_scale,
            score=prediction.score if draw_score else None,
        )

    return frame


def draw_polygon_cv2(
    frame: ImageType,
    color: Tuple[int, int, int],
    polygon: Union[PolygonTypeNP, List[Point2f]],
    flip_image: bool = False,
    cv2_font: int = cv2.FONT_HERSHEY_COMPLEX,
    label: Optional[str] = None,
    draw_caption: Optional[bool] = True,
    thickness: Optional[int] = None,
    font_scale: float = 0.9,
    score: Optional[float] = None,
) -> ImageType:
    """Draw a polygon on a given image

    Args:
        frame: Numpy array, the image
        color: Tuple of three int values, a rgb color
        polygon: List of Tuples, the polygon coordinates
        flip_image: Bool, whether to flip the image or not
        cv2_font: int, font of cv2 textual annotations
        label: Optional string, label (class information) of polygon
        draw_caption: Optional bool, whether to draw a caption text or not
        thickness: Optional int, defines the thickness of the polygon lines
        font_scale: float, defines the size of a font
        score: Optional float, defines the confidence for the label of the polygon

    Returns:
        Numpy array, the given image decorated with a polygon
    """

    if polygon is None:
        return frame

    if thickness is None:
        thickness = (frame.shape[0] + frame.shape[1]) // 450

    if flip_image:
        # TODO: what to do when image is flipped?
        pass
    else:
        pts = np.asarray(polygon, np.int32)  # type: ignore[var-annotated]
        pts = pts.reshape((-1, 1, 2))

        frame = cv2.polylines(
            img=frame, pts=[pts], isClosed=True, color=color, thickness=thickness
        )

    if draw_caption and label is not None:
        if score is not None:
            caption = f"{label}_{score:.2f}"
        else:
            caption = label

        cv2.putText(
            img=frame,
            text=caption,
            org=(int(polygon[0][0]), int(polygon[0][1])),
            fontFace=cv2_font,
            fontScale=font_scale,
            color=color,
            thickness=thickness,
        )

    return frame


def draw_bbox_cv2(
    frame: ImageType,
    color: Tuple[int, int, int],
    box: Box,
    flip_image: bool = False,
    cv2_font: int = cv2.FONT_HERSHEY_COMPLEX,
    label: Optional[str] = None,
    draw_caption: Optional[bool] = True,
    thickness: Optional[int] = None,
    font_scale: float = 0.9,
    score: Optional[float] = None,
    text_origin: Optional[Tuple[int, int]] = None,
) -> ImageType:
    """Draws a bounding box on the given image

    Args:
        frame: Numpy array, the image
        color: Tuple of three int values, a rgb color
        box: Box, a bounding box object
        flip_image: Bool, whether to flip the image or not
        cv2_font: int, font of cv2 textual annotations
        label: Optional string, label (class information) of polygon
        draw_caption: Optional bool, whether to draw a caption text or not
        thickness: Optional int, defines the thickness of the box lines
        font_scale: float, defines the size of a font
        score: Optional float, defines the confidence for the label of the polygon
        text_origin: position of text in image

    Returns:
        Numpy array, the given image decorated with a bounding box
    """

    img_w = frame.shape[0]

    if thickness is None:
        thickness = (frame.shape[0] + frame.shape[1]) // 450

    if flip_image:
        frame = cv2.rectangle(
            frame,
            (img_w - box.xmin, box.ymin),
            (img_w - box.xmax, box.ymax),
            color,
            thickness,
        )
    else:
        frame = cv2.polylines(
            img=frame,
            pts=[box.polygon().astype(np.int_)],
            isClosed=True,
            color=color,
            thickness=thickness,
        )

    if draw_caption and label is not None:
        if text_origin is None:
            text_x = int(box.top_left[0])
            text_y = max(int(box.top_left[1]) - 5, 20)
            text_origin = (text_x, text_y)

        if score is not None:
            caption = f"{label} - {score:.2f}"
        else:
            caption = label

        cv2.putText(
            img=frame,
            text=caption,
            org=text_origin,
            fontFace=cv2_font,
            fontScale=font_scale,
            color=color,
            thickness=thickness,
        )

    return frame


def draw_on_pil_image(
    image: Union[ImageType, Image.Image],
    bounding_boxes: List[BoundingBox],
    font_path: str,
    rgb_colors: List[Tuple[int, int, int]],
    thickness: int = 2,
    fill_background: bool = True,
    is_ground_truth: bool = False,
) -> ImageType:
    """Draw a given list of bounding-boxes on a given image using pillow.

    Args:
        image: either a Numpy array or a PIL Image object
        bounding_boxes: List of BoundingBox objects
        font_path: String, path to the font file which should be used
        rgb_colors: List of colors, for matching a class-name to an index of the rgb-color list
        thickness: int, thickness of the box lines
        fill_background: Bool, whether to put the label on white background or not
        is_ground_truth: Bool, depending on ground truth or not, the label will be drawn
            in the upper left corner (no gt) or in the lower left corner (is gt)

    Returns:
        Numpy array, the given image decorated with annotations
    """

    white_color = (255, 255, 255, 15)

    if type(image) is np.ndarray:
        image = Image.fromarray(image)  # type: ignore[no-untyped-call]

    assert isinstance(image, Image.Image)

    font = ImageFont.truetype(  # type: ignore[no-untyped-call]
        font=font_path, size=np.floor(0.042 * image.size[1] + 0.1).astype("int32")
    )

    draw = ImageDraw.Draw(image)

    for bounding_box in bounding_boxes:
        label = "{} {:.2f}".format(bounding_box.class_name, bounding_box.score)

        # the anchor xy can be zero because we are only interested in the necessary
        # text width and height
        label_box = draw.textbbox(xy=(0, 0), text=label, font=font)
        label_size = (label_box[2], label_box[3])

        if is_ground_truth:
            text_origin = (
                float(bounding_box.box().xmin),
                float(bounding_box.box().ymax - label_size[1]),
            )
        else:
            if bounding_box.box().ymin - label_size[1] >= 0:
                text_origin = (
                    float(bounding_box.box().xmin),
                    float(bounding_box.box().ymin - label_size[1]),
                )
            else:
                text_origin = (
                    float(bounding_box.box().xmin),
                    float(bounding_box.box().ymin + 1),
                )

        color = rgb_colors[bounding_box.class_id]

        if fill_background:
            draw.rectangle(
                (
                    text_origin,
                    (text_origin[0] + label_size[0], text_origin[1] + label_size[1]),
                ),
                fill=white_color,
            )

            draw.text(text_origin, label, fill=(0, 0, 0, 15), font=font)
        else:
            draw.text(text_origin, label, fill=color, font=font)

        for draw_step in range(thickness):
            draw.rectangle(
                (
                    float(bounding_box.box().xmin + draw_step),
                    float(bounding_box.box().ymin + draw_step),
                    float(bounding_box.box().xmax - draw_step),
                    float(bounding_box.box().ymax - draw_step),
                ),
                outline=color,
            )

    del draw

    return np.asarray(image)
