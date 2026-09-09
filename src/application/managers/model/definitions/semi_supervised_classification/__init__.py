from application.managers.model.definitions.semi_supervised_classification.LabelSpreading import (
  LABEL_SPREADING_REGISTRY_INSTANCE,
)
from application.managers.model.definitions.semi_supervised_classification.SelfTrainingSVC import (
  SELF_TRAINING_SVC_REGISTRY_INSTANCE,
)

SEMI_SUPERVISED_CLASSIFICATION_REGISTRY = {
  "Label Spreading": LABEL_SPREADING_REGISTRY_INSTANCE,
  "Self-Training (SVC)": SELF_TRAINING_SVC_REGISTRY_INSTANCE,
}

__all__ = [
  "SEMI_SUPERVISED_CLASSIFICATION_REGISTRY",
]
