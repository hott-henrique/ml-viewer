from application.managers.model.definitions.semi_supervised_regression.SelfTrainingRegressor import (
  SELF_TRAINING_REGRESSOR_REGISTRY_INSTANCE,
)

SEMI_SUPERVISED_REGRESSION_REGISTRY = {
  "Self-Training Regressor": SELF_TRAINING_REGRESSOR_REGISTRY_INSTANCE,
}

__all__ = [
  "SEMI_SUPERVISED_REGRESSION_REGISTRY",
]
