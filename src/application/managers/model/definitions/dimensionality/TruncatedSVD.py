TRUNCATED_SVD_REGISTRY_INSTANCE = {
  "module": "sklearn.decomposition",
  "class": "TruncatedSVD",
  "description": "Dimensionality reduction via truncated singular value decomposition (works well on sparse count data).",
  "params": [
    {
      "name": "n_components",
      "type": "int",
      "default": 2,
      "label": "N Components",
      "description": "Desired dimensionality of the output data.",
    },
    {
      "name": "algorithm",
      "type": "categorical",
      "options": ["randomized", "arpack"],
      "default": "randomized",
      "label": "Algorithm",
      "description": "SVD solver to use.",
    },
    {
      "name": "n_iter",
      "type": "int",
      "default": 5,
      "label": "N Iter",
      "description": "Number of iterations for randomized SVD solver.",
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State",
      "description": "Controls reproducibility of randomized SVD.",
    },
  ],
}
