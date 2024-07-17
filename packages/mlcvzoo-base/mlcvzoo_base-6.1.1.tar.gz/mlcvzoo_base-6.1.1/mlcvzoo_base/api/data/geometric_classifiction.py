# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Data class that holds attributes of Classification objects"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from mlcvzoo_base.api.data.box import Box, GeometricPerception
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.data.types import PolygonTypeNP


class GeometricClassification(GeometricPerception, ABC, Classification):
    def __init__(
        self,
        class_identifier: ClassIdentifier,
        score: float,
        model_class_identifier: Optional[ClassIdentifier] = None,
    ) -> None:
        Classification.__init__(
            self,
            class_identifier=class_identifier,
            model_class_identifier=model_class_identifier,
            score=score,
        )

    @abstractmethod
    def box(self) -> Box:
        raise NotImplementedError(f"Call of .box() from abstract class {self.__class__}")

    @abstractmethod
    def ortho_box(self) -> Box:
        raise NotImplementedError(f"Call of .ortho_box() from abstract class {self.__class__}")

    @abstractmethod
    def polygon(self) -> PolygonTypeNP:
        raise NotImplementedError(f"Call of .polygon() from abstract class {self.__class__}")
