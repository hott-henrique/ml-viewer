from application.managers.model.definitions.clustering.KMeans import KMEANS_REGISTRY_INSTANCE
from application.managers.model.definitions.clustering.GaussianMixture import GAUSSIAN_MIXTURE_REGISTRY_INSTANCE

CLUSTERING_REGISTRY = {
  "K-Means": KMEANS_REGISTRY_INSTANCE,
  "Gaussian Mixture": GAUSSIAN_MIXTURE_REGISTRY_INSTANCE,
}

__all__ = [
  "CLUSTERING_REGISTRY",
]
