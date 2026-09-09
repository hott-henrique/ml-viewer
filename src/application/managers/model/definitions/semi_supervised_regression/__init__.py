from application.managers.model.definitions.semi_supervised_regression.SelfTrainingRegressor import (
  SELF_TRAINING_REGRESSOR_REGISTRY_INSTANCE,
)
from application.managers.model.definitions.semi_supervised_regression.SelfTrainingDecisionTreeRegressor import (
  SELF_TRAINING_DECISION_TREE_REGRESSOR_REGISTRY_INSTANCE,
)

SEMI_SUPERVISED_REGRESSION_REGISTRY = {
  "Self-Training Regressor": SELF_TRAINING_REGRESSOR_REGISTRY_INSTANCE,
  "Self-Training (Decision Tree)": SELF_TRAINING_DECISION_TREE_REGRESSOR_REGISTRY_INSTANCE,
}

__all__ = [
  "SEMI_SUPERVISED_REGRESSION_REGISTRY",
]
