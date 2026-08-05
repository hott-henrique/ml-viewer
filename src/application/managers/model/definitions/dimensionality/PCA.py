PCA_REGISTRY_INSTANCE = {
  "module": "sklearn.decomposition",
  "class": "PCA",
  "description": "Linear dimensionality reduction using Singular Value Decomposition to project data to a lower-dimensional space.",
  "params": [
    {
      "name": "n_components",
      "type": "int",
      "default": 2,
      "label": "N Components",
      "description": "Number of components to keep.",
    },
    {
      "name": "svd_solver",
      "type": "categorical",
      "options": ["auto", "full", "arpack", "randomized"],
      "default": "auto",
      "label": "SVD Solver",
      "description": "Solver used to compute the singular value decomposition.",
    },
    {
      "name": "whiten",
      "type": "bool",
      "default": False,
      "label": "Whiten",
      "description": "When True, components are whitened so they have unit variance.",
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State",
      "description": "Used when the solver is randomized.",
    },
  ],
}
