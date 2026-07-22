import importlib

from typing import Protocol, Any

from loader.definitions import *

class ModelAPI(Protocol):
  def fit(self, X: Any, y: Any, **fit_params: Any) -> 'ModelAPI':
    ...

  def predict(self, X: Any) -> Any:
    ...

class AlgorithmRegistry:
  BASE_ALGORITHM_REGISTRY: dict[str, dict] = {
    "Classification": CLASSIFICATION_REGISTRY,
    "Regression": REGRETION_REGISTRY
  }

  @staticmethod
  def registry(problem_type: str) -> dict[str, dict]:
    return AlgorithmRegistry.BASE_ALGORITHM_REGISTRY.get(problem_type)

  @staticmethod
  def options(problem_type: str) -> list[str]:
    return list(AlgorithmRegistry.registry(problem_type).keys())

  @staticmethod
  def instantiate(problem_type: str, name: str, params: dict) -> ModelAPI:
    registry = AlgorithmRegistry.registry(problem_type)

    if name not in registry:
      raise ValueError('Algorithm not found in registry.', name)

    config: dict = registry.get(name)

    module_path = config["module"]
    class_name = config["class"]

    module = importlib.import_module(module_path)

    model_class = getattr(module, class_name)

    return model_class(**params)
