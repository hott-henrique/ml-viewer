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
    },
    "Logistic Regression": {
        "module": "sklearn.linear_model",
        "class": "LogisticRegression",
        "params": [
          {"name": "C", "type": "float", "default": 1.0, "label": "Inverse Regularization (C)"},
          {"name": "max_iter", "type": "int", "default": 100, "label": "Max Iterations"}
        ]
    },
    "Decision Tree": {
      "module": "sklearn.tree",
      "class": "DecisionTreeClassifier",
      "params": [
        {
          "name": "criterion",
          "type": "categorical",
          "options": ["gini", "entropy", "log_loss"],
          "default": "gini",
          "label": "Criterion"
        },
        {
          "name": "splitter",
          "type": "categorical",
          "options": ["best", "random"],
          "default": "best",
          "label": "Splitter"
        },
        {
          "name": "max_depth",
          "type": "int",
          "default": "",
          "label": "Max Depth"
        },
        {
          "name": "min_samples_split",
          "type": "float",
          "default": 1.9,
          "label": "Min Samples Split"
        },
        {
          "name": "min_samples_leaf",
          "type": "float",
          "default": 0.9,
          "label": "Min Samples Leaf"
        },
        {
          "name": "min_weight_fraction_leaf",
          "type": "float",
          "default": 0.0,
          "label": "Min Weight Fraction Leaf"
        },
        {
          "name": "max_features",
          "type": "categorical",
          "options": ["None", "sqrt", "log2"],
          "default": "None",
          "label": "Max Features"
        },
        {
          "name": "random_state",
          "type": "int",
          "default": 42,
          "label": "Random State"
        },
        {
          "name": "max_leaf_nodes",
          "type": "int",
          "default": "",
          "label": "Max Leaf Nodes"
        },
        {
          "name": "min_impurity_decrease",
          "type": "float",
          "default": 0.0,
          "label": "Min Impurity Decrease"
        },
        {
          "name": "class_weight",
          "type": "categorical",
          "options": ["None", "balanced"],
          "default": "None",
          "label": "Class Weight"
        },
        {
          "name": "ccp_alpha",
          "type": "float",
          "default": 0.0,
          "label": "CCP Alpha"
        }
      ]
    }
      # criterion: Literal['gini', 'entropy', 'log_loss'] = "gini",
      # splitter: Literal['best', 'random'] = "best",
      # max_depth: Int | None = None,
      # min_samples_split: float = 2,
      # min_samples_leaf: float = 1,
      # min_weight_fraction_leaf: Float = 0,
      # max_features: float | Literal['auto', 'sqrt', 'log2'] | None = None,
    # random_state: Int | RandomState | None = None,
    # max_leaf_nodes: Int | None = None,
    # min_impurity_decrease: Float = 0,
    # class_weight: Mapping | str | Sequence[Mapping] | None = None,
    # ccp_alpha: float = 0
  }
  import sklearn.tree
  sklearn.tree.DecisionTreeClassifier()

  @staticmethod
  def registry() -> dict:
    return AlgorithmRegistry.BASE_ALGORITHM_REGISTRY

  @staticmethod
  def options() -> list[str]:
    return list(AlgorithmRegistry.registry().keys())

  @staticmethod
  def instantiate(name: str, params: dict) -> SklearnClassifierAPI:
    registry = AlgorithmRegistry.registry()

    if name not in registry:
      raise ValueError('Algorithm not found in registry.', name)

    config: dict = registry.get(name)

    module_path = config["module"]
    class_name = config["class"]

    module = importlib.import_module(module_path)

    model_class = getattr(module, class_name)

    return model_class(**params)
