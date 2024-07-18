# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for evaluating currently trained model checkpoints"""

import logging
from typing import List, Union

from tqdm import tqdm

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.geometric_classifiction import GeometricClassification
from mlcvzoo_base.api.model import (
    ConfigurationType,
    DataType,
    ObjectDetectionModel,
    SegmentationModel,
)
from mlcvzoo_base.evaluation.geometric.data_classes import GeometricEvaluationMetrics
from mlcvzoo_base.evaluation.geometric.metrics_computation import (
    EvaluationContexts,
    MetricsComputation,
)

logger = logging.getLogger(__name__)


def evaluate_with_model(
    gt_annotations: List[BaseAnnotation],
    iou_thresholds: List[float],
    model: Union[
        ObjectDetectionModel[ConfigurationType, DataType],
        SegmentationModel[ConfigurationType, DataType],
    ],
    evaluation_context: str = EvaluationContexts.ALL.value,
) -> GeometricEvaluationMetrics:
    """Compute the metric for the given object detection model. The evaluation is performed
    on the basis of the given ground truth annotations.

    Args:
        model: The model that should be evaluated
        gt_annotations: ground truth annotations where the model should be evaluated on
        iou_thresholds: List of thresholds for which a metrics should be computed
        evaluation_context: Context of the evaluation

    Returns:
        The computed object detection metrics for this model
    """

    predictions_list: List[List[GeometricClassification]] = []

    process_bar = tqdm(
        gt_annotations,
        desc=f"Run prediction",
    )

    for index, gt_annotation in enumerate(process_bar):
        # Every ObjectDetectionModel and SegmentationModel returns GeometricClassifications
        _, predictions = model.predict(data_item=gt_annotation.image_path)
        predictions_list.append(predictions)  # type: ignore[arg-type]

    return MetricsComputation(
        model_specifier=model.unique_name,
        iou_thresholds=iou_thresholds,
        gt_annotations=gt_annotations,
        predictions_list=predictions_list,
        mapper=model.mapper,
        evaluation_context=evaluation_context,
    ).compute_metrics()


def evaluate_with_precomputed_data(
    model_specifier: str,
    gt_annotations: List[BaseAnnotation],
    iou_thresholds: List[float],
    predictions_list: List[List[GeometricClassification]],
    mapper: AnnotationClassMapper,
    evaluation_context: str = EvaluationContexts.ALL,
) -> GeometricEvaluationMetrics:
    """
    Compute the object detection metrics taking precomputed (predicted) bounding boxes and
    ground truth annotations.

    IMPORTANT REMARK: The index of the lists 'ground_truth_annotations'
                      and 'predictions_list' have to match exactly. This means
                      index 0 indicates the ground truth data and predicted bounding boxes
                      for image 0.

    Args:
        model_specifier: A string to indicate with which model the precomputed bounding boxes
                         have been predicted
        gt_annotations: The ground truth data as basis for the evaluation
        iou_thresholds: List of thresholds for which a metrics should be computed
        predictions_list: A list containing the predicted GeometricClassifications for each
                          image of ground truth data
       mapper: An AnnotationClassMapper object that states the mapping of Class-IDs/Class-Names
               to ClassIdentifier(s)
       evaluation_context: Context of the evaluation

    Returns:
        The computed object detection metrics
    """

    return MetricsComputation(
        model_specifier=model_specifier,
        iou_thresholds=iou_thresholds,
        gt_annotations=gt_annotations,
        predictions_list=predictions_list,
        mapper=mapper,
        evaluation_context=evaluation_context,
    ).compute_metrics()
