from application.managers.model.definitions.classification.DecisionTree import DECISION_TREE_REGISTRY_INSTANCE
from application.managers.model.definitions.classification.KNN import KNN_REGISTRY_INSTANCE
from application.managers.model.definitions.classification.SVM import SVM_REGISTRY_INSTANCE

CLASSIFICATION_REGISTRY = {
  "Support Vector Machines (SVM)": SVM_REGISTRY_INSTANCE,
  "KNN": KNN_REGISTRY_INSTANCE,
  "Decision Tree": DECISION_TREE_REGISTRY_INSTANCE
}

__all__ = [
  'CLASSIFICATION_REGISTRY'
]
