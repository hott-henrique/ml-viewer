from application.managers.model.definitions.dimensionality.PCA import PCA_REGISTRY_INSTANCE
from application.managers.model.definitions.dimensionality.TruncatedSVD import TRUNCATED_SVD_REGISTRY_INSTANCE

DIMENSIONALITY_REGISTRY = {
  "PCA": PCA_REGISTRY_INSTANCE,
  "Truncated SVD": TRUNCATED_SVD_REGISTRY_INSTANCE,
}

__all__ = [
  "DIMENSIONALITY_REGISTRY",
]
