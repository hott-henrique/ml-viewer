import importlib

from typing import Protocol, Any

class SklearnClassifierAPI(Protocol):
    def fit(self, X: Any, y: Any, **fit_params: Any) -> 'SklearnClassifierAPI':
        ...
        
    def predict(self, X: Any) -> Any:
        ...

class AlgorithmRegistry:
  BASE_ALGORITHM_REGISTRY = {
    "Random Forest": {
        "module": "sklearn.ensemble",
        "class": "RandomForestClassifier",
        "params": [
          {"name": "n_estimators", "type": "int", "default": 100, "label": "Number of Trees"},
          {"name": "criterion", "type": "categorical", "options": ["gini", "entropy", "log_loss"], "default": "gini", "label": "Criterion"}
        ]
        # "kwargs": {"random_state": 42}
    },
    "Logistic Regression": {
        "module": "sklearn.linear_model",
        "class": "LogisticRegression",
        "params": [
          {"name": "C", "type": "float", "default": 1.0, "label": "Inverse Regularization (C)"},
          {"name": "max_iter", "type": "int", "default": 100, "label": "Max Iterations"}
        ]
        # "kwargs": {"random_state": 42, "max_iter": 1000}
    },
    # "Decision Tree": {
    #     "module": "sklearn.tree",
    #     "class": "DecisionTreeClassifier",
    #     "kwargs": {"random_state": 42}
    # },
    # "Support Vector Machine (SVM)": {
    #     "module": "sklearn.svm",
    #     "class": "SVC",
    #     "kwargs": {"random_state": 42}
    # },
  }

  @staticmethod
  def registry() -> dict:
    return AlgorithmRegistry.BASE_ALGORITHM_REGISTRY

  @staticmethod
  def options() -> list[str]:
    return list(AlgorithmRegistry.registry().keys())

  @staticmethod
  def instantiate(name: str) -> SklearnClassifierAPI:
    registry = AlgorithmRegistry.registry()

    if name not in registry:
      raise ValueError('Algorithm not found in registry.', name)

    config: dict = registry.get(name)

    module_path = config["module"]
    class_name = config["class"]
    kwargs = config.get("kwargs", {})

    module = importlib.import_module(module_path)

    model_class = getattr(module, class_name)

    return model_class(**kwargs)
