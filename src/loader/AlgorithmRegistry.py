import importlib

from typing import Protocol, Any

from loader.definitions.classification import *

class ModelAPI(Protocol):
  def fit(self, X: Any, y: Any, **fit_params: Any) -> 'ModelAPI':
    ...

  def predict(self, X: Any) -> Any:
    ...

class AlgorithmRegistry:
  BASE_ALGORITHM_REGISTRY = {
    "Support Vector Machines (SVM)": SVM_REGISTRY_INSTANCE,
    "KNN": KNN_REGISTRY_INSTANCE,
    "Decision Tree": DECISION_TREE_REGISTRY_INSTANCE
  }

  @staticmethod
  def registry() -> dict:
    return AlgorithmRegistry.BASE_ALGORITHM_REGISTRY

  @staticmethod
  def options() -> list[str]:
    return list(AlgorithmRegistry.registry().keys())

  @staticmethod
  def instantiate(name: str, params: dict) -> ModelAPI:
    registry = AlgorithmRegistry.registry()

    if name not in registry:
      raise ValueError('Algorithm not found in registry.', name)

    config: dict = registry.get(name)

    module_path = config["module"]
    class_name = config["class"]

    module = importlib.import_module(module_path)

    model_class = getattr(module, class_name)

    return model_class(**params)
