# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Base class for image annotations """

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.ocr_perception import OCRPerception
from mlcvzoo_base.api.data.segmentation import Segmentation
from mlcvzoo_base.data_preparation.structs import CSVOutputStringFormats

logger = logging.getLogger(__name__)


# TODO: Ensure annotations and contained coordinates are valid at any point in time
@dataclass
class BaseAnnotation:
    """
    An image annotation.
    """

    # Absolute file path to the image of the annotation
    image_path: str
    # Absolute file path for the annotation
    annotation_path: str

    # shape of the image in the format (height, width)
    image_shape: Tuple[int, int]
    # List of classifications for this image. Can be used for training classification algorithms,
    # or to filter out images by their content.
    classifications: List[Classification] = field(default_factory=lambda: [])
    # List of bounding_boxes
    bounding_boxes: List[BoundingBox] = field(default_factory=lambda: [])
    # List of segmentations
    segmentations: List[Segmentation] = field(default_factory=lambda: [])
    # List of ocr perceptions (Text)
    ocr_perception: Optional[OCRPerception] = None

    image_dir: str = ""
    # TODO: rename to annotation_path_dir?
    #       When pascal-voc is used, the annotation_path_dir is a
    #       directory, when other formats are used,
    #       the annotation_path_dir is a path
    annotation_dir: str = ""
    replacement_string: str = ""

    def __repr__(self):  # type: ignore

        annotation_string = "BaseAnnotation("
        annotation_string += f'image_path="{self.image_path}", '
        annotation_string += f'annotation_path="{self.annotation_path}", '
        annotation_string += f"image_shape={tuple(self.image_shape)}, "

        annotation_string += f"classifications={self.classifications}, "
        annotation_string += f"bounding_boxes={self.bounding_boxes}, "
        annotation_string += f"segmentations={self.segmentations}, "

        annotation_string += f"ocr_perception={self.ocr_perception}, "

        annotation_string += f'image_dir="{self.image_dir}", '
        annotation_string += f'annotation_dir="{self.annotation_dir}", '
        annotation_string += f'replacement_string="{self.annotation_dir}")'

        return annotation_string

    def __eq__(self, other: object) -> bool:
        try:
            self.image_path = other.image_path  # type: ignore[attr-defined]

            if len(self.classifications) != len(other.classifications):  # type: ignore[attr-defined]
                return False
            if len(self.bounding_boxes) != len(other.bounding_boxes):  # type: ignore[attr-defined]
                return False
            if len(self.segmentations) != len(other.segmentations):  # type: ignore[attr-defined]
                return False

            for self_classification, other_classification in zip(
                self.classifications, other.classifications  # type: ignore[attr-defined]
            ):
                if self_classification != other_classification:
                    return False

            for self_bounding_box, other_bounding_box in zip(
                self.bounding_boxes, other.bounding_boxes  # type: ignore[attr-defined]
            ):
                if self_bounding_box != other_bounding_box:
                    return False

            for self_segmentation, other_segmentation in zip(
                self.segmentations, other.segmentations  # type: ignore[attr-defined]
            ):
                if self_segmentation != other_segmentation:
                    return False
        except AttributeError:
            return False

        return True

    def to_dict(self, raw_type: bool = False, reduced: bool = False) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the object. The raw_type defined whether
        all data attributes should be converted to python native data types or should
        be kept as is. The reduced parameter allows to create a more compact representation
        where only the main attributes of the object are present.

        Args:
            raw_type: Whether to convert the data attributes to python native data types
            reduced: Whether to create a more compact representation

        Returns:
            The created dictionary representation
        """
        if self.ocr_perception is not None:
            ocr_perception_dict = (
                self.ocr_perception if raw_type else self.ocr_perception.to_dict()
            )
        else:
            ocr_perception_dict = None

        return {
            "image_path": self.image_path,
            "annotation_path": self.annotation_path,
            "image_shape": self.image_shape,
            "classifications": (
                self.classifications
                if raw_type
                else [c.to_dict(raw_type=raw_type, reduced=reduced) for c in self.classifications]  # type: ignore[misc]
            ),
            "bounding_boxes": (
                self.bounding_boxes
                if raw_type
                else [b.to_dict(raw_type=raw_type, reduced=reduced) for b in self.bounding_boxes]  # type: ignore[misc]
            ),
            "segmentations": (
                self.segmentations
                if raw_type
                else [s.to_dict(raw_type=raw_type, reduced=reduced) for s in self.segmentations]  # type: ignore[misc]
            ),
            "ocr_perception": ocr_perception_dict,
            "image_dir": self.image_dir,
            "annotation_dir": self.annotation_dir,
            "replacement_string": self.replacement_string,
        }

    def get_height(self) -> int:
        """

        Returns:
            Height in pixels of the image for which the annotation is.

        """
        return int(self.image_shape[0])

    def get_width(self) -> int:
        """

        Returns:
            Width in pixels of the image for which the annotation is.

        """
        return int(self.image_shape[1])

    def get_bounding_boxes(self, include_segmentations: bool = True) -> List[BoundingBox]:
        """

        Args:
            include_segmentations (bool): Whether to return segmentations in the image

        Returns:
            list of BoundingBox objects. The bounding boxes (and segmentations) present
            in the image.

        """

        bounding_boxes: List[BoundingBox] = []

        bounding_boxes.extend([b for b in self.bounding_boxes])

        if include_segmentations:
            bounding_boxes.extend(
                [s.to_bounding_box(self.image_shape) for s in self.segmentations]
            )

        return bounding_boxes

    def to_csv_entry(
        self,
        use_difficult: bool,
        use_occluded: bool,
        include_surrounding_bboxes: bool = True,
        output_string_format: str = CSVOutputStringFormats.BASE,
    ) -> Optional[str]:
        """
        Transforms the BaseAnnotation object to CSV format.

        Args:
            use_difficult (bool): Whether or not to consider the BaseAnnotation object if marked
            with 'difficult' flag
            use_occluded(bool): Whether or not to consider the BaseAnnotation object marked
            with 'occluded' flag
            include_surrounding_bboxes (bool): Whether or not to consider the BaseAnnotation
            object if it is a segmentation.
            output_string_format (str): One of CSVOutputStringFormats. Defines the format
            type of the resulting CSV string.

        Returns:
            String in CSV Format, Optional. Depending on the input parameters and format type
            the method either returns a CSV sting or None.

        """

        if output_string_format == CSVOutputStringFormats.BASE:
            csv_entry = self.__to_base_entry(
                use_difficult=use_difficult,
                use_occluded=use_occluded,
                include_segmentations=include_surrounding_bboxes,
            )
        elif output_string_format == CSVOutputStringFormats.YOLO:
            csv_entry = self.__to_yolo_entry(
                use_difficult=use_difficult,
                use_occluded=use_occluded,
                include_segmentations=include_surrounding_bboxes,
            )
        else:
            logger.warning(
                "Could not find a valid output_string_format. Given format: %s",
                output_string_format,
            )
            csv_entry = ""

        return csv_entry

    def __to_base_entry(
        self, use_difficult: bool, use_occluded: bool, include_segmentations: bool
    ) -> Optional[str]:
        csv_line = ""

        for bounding_box in self.get_bounding_boxes(include_segmentations=include_segmentations):
            if not use_occluded and bounding_box.occluded:
                logger.debug("Skip occluded bounding-box: %r", bounding_box)
                continue

            if not use_difficult and bounding_box.difficult:
                logger.debug("Skip difficult bounding-box: %r", bounding_box)
                continue

            is_valid_box = self.is_valid_bounding_box(box=bounding_box.ortho_box())
            if is_valid_box:
                csv_line += "{},{},{},{},{} ".format(
                    bounding_box.ortho_box().xmin,
                    bounding_box.ortho_box().ymin,
                    bounding_box.ortho_box().xmax,
                    bounding_box.ortho_box().ymax,
                    bounding_box.class_name,
                )
            else:
                logger.warning(
                    "Skip bounding-box because it doesn't fulfill "
                    "the requirements check by is_valid_bounding_box: \n"
                    "   bounding-box: %s",
                    bounding_box,
                )

        if csv_line != "":
            csv_entry: Optional[str] = "{} {} {} {}\n".format(
                self.image_path, self.get_height(), self.get_width(), csv_line
            )
        else:
            csv_entry = None

        return csv_entry

    def __to_yolo_entry(
        self, use_difficult: bool, use_occluded: bool, include_segmentations: bool
    ) -> Optional[str]:
        csv_line = ""

        for bounding_box in self.get_bounding_boxes(include_segmentations=include_segmentations):
            if not use_occluded and bounding_box.occluded:
                logger.debug("Skip occluded bounding-box: %s", bounding_box)
                continue

            if not use_difficult and bounding_box.difficult:
                logger.debug("Skip difficult bounding-box: %s", bounding_box)
                continue

            is_valid_box = self.is_valid_bounding_box(box=bounding_box.ortho_box())
            if is_valid_box:
                csv_line += "{},{},{},{},{} ".format(
                    bounding_box.ortho_box().xmin,
                    bounding_box.ortho_box().ymin,
                    bounding_box.ortho_box().xmax,
                    bounding_box.ortho_box().ymax,
                    bounding_box.class_id,
                )
            else:
                logger.warning(
                    "Skip bounding-box because it doesn't fulfill "
                    "the requirements check by is_valid_bounding_box: \n"
                    "   bounding-box: %s",
                    bounding_box,
                )

        if csv_line != "":
            csv_entry: Optional[str] = "{} {}\n".format(self.image_path, csv_line)
        else:
            csv_entry = None

        return csv_entry

    def is_valid_bounding_box(self, box: Box) -> bool:
        """

        Args:
            box: a Box object

        Returns:
            True if the coordinates of the Annotation are valid, else False.

        """

        bbox_has_valid_coordinates: bool = (
            (0 <= box.xmin <= self.get_width())
            and (0 <= box.xmax <= self.get_width())
            and (0 <= box.ymin <= self.get_height())
            and (0 <= box.ymax <= self.get_height())
            and (box.xmin < box.xmax)
            and (box.ymin < box.ymax)
        )

        return bbox_has_valid_coordinates

    def copy_annotation(
        self,
        classifications: Optional[List[Classification]] = None,
        bounding_boxes: Optional[List[BoundingBox]] = None,
        segmentations: Optional[List[Segmentation]] = None,
    ) -> BaseAnnotation:
        return BaseAnnotation(
            image_path=self.image_path,
            annotation_path=self.image_path,
            image_shape=self.image_shape,
            classifications=(
                classifications if classifications is not None else self.classifications
            ),
            bounding_boxes=bounding_boxes if bounding_boxes is not None else self.bounding_boxes,
            segmentations=segmentations if segmentations is not None else self.segmentations,
            image_dir=self.image_dir,
            annotation_dir=self.annotation_dir,
            replacement_string=self.replacement_string,
        )
