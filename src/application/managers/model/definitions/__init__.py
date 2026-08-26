from application.managers.model.definitions.classification import CLASSIFICATION_REGISTRY
from application.managers.model.definitions.regression import REGRETION_REGISTRY
from application.managers.model.definitions.clustering import CLUSTERING_REGISTRY
from application.managers.model.definitions.dimensionality import DIMENSIONALITY_REGISTRY
from application.managers.model.definitions.association import ASSOCIATION_REGISTRY
from application.managers.model.definitions.rl import RL_REGISTRY


__all__ = [
  "CLASSIFICATION_REGISTRY",
  "REGRETION_REGISTRY",
  "CLUSTERING_REGISTRY",
  "DIMENSIONALITY_REGISTRY",
  "ASSOCIATION_REGISTRY",
  "RL_REGISTRY",
]
