# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

import copy
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from tqdm import tqdm

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.geometric_classifiction import GeometricClassification
from mlcvzoo_base.evaluation.geometric.data_classes import (
    CONFUSION_MATRIX_DICT_TYPE,
    DEFAULT_FLOAT_VALUE,
    DEFAULT_INT_VALUE,
    METRIC_DICT_TYPE,
    METRIC_IMAGE_INFO_TYPE,
    EvaluationEntry,
    GeometricEvaluationComputingData,
    GeometricEvaluationMetrics,
    GeometricMetrics,
    MetricImageInfo,
)
from mlcvzoo_base.evaluation.geometric.structs import GeometricSizeTypes
from mlcvzoo_base.evaluation.geometric.utils import (
    compute_max_prediction,
    get_bbox_size_type,
)
from mlcvzoo_base.third_party.py_faster_rcnn.voc_ap import voc_ap

logger = logging.getLogger(__name__)


class EvaluationContexts(str, Enum):
    ALL = "ALL"
    OBJECT_DETECTION = "OBJECT_DETECTION"
    ROTATED_OBJECT_DETECTION = "ROTATED_OBJECT_DETECTION"
    SEGMENTATION = "SEGMENTATION"

    def __repr__(self):  # type: ignore[no-untyped-def]
        return str.__repr__(self)

    def __str__(self):  # type: ignore[no-untyped-def]
        return str.__str__(self)


