"""Stable extension surface for ml-viewer plugins.

Plugin authors should import contracts from this package only::

    from application.api import AgentAPI, EnvironmentAPI, StepResult
    from application.api import SupervisedAnalyzer, ScalarResult, HyperParamConfig

Declare one of:

- ``MODEL_CONFIG`` — models / RL agents (implement the matching Protocol)
- ``ENV_CONFIG`` — environments (implement ``EnvironmentAPI``; ``step`` returns ``StepResult``)
- ``ANALYSIS_CONFIG`` — analyses (subclass an analyzer ABC; return an ``ExportResult``)

RL agents do not own the training loop; the app's ``TrainingRunner`` calls
``select_action`` / ``update``. Compatible environments for an agent are chosen
in the Models UI (not in ``ENV_CONFIG``).
"""

from __future__ import annotations

from application.api.analysis import (
  AssociationRulesAnalyzer,
  ClusteringAnalyzer,
  DimensionalityReductionAnalyzer,
  ExportResult,
  ImageResult,
  ReinforcementLearningAnalyzer,
  ResultAnalyzer,
  ScalarResult,
  StoredImageResult,
  SupervisedAnalyzer,
  TextResult,
  fallback_result_label,
  write_metrics_json,
)
from application.api.environment import EnvironmentAPI
from application.api.models import (
  AgentAPI,
  AssociationRulesModelAPI,
  ClusteringModelAPI,
  DimensionalityReductionModelAPI,
  ModelAPI,
  SemiSupervisedModelAPI,
  SupervisedModelAPI,
)
from application.api.params import HyperParamConfig, ParamType
from application.api.types import StepResult, Transition

__all__ = [
  # Types
  "StepResult",
  "Transition",
  # Environment
  "EnvironmentAPI",
  # Models / agents
  "SupervisedModelAPI",
  "ClusteringModelAPI",
  "DimensionalityReductionModelAPI",
  "AssociationRulesModelAPI",
  "SemiSupervisedModelAPI",
  "AgentAPI",
  "ModelAPI",
  # Params
  "ParamType",
  "HyperParamConfig",
  # Analysis
  "ExportResult",
  "TextResult",
  "ScalarResult",
  "ImageResult",
  "StoredImageResult",
  "ResultAnalyzer",
  "SupervisedAnalyzer",
  "ClusteringAnalyzer",
  "DimensionalityReductionAnalyzer",
  "AssociationRulesAnalyzer",
  "ReinforcementLearningAnalyzer",
  "fallback_result_label",
  "write_metrics_json",
]
