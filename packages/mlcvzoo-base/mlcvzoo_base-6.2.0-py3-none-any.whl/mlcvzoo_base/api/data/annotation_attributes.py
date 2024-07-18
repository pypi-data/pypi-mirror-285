# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Dataclass that holds attributes of Annotation objects"""

from typing import Any, Dict, Optional


class AnnotationAttributes:
    """Class for describing different annotation attributes"""

    def __init__(
        self,
        difficult: bool = False,
        occluded: bool = False,
        content: str = "",
        background: bool = False,
        meta_attributes: Optional[Dict[Any, Any]] = None,
    ):
        self.__difficult: bool = difficult
        self.__occluded: bool = occluded
        self.__content: str = content
        self.__background: bool = background
        self.__meta_attributes: Dict[Any, Any] = (
            meta_attributes if meta_attributes is not None else {}
        )

    @property
    def difficult(self) -> bool:
        """Attribute that defines that an object annotation should be handled as
        "difficult" to see in the image. It can be used later on in the AnnotationHandler
        to filter out specific annotations.

        Returns:
            Whether the object should be handled as "difficult"
        """
        return self.__difficult

    @property
    def occluded(self) -> bool:
        """Attribute that defines that an annotation object is occluded by another
        object in the image. It can be used later on in the AnnotationHandler to filter
        out specific annotations.

        Returns:
            Whether the object should be handled as "occluded"
        """
        return self.__occluded

    @property
    def content(self) -> str:
        """Attribute that defines the textual content of an annotation object.

        Returns:
            The content of an annotation object
        """
        return self.__content

    @property
    def background(self) -> bool:
        """Attribute that defines that an object should be handled as "background".
        Those are objects which are not in the main focus for the training, because
        they are not positioned in the front of the image view. It is mainly used to
        describe the characteristic of an object with more than just "difficult"
        or occluded. It can be used later on in the annotation handler
        to filter out specific annotations.

        Returns:
            Whether the object should be handled as "background"
        """
        return self.__background

    @property
    def meta_attributes(self) -> Dict[Any, Any]:
        """Attribute that is utilized to store any meta attribute information that
        should be associated with an annotation object.

        Returns:
            The meta attributes of an annotation object as dictionary
        """
        return self.__meta_attributes