class MetricsComputation:
    """
    Main class for handling the evaluation of object detection models.
    """

    iou_thresholds_ap_50_95: List[float] = [
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
    ]

    def __init__(
        self,
        model_specifier: str,
        iou_thresholds: List[float],
        gt_annotations: List[BaseAnnotation],
        predictions_list: List[List[GeometricClassification]],
        mapper: AnnotationClassMapper,
        evaluation_context: str = EvaluationContexts.ALL.value,
    ):
        self.model_specifier = model_specifier
        self.iou_thresholds: List[float] = iou_thresholds
        self.dataset_length: int = len(gt_annotations)

        self.class_identifier_list: List[ClassIdentifier] = []

        self.mapper = mapper
        self.class_identifier_list = self.mapper.create_class_identifier_list()

        # Remove duplicates
        self.class_identifier_list = list(dict.fromkeys(self.class_identifier_list))

        # 1st key: dataset index
        # 2nd key: class-identifier
        self._all_predictions_dict: Dict[int, Dict[str, List[EvaluationEntry]]] = {
            i: {} for i in range(self.dataset_length)
        }
        self._all_gt_dict: Dict[int, Dict[str, List[EvaluationEntry]]] = {
            i: {} for i in range(self.dataset_length)
        }

        self.model_metrics: GeometricEvaluationMetrics = GeometricEvaluationMetrics(
            model_specifier=self.model_specifier
        )
        self.computing_data: GeometricEvaluationComputingData = GeometricEvaluationComputingData()

        process_bar = tqdm(
            zip(gt_annotations, predictions_list),
            desc=f"Compute metrics",
        )

        for index, (gt_annotation, predictions) in enumerate(process_bar):
            self.__update_from_prediction(
                index=index,
                image_path=gt_annotation.image_path,
                gt_objects=MetricsComputation.__filter_gt_objects(
                    evaluation_context=evaluation_context, gt_annotation=gt_annotation
                ),
                predictions=predictions,
            )

    @staticmethod
    def __filter_gt_objects(
        evaluation_context: str, gt_annotation: BaseAnnotation
    ) -> List[GeometricClassification]:
        gt_objects: List[GeometricClassification]
        if evaluation_context == EvaluationContexts.ALL.value:
            gt_objects = gt_annotation.bounding_boxes + gt_annotation.segmentations  # type: ignore[assignment, operator]
        elif evaluation_context == EvaluationContexts.OBJECT_DETECTION.value:
            gt_objects = []
            for bounding_box in gt_annotation.bounding_boxes:
                if bounding_box.box().is_orthogonal():
                    gt_objects.append(bounding_box)
        elif evaluation_context == EvaluationContexts.ROTATED_OBJECT_DETECTION.value:
            gt_objects = gt_annotation.bounding_boxes  # type: ignore[assignment]
        elif evaluation_context == EvaluationContexts.SEGMENTATION.value:
            gt_objects = gt_annotation.segmentations  # type: ignore[assignment]
        else:
            raise ValueError(
                "EvaluationContext '%s' not valid, must be one of %s"
                % (
                    evaluation_context,
                    [EvaluationContexts.OBJECT_DETECTION, EvaluationContexts.SEGMENTATION],
                )
            )

        return gt_objects

    def get_metrics_dict(self) -> METRIC_DICT_TYPE:
        return self.model_metrics.metrics_dict

    def get_metrics_image_info_dict(
        self,
    ) -> METRIC_IMAGE_INFO_TYPE:
        return self.model_metrics.metrics_image_info_dict

    @staticmethod
    def get_overall_ap(metrics_dict: METRIC_DICT_TYPE, iou_threshold: float) -> float:
        """
        Calculate AP metric over every class specific AP metric for bounding boxes of all sizes.

        Args:
            metrics_dict: The dictionary that stores the relevant metric data, which is the
                          basis for the calculation
            iou_threshold: The iou threshold for which the AP metric should be computed

        Returns:
            The computed overall AP metric
        """

        if iou_threshold in metrics_dict:
            class_metrics = metrics_dict[iou_threshold][GeometricSizeTypes.BBOX_ALL]
        else:
            raise ValueError(
                "Can not compute overall AP for iou-threshold=%s, "
                "no data is given in the metrics-dict.",
                iou_threshold,
            )

        ap_list: List[float] = [class_metric.AP for class_metric in class_metrics.values()]
        return sum(ap_list) / len(ap_list)

    @staticmethod
    def compute_average_ap(model_metrics: GeometricEvaluationMetrics) -> float:
        """
        Compute the average of the AP metric for every
        overall AP (average over all classes) of all iou-thresholds
        in the metrics_dict.

        Args:
            model_metrics: The model-metrics for which to compute the average ap

        Returns:
            The computed average AP metric
        """
        ap_list: List[float] = [
            MetricsComputation.get_overall_ap(
                metrics_dict=model_metrics.metrics_dict,
                iou_threshold=iou_threshold,
            )
            for iou_threshold in model_metrics.metrics_dict.keys()
        ]
        return sum(ap_list) / len(ap_list)

    @staticmethod
    def get_ap_50_95(model_metrics: GeometricEvaluationMetrics) -> float:
        """
        Compute the COCO mAP metric which is defined as the AP
        metric for the iou-thresholds = [0.5, 0.55, ..., 0.95].

        Args:
            model_metrics: The model-metrics for which to compute the COCO mAP

        Returns:
            The computed COCO mAP
        """
        return sum(
            [
                MetricsComputation.get_overall_ap(
                    metrics_dict=model_metrics.metrics_dict, iou_threshold=iou
                )
                for iou in MetricsComputation.iou_thresholds_ap_50_95
            ]
        ) / len(MetricsComputation.iou_thresholds_ap_50_95)

    @staticmethod
    def get_ap_50(model_metrics: GeometricEvaluationMetrics) -> float:
        """
        Compute the AP50 metric which is defined as the AP
        metric for the iou-threshold=0.5

        Args:
            model_metrics: The model-metrics for which to compute the COCO mAP

        Returns:
            The computed AP50
        """

        return MetricsComputation.get_overall_ap(
            metrics_dict=model_metrics.metrics_dict, iou_threshold=0.5
        )

    def __reset_main_dictionaries(
        self,
    ) -> None:
        for class_identifier in self.class_identifier_list:
            self.model_metrics.metrics_image_info_dict[str(class_identifier)] = dict()

        for bbox_size_type in GeometricSizeTypes.get_values_as_list(class_type=GeometricSizeTypes):
            self.computing_data.gt_counter_dict[bbox_size_type] = dict()

            for class_identifier in self.class_identifier_list:
                self.computing_data.gt_counter_dict[bbox_size_type][str(class_identifier)] = 0

        for iou_thresh in self.iou_thresholds:
            self.model_metrics.metrics_dict[iou_thresh] = dict()

            for bbox_size_type in GeometricSizeTypes.get_values_as_list(
                class_type=GeometricSizeTypes
            ):
                self.model_metrics.metrics_dict[iou_thresh][bbox_size_type] = dict()

                for class_identifier in self.class_identifier_list:
                    self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
                        str(class_identifier)
                    ] = GeometricMetrics()

    def __reset_computing_dictionaries(self) -> None:
        for iou_thresh in self.iou_thresholds:
            self.computing_data.false_positives_dict[iou_thresh] = dict()
            self.computing_data.true_positives_dict[iou_thresh] = dict()
            self.computing_data.scores[iou_thresh] = dict()

            for bbox_size in GeometricSizeTypes.get_values_as_list(class_type=GeometricSizeTypes):
                self.computing_data.false_positives_dict[iou_thresh][bbox_size] = np.zeros((0,))
                self.computing_data.true_positives_dict[iou_thresh][bbox_size] = np.zeros((0,))

                self.computing_data.scores[iou_thresh][bbox_size] = np.zeros((0,))

        for bbox_size in GeometricSizeTypes.get_values_as_list(class_type=GeometricSizeTypes):
            self.computing_data.iou_dict[bbox_size] = np.zeros((0,))

    def compute_metrics(
        self,
    ) -> GeometricEvaluationMetrics:
        """
        Compute MAP Metrics

        Returns:
            The metrics dictionary in the form of:

            1st key: The iou-threshold under which the metrics should be computed
            2nd key: The type of the size of the geometric object
            3rd key: The class-identifier as string
            Value: The computed metrics

            Dict[IOU_THRESHOLD][GeometricSizeTypes.BBOX_SIZE_TYPE][CLASS_IDENTIFIER_STRING] = GeometricMetrics
        """

        self.__reset_main_dictionaries()

        for class_identifier in self.class_identifier_list:
            self.__reset_computing_dictionaries()

            self.__fill_computing_data(
                class_identifier=class_identifier,
            )

            self.__compute_metrics(class_identifier=class_identifier)

        return GeometricEvaluationMetrics(
            model_specifier=self.model_specifier,
            metrics_dict=self.get_metrics_dict(),
            metrics_image_info_dict=self.get_metrics_image_info_dict(),
        )

    def __update_from_prediction(
        self,
        index: int,
        image_path: str,
        gt_objects: List[GeometricClassification],
        predictions: List[GeometricClassification],
    ) -> None:
        """
        Update the main computing dictionaries given the information from the ground truth
        annotation and predicted bounding boxes at the dataset index.

        Args:
            index: The index of the dataset where to update the data
            image_path: The image-path for which the internal annotation data dictionaries should be updated
            predictions: The predicted perceptions for this index (data item)

        Returns:
            None
        """

        logger.debug("Get metrics for annotation: \n" "  - image-path:       %s\n" % image_path)

        self._all_gt_dict = MetricsComputation.__update_annotation_data_dict(
            class_identifier_list=self.class_identifier_list,
            all_annotations_dict=self._all_gt_dict,
            index=index,
            image_path=image_path,
            geometric_objects=gt_objects,
        )

        self._all_predictions_dict = MetricsComputation.__update_annotation_data_dict(
            class_identifier_list=self.class_identifier_list,
            all_annotations_dict=self._all_predictions_dict,
            index=index,
            image_path=image_path,
            geometric_objects=predictions,
        )

    @staticmethod
    def __update_annotation_data_dict(
        class_identifier_list: List[ClassIdentifier],
        all_annotations_dict: Dict[int, Dict[str, List[EvaluationEntry]]],
        index: int,
        image_path: str,
        geometric_objects: List[GeometricClassification],
    ) -> Dict[int, Dict[str, List[EvaluationEntry]]]:
        """
        Update the annotation data dict at the specified index with the per class geometric object
        information.

        Args:
            class_identifier_list: List of class identifier for which to update the annotation
                                   data
            all_annotations_dict: The dictionary to update
            index: int, index of entry (image) which annotations should be updated
            image_path: The image path for which the EvaluationEntries should be created

        Returns:
            The updated annotation data dict in the form of:

            1st key: The index of the dataset
            2nd key: The class-identifier as string
            Value: The list of geometrics objects that are fitting to the respective keys

            Dict[INDEX][CLASS_IDENTIFIER_STRING] = List[EvaluationEntry]
        """

        if len(geometric_objects) == 0:
            # No update necessary
            return all_annotations_dict

        # Gather (BoundingBox / Annotation) data for each class-id.
        # This is needed to be able to compute detailed metrics
        # for each class-id.
        for class_identifier in class_identifier_list:
            # Have to find all bounding-boxes for a specific class-id.
            # In order to have access to the information about the image-path,
            # we need to store an annotation object, rather than a single bounding-box.
            # Despite the fact that for the metric calculation itself the bounding-box
            # information is enough.
            # For purposes like: draw/log all false-positive bounding-boxes for specific
            # images we need to have the information about the image-path
            #   => therefore use BaseAnnotation and not BoundingBox alone
            all_annotations_dict[index][str(class_identifier)] = []
            for s in geometric_objects:
                if s.class_id == class_identifier.class_id:
                    all_annotations_dict[index][str(class_identifier)].append(
                        EvaluationEntry(
                            image_path=image_path,
                            evaluation_objects=[type(s).from_dict(s.to_dict())],  # type: ignore[list-item]
                        )
                    )

        return all_annotations_dict

    def __update_tp_fp_data(
        self, is_true_positive: bool, iou_thresh: float, bbox_size_type: str, iou_value: float
    ) -> None:
        if is_true_positive:
            tp_value = 1
            fp_value = 0
        else:
            tp_value = 0
            fp_value = 1

        # Update dictionary for overall mAP computation
        self.computing_data.true_positives_dict[iou_thresh][GeometricSizeTypes.BBOX_ALL] = (
            np.append(
                self.computing_data.true_positives_dict[iou_thresh][GeometricSizeTypes.BBOX_ALL],
                tp_value,
            )
        )
        self.computing_data.false_positives_dict[iou_thresh][GeometricSizeTypes.BBOX_ALL] = (
            np.append(
                self.computing_data.false_positives_dict[iou_thresh][GeometricSizeTypes.BBOX_ALL],
                fp_value,
            )
        )
        self.computing_data.iou_dict[GeometricSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.iou_dict[GeometricSizeTypes.BBOX_ALL],
            iou_value,
        )

        # Update dictionary for size specific mAP computation
        self.computing_data.true_positives_dict[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.true_positives_dict[iou_thresh][bbox_size_type],
            tp_value,
        )
        self.computing_data.false_positives_dict[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.false_positives_dict[iou_thresh][bbox_size_type],
            fp_value,
        )
        self.computing_data.iou_dict[bbox_size_type] = np.append(
            self.computing_data.iou_dict[bbox_size_type],
            iou_value,
        )

    def __update_computation_dictionaries(
        self,
        prediction: GeometricClassification,
        iou_thresh: float,
        unmatched_gt_objects: List[GeometricClassification],
    ) -> List[GeometricClassification]:
        bbox_size_type: str = get_bbox_size_type(prediction.ortho_box())

        # if the ground truth data for this image indicates that nothing has to be detected,
        # indicate this box as False-Positive right away!
        if len(unmatched_gt_objects) == 0:
            self.__update_tp_fp_data(
                is_true_positive=False,
                iou_thresh=iou_thresh,
                bbox_size_type=bbox_size_type,
                iou_value=0.0,
            )
        else:
            max_overlap, assigned_evaluation_entry = compute_max_prediction(
                prediction=prediction, gt_predictions=unmatched_gt_objects
            )

            # If max-overlap fulfills given threshold
            # the detected box is treated as TP, otherwise as FP
            if (
                max_overlap
                >= iou_thresh
                # and
                # if this prediction has not already been assigned as valid,
                # treat it as true positive, otherwise as false positive
                # assigned_prediction not in self.detected_annotations[iou_thresh]
            ):
                unmatched_gt_objects.remove(assigned_evaluation_entry)

                # NOTE: In order to have correct metrics, the size of a true positive
                #       bounding box is the same as for the matching ground truth bounding box
                bbox_size_type = get_bbox_size_type(assigned_evaluation_entry.ortho_box())

                # Update as True-Positive
                self.__update_tp_fp_data(
                    is_true_positive=True,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                    iou_value=max_overlap,
                )
            else:
                # Update as False-Positive
                self.__update_tp_fp_data(
                    is_true_positive=False,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                    iou_value=0.0,
                )

        # append the score of the current bounding-box to the overall  scores list
        self.computing_data.scores[iou_thresh][GeometricSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.scores[iou_thresh][GeometricSizeTypes.BBOX_ALL],
            prediction.score,
        )

        # append the score of the current bounding-box to the size specific scores list
        self.computing_data.scores[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.scores[iou_thresh][bbox_size_type], prediction.score
        )

        return unmatched_gt_objects

    def __update_true_positive_metric_info(
        self,
        gt_evaluation_entry: Optional[EvaluationEntry],
        prediction_evaluation_entry: EvaluationEntry,
        prediction: GeometricClassification,
        class_identifier: ClassIdentifier,
    ) -> None:
        # The predicted annotation is an TP, therefore store it in a dict so that
        # it can be logged to tensorboard after the evaluation has finished

        # Build an EvaluationEntry based on the ground truth data and the given prediction
        tp_evaluation_entry = EvaluationEntry(
            image_path=prediction_evaluation_entry.image_path,
            evaluation_objects=[prediction],
        )

        if (
            prediction_evaluation_entry.image_path
            not in self.model_metrics.metrics_image_info_dict[str(class_identifier)]
        ):
            # There is no entry for the class-name + image-path combination yet,
            # create a new MetricImageInfo object

            self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                prediction_evaluation_entry.image_path
            ] = MetricImageInfo(
                gt_evaluation_entry=gt_evaluation_entry,
                tp_evaluation_entry=tp_evaluation_entry,
            )
        else:
            # Update MetricImageInfo entry that belongs
            # to the given class-name + image-path combination
            if (
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    prediction_evaluation_entry.image_path
                ].tp_evaluation_entry
                is not None
            ):
                # There is already a tp_evaluation_entry, update its predictions
                #
                # NOTE: the mypy error 'Item "None" of "Optional[EvaluationEntry]" has no
                #       attribute "evaluation_objects' can be ignored. It is checked by the
                #       above query operation. Somehow mypy does not get that.
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    prediction_evaluation_entry.image_path  # type: ignore[union-attr]
                ].tp_evaluation_entry.evaluation_objects.append(prediction)
            else:
                # There is now tp_evaluation_entry yet, set a new one for the MetricImageInfo object
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    prediction_evaluation_entry.image_path
                ].tp_evaluation_entry = tp_evaluation_entry

    def __update_false_positive_metric_info(
        self,
        gt_evaluation_entry: Optional[EvaluationEntry],
        prediction_evaluation_entry: EvaluationEntry,
        prediction: GeometricClassification,
        class_identifier: ClassIdentifier,
    ) -> None:
        # The predicted annotation is an FP, therefore store it in a dict so that
        # it can be logged to tensorboard after the evaluation has finished

        # Build an EvaluationEntry based on the ground truth data and the given prediction
        fp_evaluation_entry = EvaluationEntry(
            image_path=prediction_evaluation_entry.image_path,
            evaluation_objects=[prediction],
        )

        if (
            prediction_evaluation_entry.image_path
            not in self.model_metrics.metrics_image_info_dict[str(class_identifier)]
        ):
            # There is no entry for the class-name + image-path combination yet,
            # create a new MetricImageInfo object

            self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                prediction_evaluation_entry.image_path
            ] = MetricImageInfo(
                gt_evaluation_entry=gt_evaluation_entry,
                fp_evaluation_entry=fp_evaluation_entry,
            )
        else:
            # Update MetricImageInfo entry that belongs
            # to the given class-name + image-path combination
            if (
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    prediction_evaluation_entry.image_path
                ].fp_evaluation_entry
                is not None
            ):
                # There is already a fp_evaluation_entry, update its predictions
                #
                # NOTE: the mypy error 'Item "None" of "Optional[BaseAnnotation]" has no
                #       attribute "evaluation_objects' can be ignored. It is checked by the
                #       above query operation. Somehow mypy does not get that.
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    prediction_evaluation_entry.image_path  # type: ignore[union-attr]
                ].fp_evaluation_entry.evaluation_objects.append(prediction)
            else:
                # There is now fp_evaluation_entry yet, set a new one for the MetricImageInfo object
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    prediction_evaluation_entry.image_path
                ].fp_evaluation_entry = fp_evaluation_entry

    def __update_false_negative_metric_info(
        self,
        gt_evaluation_entry: EvaluationEntry,
        iou_unmatched_gt_objects: List[GeometricClassification],
        class_identifier: ClassIdentifier,
    ) -> None:
        """
        Update the fn_evaluation_entry entry of model_metrics.metrics_image_info_dict
        for the given class_name and the image path of the given ground truth annotation.

        Args:
            gt_evaluation_entry:
            iou_unmatched_gt_objects:
            class_identifier:

        Returns:
            None
        """

        fn_evaluation_entry = EvaluationEntry(
            image_path=gt_evaluation_entry.image_path,
            evaluation_objects=iou_unmatched_gt_objects,
        )

        if (
            gt_evaluation_entry.image_path
            not in self.model_metrics.metrics_image_info_dict[str(class_identifier)]
        ):
            self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                gt_evaluation_entry.image_path
            ] = MetricImageInfo(
                gt_evaluation_entry=gt_evaluation_entry,
                fn_evaluation_entry=fn_evaluation_entry,
            )
        else:
            self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                gt_evaluation_entry.image_path
            ].fn_evaluation_entry = fn_evaluation_entry

    def __get_gt_annotation(
        self, dataset_index: int, class_identifier: ClassIdentifier
    ) -> Tuple[Optional[EvaluationEntry], List[GeometricClassification]]:
        # annotation object for gathering all ground truth bounding boxes for this image
        new_evaluation_entry: Optional[EvaluationEntry] = None

        unmatched_gt_objects: List[GeometricClassification] = []

        if not str(class_identifier) in self._all_gt_dict[dataset_index]:
            return new_evaluation_entry, unmatched_gt_objects

        # Iterate over all ground-truth annotations that containing bounding-box
        # information for this image (dataset_index) and the given class-id
        for evaluation_entry in self._all_gt_dict[dataset_index][str(class_identifier)]:
            unmatched_gt_objects.extend(evaluation_entry.evaluation_objects)

            for prediction in evaluation_entry.evaluation_objects:
                # Increase ground-truth counter for overall count
                # and the specific prediction size count

                self.computing_data.gt_counter_dict[GeometricSizeTypes.BBOX_ALL][
                    str(class_identifier)
                ] += 1

                self.computing_data.gt_counter_dict[get_bbox_size_type(prediction.ortho_box())][
                    str(class_identifier)
                ] += 1

            # Initialize/update an overall ground_truth annotation that contains all
            # data for this image and class-id
            if new_evaluation_entry is None:
                new_evaluation_entry = copy.deepcopy(evaluation_entry)
            else:
                new_evaluation_entry.evaluation_objects.extend(evaluation_entry.evaluation_objects)

        return new_evaluation_entry, unmatched_gt_objects

    def __fill_computing_data(
        self,
        class_identifier: ClassIdentifier,
    ) -> None:
        process_bar = tqdm(
            range(self.dataset_length),
            desc=f"Compute metrics for class-identifier: {class_identifier}",
        )

        # Iterate over all image indices
        for dataset_index in process_bar:
            (
                gt_evaluation_entry,
                unmatched_gt_objects,
            ) = self.__get_gt_annotation(
                dataset_index=dataset_index, class_identifier=class_identifier
            )

            for iou_thresh in self.iou_thresholds:
                # Iterate over all predicted annotations for this image and class-id
                iou_unmatched_gt_objects = copy.deepcopy(unmatched_gt_objects)

                if str(class_identifier) in self._all_predictions_dict[dataset_index]:
                    for predicted_evaluation_entry in self._all_predictions_dict[dataset_index][
                        str(class_identifier)
                    ]:
                        for prediction in predicted_evaluation_entry.evaluation_objects:
                            iou_unmatched_gt_objects = self.__update_computation_dictionaries(
                                prediction=prediction,
                                iou_thresh=iou_thresh,
                                unmatched_gt_objects=iou_unmatched_gt_objects,
                            )

                            # The prediction is an FP if the last entry of the list from the
                            # false positives is equal to 1
                            if (
                                self.computing_data.false_positives_dict[iou_thresh][
                                    GeometricSizeTypes.BBOX_ALL
                                ][-1]
                                == 1
                            ):

                                self.__update_false_positive_metric_info(
                                    gt_evaluation_entry=gt_evaluation_entry,
                                    prediction_evaluation_entry=predicted_evaluation_entry,
                                    prediction=prediction,
                                    class_identifier=class_identifier,
                                )
                            else:
                                self.__update_true_positive_metric_info(
                                    gt_evaluation_entry=gt_evaluation_entry,
                                    prediction_evaluation_entry=predicted_evaluation_entry,
                                    prediction=prediction,
                                    class_identifier=class_identifier,
                                )

                # Check if there are ground truth annotations which haven't been matched,
                # this states that the box is a false negative
                if (
                    str(class_identifier) in self._all_gt_dict[dataset_index]
                    and len(self._all_gt_dict[dataset_index][str(class_identifier)]) > 0
                    and len(iou_unmatched_gt_objects) > 0
                    and gt_evaluation_entry is not None
                ):
                    self.__update_false_negative_metric_info(
                        gt_evaluation_entry=gt_evaluation_entry,
                        iou_unmatched_gt_objects=iou_unmatched_gt_objects,
                        class_identifier=class_identifier,
                    )

    def __compute_and_update_metrics_step(
        self,
        class_identifier: ClassIdentifier,
        iou_thresh: float,
        bbox_size_type: str,
        num_annotations: int,
        true_positives: np.ndarray,  # type: ignore[type-arg]
        false_positives: np.ndarray,  # type: ignore[type-arg]
    ) -> None:
        # compute recall and precision
        recall_values = true_positives / num_annotations
        precision_values = true_positives / np.maximum(
            true_positives + false_positives, np.finfo(np.float64).eps
        )

        # compute average precision
        # NOTE: mypy error 'Call to untyped function "close" in typed context' can be ignored
        ap = voc_ap(rec=recall_values, prec=precision_values, use_07_metric=False)  # type: ignore

        # IoUs only count if it is a true positive and therefore
        # has to be bigger or equal than the IoU threshold
        tp_iou_values = [
            iou_value
            for iou_value in self.computing_data.iou_dict[bbox_size_type]
            if iou_value > iou_thresh
        ]

        if len(tp_iou_values) > 0:
            avg_tp_iou = sum(tp_iou_values) / len(tp_iou_values)
        else:
            avg_tp_iou = 0.0

        if len(true_positives) > 0:
            tp = int(true_positives[-1])

            if tp > num_annotations:
                print("TP not valid")

            rc = tp / num_annotations
        else:
            tp = DEFAULT_INT_VALUE
            rc = DEFAULT_FLOAT_VALUE

        if len(false_positives) > 0:
            fp = int(false_positives[-1])
        else:
            fp = DEFAULT_INT_VALUE

        try:
            pr = tp / (fp + tp)
        except ZeroDivisionError:
            pr = DEFAULT_FLOAT_VALUE

        try:
            f1 = 2 * (pr * rc) / (pr + rc)
        except ZeroDivisionError:
            f1 = DEFAULT_FLOAT_VALUE

        fn = num_annotations - tp

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][str(class_identifier)] = (
            GeometricMetrics(
                TP=tp,
                FP=fp,
                FN=fn,
                PR=pr,
                RC=rc,
                F1=f1,
                AP=ap,
                COUNT=num_annotations,
                AVG_TP_IOU=avg_tp_iou,
            )
        )

    def __compute_metrics(self, class_identifier: ClassIdentifier) -> None:
        for iou_thresh in self.iou_thresholds:
            for bbox_size_type in GeometricSizeTypes.get_values_as_list(
                class_type=GeometricSizeTypes
            ):
                num_annotations = self.computing_data.gt_counter_dict[bbox_size_type][
                    str(class_identifier)
                ]

                if num_annotations == 0.0:
                    continue

                # sort by score
                indices = np.argsort(-self.computing_data.scores[iou_thresh][bbox_size_type])

                false_positives = self.computing_data.false_positives_dict[iou_thresh][
                    bbox_size_type
                ][indices]

                true_positives = self.computing_data.true_positives_dict[iou_thresh][
                    bbox_size_type
                ][indices]

                # compute false positives and true positives
                false_positives = np.cumsum(false_positives)
                true_positives = np.cumsum(true_positives)

                self.__compute_and_update_metrics_step(
                    class_identifier=class_identifier,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                    num_annotations=num_annotations,
                    true_positives=true_positives,
                    false_positives=false_positives,
                )

    @staticmethod
    def match_false_negatives_and_false_positives_as_dict(
        metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
        iou_threshold: float,
    ) -> Tuple[METRIC_IMAGE_INFO_TYPE, CONFUSION_MATRIX_DICT_TYPE]:
        """
        Build a dictionary containing the confusion matrix that is based on the given
        metrics by the metrics_image_info_dict.

        Args:
            metrics_image_info_dict: The dictionary containing the information of the metrics
            iou_threshold: The iou threshold for which to compute the confusion matrix

        Returns:
            A tuple containing:
            - The reverse metrics_image_info_dict where the keys class_identifier_str and image-path have been swapped
            - The confusion matrix
        """

        confusion_matrix: CONFUSION_MATRIX_DICT_TYPE = {
            k2: {k1: 0 for k1 in metrics_image_info_dict.keys()}
            for k2 in metrics_image_info_dict.keys()
        }

        # Build a dict for reverse look up (reverse of metrics_image_info_dict),
        # where the keys are image paths. This is needed to fill the confusion matrix per image.
        # 1st key: Image Path
        # 2nd key: Class Identifier as string
        # value: The MetricImageInfo for this image path and class name
        image_metrics_info_dict: Dict[str, Dict[str, MetricImageInfo]] = {}
        for class_identifier_str in metrics_image_info_dict.keys():
            for image_path, metric_image_info in metrics_image_info_dict[
                class_identifier_str
            ].items():
                if image_path not in image_metrics_info_dict:
                    image_metrics_info_dict[image_path] = {}

                if class_identifier_str not in image_metrics_info_dict[image_path]:
                    image_metrics_info_dict[image_path][class_identifier_str] = metric_image_info

        result_metrics_image_info_dict = copy.deepcopy(metrics_image_info_dict)

        for image_path in image_metrics_info_dict.keys():
            class_identifiers: List[ClassIdentifier] = [
                ClassIdentifier.from_str(class_identifier_str=c)
                for c in image_metrics_info_dict[image_path].keys()
            ]

            for class_identifier in class_identifiers:
                other_class_identifiers: List[ClassIdentifier] = copy.deepcopy(class_identifiers)
                other_class_identifiers.remove(class_identifier)

                class_img_metrics_info = image_metrics_info_dict[image_path][str(class_identifier)]
                if class_img_metrics_info.fn_evaluation_entry:
                    class_fn_predictions = (
                        class_img_metrics_info.fn_evaluation_entry.evaluation_objects
                    )

                    for fn_prediction in class_fn_predictions:
                        for other_class_identifier in other_class_identifiers:
                            other_class_img_metrics_info = image_metrics_info_dict[image_path][
                                str(other_class_identifier)
                            ]

                            if other_class_img_metrics_info.fp_evaluation_entry:
                                other_class_fp_predictions = (
                                    other_class_img_metrics_info.fp_evaluation_entry.evaluation_objects
                                )

                                (
                                    max_overlap,
                                    assigned_fp_prediction,
                                ) = compute_max_prediction(
                                    prediction=fn_prediction,
                                    gt_predictions=other_class_fp_predictions,
                                )

                                if max_overlap > iou_threshold:
                                    confusion_matrix[str(class_identifier)][
                                        str(other_class_identifier)
                                    ] += 1
                                    class_img_metrics_info.fn_evaluation_entry.evaluation_objects.remove(
                                        fn_prediction
                                    )
                                    other_class_img_metrics_info.fp_evaluation_entry.evaluation_objects.remove(
                                        assigned_fp_prediction
                                    )

                                    result_metrics_image_info_dict = MetricsComputation.__change_matched_bbox_attribute(
                                        metrics_image_info_dict=result_metrics_image_info_dict,
                                        image_path=class_img_metrics_info.fn_evaluation_entry.image_path,
                                        class_identifier=class_identifier,
                                        other_class_identifier=other_class_identifier,
                                        fn_prediction=fn_prediction,
                                        assigned_fp_prediction=assigned_fp_prediction,
                                        class_img_metrics_info=class_img_metrics_info,
                                        other_class_img_metrics_info=other_class_img_metrics_info,
                                    )

                            if other_class_img_metrics_info.fp_evaluation_entry:
                                if (
                                    len(
                                        other_class_img_metrics_info.fp_evaluation_entry.evaluation_objects
                                    )
                                    == 0
                                ):
                                    other_class_img_metrics_info.fp_evaluation_entry = None

                if class_img_metrics_info.fn_evaluation_entry:
                    if len(class_img_metrics_info.fn_evaluation_entry.evaluation_objects) == 0:
                        class_img_metrics_info.fn_evaluation_entry = None

        return result_metrics_image_info_dict, confusion_matrix

    @staticmethod
    def __change_matched_bbox_attribute(
        metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
        image_path: str,
        class_identifier: ClassIdentifier,
        other_class_identifier: ClassIdentifier,
        fn_prediction: GeometricClassification,
        assigned_fp_prediction: GeometricClassification,
        class_img_metrics_info: MetricImageInfo,
        other_class_img_metrics_info: MetricImageInfo,
    ) -> METRIC_IMAGE_INFO_TYPE:
        if class_img_metrics_info.fn_matched_fp_evaluation_entry is not None:
            class_img_metrics_info.fn_matched_fp_evaluation_entry.evaluation_objects.append(
                fn_prediction
            )
        else:
            class_img_metrics_info.fn_matched_fp_evaluation_entry = EvaluationEntry(
                image_path=image_path,
                evaluation_objects=[fn_prediction],
            )

        if other_class_img_metrics_info.fn_matched_fp_evaluation_entry is not None:
            other_class_img_metrics_info.fn_matched_fp_evaluation_entry.evaluation_objects.append(
                assigned_fp_prediction
            )

        else:
            other_class_img_metrics_info.fn_matched_fp_evaluation_entry = EvaluationEntry(
                image_path=image_path,
                evaluation_objects=[assigned_fp_prediction],
            )

        metrics_image_info_dict[str(class_identifier)][image_path] = class_img_metrics_info
        metrics_image_info_dict[str(other_class_identifier)][
            image_path
        ] = other_class_img_metrics_info

        return metrics_image_info_dict
