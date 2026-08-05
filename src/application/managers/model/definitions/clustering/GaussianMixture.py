GAUSSIAN_MIXTURE_REGISTRY_INSTANCE = {
  "module": "sklearn.mixture",
  "class": "GaussianMixture",
  "description": "Probabilistic clustering that fits a mixture of Gaussian distributions and assigns soft/hard cluster labels.",
  "params": [
    {
      "name": "n_components",
      "type": "int",
      "default": 3,
      "label": "N Components",
      "description": "Number of mixture components (clusters).",
    },
    {
      "name": "covariance_type",
      "type": "categorical",
      "options": ["full", "tied", "diag", "spherical"],
      "default": "full",
      "label": "Covariance Type",
      "description": "Constraints on the covariance of each mixture component.",
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": 100,
      "label": "Max Iter",
      "description": "Maximum number of EM iterations.",
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State",
      "description": "Controls reproducibility of initialization.",
    },
  ],
}
