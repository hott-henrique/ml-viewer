from application.managers.model.definitions.regression.LinearRegression import LINEAR_REGRESSION_REGISTRY_INSTANCE
from application.managers.model.definitions.regression.DecisionTree import DECISION_TREE_REGRESSOR_REGISTRY_INSTANCE

REGRETION_REGISTRY = {
  "Linear Regression": LINEAR_REGRESSION_REGISTRY_INSTANCE,
  "Decision Tree Regressor": DECISION_TREE_REGRESSOR_REGISTRY_INSTANCE,
}

__all__ = [
  "REGRETION_REGISTRY",
]
