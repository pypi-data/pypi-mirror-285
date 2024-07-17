# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Class for Bounding Box Annotation"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from mlcvzoo_base.api.data.annotation_attributes import AnnotationAttributes
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.geometric_classifiction import GeometricClassification
from mlcvzoo_base.api.data.types import PolygonTypeNP, polygon_equal
from mlcvzoo_base.api.structs import float_equality_precision


class BoundingBox(GeometricClassification, AnnotationAttributes):
    """
    A class for defining the data object consumed by ObjectDetection models.
    It is mainly described by the box attribute, which covers an rectangular
    area of an image and is associated with a certain class
    """

    def __init__(
        self,
        box: Box,
        class_identifier: ClassIdentifier,
        score: float,
        difficult: bool = False,
        occluded: bool = False,
        content: str = "",
        model_class_identifier: Optional[ClassIdentifier] = None,
        background: bool = False,
        meta_attributes: Optional[Dict[Any, Any]] = None,
    ):
        Classification.__init__(
            self,
            class_identifier=class_identifier,
            model_class_identifier=model_class_identifier,
            score=score,
        )
        AnnotationAttributes.__init__(
            self,
            difficult=difficult,
            occluded=occluded,
            content=content,
            background=background,
            meta_attributes=meta_attributes,
        )
        self.__box = box
        # The polygon is created lazily
        self.__polygon: Optional[PolygonTypeNP] = None

    def box(self) -> Box:
        return self.__box

    def ortho_box(self) -> Box:
        if self.__box.is_orthogonal():
            return self.__box

        return self.__box.ortho_box()

    def polygon(self) -> PolygonTypeNP:
        if self.__polygon is None:
            self.__polygon = self.__box.polygon()

        return self.__polygon

    def __eq__(self, other: object) -> bool:
        try:
            # NOTE: Since floats may very for different systems, don't check the score for equality,
            #       but allow it to be in a reasonable range
            return (
                self.box() == other.box()  # type: ignore[attr-defined]
                and self.class_identifier.class_id == other.class_identifier.class_id  # type: ignore[attr-defined]
                and self.class_identifier.class_name == other.class_identifier.class_name  # type: ignore[attr-defined]
                and self.model_class_identifier.class_id
                == other.model_class_identifier.class_id  # type: ignore[attr-defined]
                and self.model_class_identifier.class_name
                == other.model_class_identifier.class_name  # type: ignore[attr-defined]
                and self.occluded == other.occluded  # type: ignore[attr-defined]
                and self.difficult == other.difficult  # type: ignore[attr-defined]
                and self.background == other.background  # type: ignore[attr-defined]
                and self.content == other.content  # type: ignore[attr-defined]
                and self.meta_attributes == other.meta_attributes  # type: ignore[attr-defined]
                and math.isclose(a=self.score, b=other.score, abs_tol=float_equality_precision)  # type: ignore[attr-defined]
                and polygon_equal(polygon=self.polygon(), other_polygon=other.polygon())  # type: ignore[attr-defined]
            )
        except AttributeError:
            return False

    def __str__(self):  # type: ignore
        return (
            f"BoundingBox("
            f'class_identifier="{str(self.class_identifier)}", '
            f'model_class_identifier="{str(self.model_class_identifier)}", '
            f"box={self.__box}, "
            f"score={self.score}, "
            f"difficult={self.difficult}, "
            f"occluded={self.occluded}, "
            f"background={self.background}, "
            f'content="{self.content}", '
            f"meta_attributes={self.meta_attributes}"
            f")"
        )

    def __repr__(self):  # type: ignore
        return (
            f"BoundingBox("
            f"class_identifier={repr(self.class_identifier)}, "
            f"model_class_identifier={repr(self.model_class_identifier)}, "
            f"box={self.__box}, "
            f"score={self.score}, "
            f"difficult={self.difficult}, "
            f"occluded={self.occluded}, "
            f"background={self.background}, "
            f'content="{self.content}", '
            f"meta_attributes={self.meta_attributes}"
            f")"
        )

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
        if reduced:
            return {
                "box": self.__box if raw_type else self.__box.to_dict(),
                "class_id": self.class_id,
                "class_name": self.class_name,
                "model_class_id": self.model_class_identifier.class_id,
                "model_class_name": self.model_class_identifier.class_name,
                "score": self.score,
            }

        return {
            "box": self.__box if raw_type else self.__box.to_dict(),
            "class_identifier": (
                self.class_identifier if raw_type else self.class_identifier.to_dict()
            ),
            "model_class_identifier": (
                self.model_class_identifier if raw_type else self.model_class_identifier.to_dict()
            ),
            "score": self.score,
            "difficult": self.difficult,
            "occluded": self.occluded,
            "background": self.background,
            "content": self.content,
        }

    @staticmethod
    def from_dict(input_dict: Dict[str, Any], reduced: bool = False) -> BoundingBox:
        # fmt: off
        if reduced:
            return BoundingBox(**{
                "box": Box(**input_dict["box"]),
                "class_identifier": ClassIdentifier(**{
                    "class_id": input_dict["class_id"],
                    "class_name": input_dict["class_name"],
                }),
                "model_class_identifier": ClassIdentifier(**{
                    "class_id": input_dict["model_class_id"],
                    "class_name": input_dict["model_class_name"],
                }),
                "score": input_dict["score"],
                "difficult": False,
                "occluded": False,
                "background": False,
                "content": "",
            })
        else:
            return BoundingBox(**{
                "box": Box(**input_dict["box"]),
                "class_identifier": ClassIdentifier(
                    **input_dict["class_identifier"]
                ),
                "model_class_identifier": ClassIdentifier(
                    **input_dict["model_class_identifier"]
                ),
                "score": input_dict["score"],
                "difficult": input_dict["difficult"],
                "occluded": input_dict["occluded"],
                "background": input_dict["background"],
                "content": input_dict["content"],
            })
        # fmt: on

    def to_json(self) -> Any:
        return self.to_dict(raw_type=False)

    def to_list(self) -> List[int]:
        """Transforms the BoundingBox object to a list of its coordinates.

        REMARK: This function uses the ortho_box() since is only defined for
                orthogonal bounding boxes

        Returns:
            A 1x4 list of the objects coordinates [xmin, ymin, xmax, ymax]
        """
        return self.ortho_box().to_list()

    def copy_bounding_box(self, class_identifier: ClassIdentifier) -> BoundingBox:
        """Constructs a copy of the BoundingBox object with the given class-identifier.

        Args:
            class_identifier: The class-identifier of the new BoundingBox object

        Returns:
            The created copy
        """
        return BoundingBox(
            box=self.__box,
            class_identifier=class_identifier,
            score=self.score,
            difficult=self.difficult,
            occluded=self.occluded,
            background=self.background,
            content=self.content,
            model_class_identifier=self.model_class_identifier,
        )
