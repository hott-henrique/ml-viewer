PCA_REGISTRY_INSTANCE = {
  "module": "sklearn.decomposition",
  "class": "PCA",
  "title": {"en_US": "PCA", "pt_BR": "PCA"},
  "description": {
    "en_US": "Linear dimensionality reduction using Singular Value Decomposition to project data to a lower-dimensional space.",
    "pt_BR": "Redução linear de dimensionalidade via decomposição em valores singulares.",
  },
  "params": [
    {
      "name": "n_components",
      "type": "int",
      "default": 2,
      "label": {"en_US": "N Components", "pt_BR": "N componentes"},
      "description": {
        "en_US": "Number of components to keep.",
        "pt_BR": "Número de componentes a manter.",
      },
    },
    {
      "name": "svd_solver",
      "type": "categorical",
      "options": ["auto", "full", "arpack", "randomized"],
      "default": "auto",
      "label": {"en_US": "SVD Solver", "pt_BR": "Solver SVD"},
      "description": {
        "en_US": "Solver used to compute the singular value decomposition.",
        "pt_BR": "Solver usado para calcular a decomposição em valores singulares.",
      },
    },
    {
      "name": "whiten",
      "type": "bool",
      "default": False,
      "label": {"en_US": "Whiten", "pt_BR": "Whitening"},
      "description": {
        "en_US": "When True, components are whitened so they have unit variance.",
        "pt_BR": "Quando True, os componentes são normalizados para variância unitária.",
      },
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": {"en_US": "Random State", "pt_BR": "Estado aleatório"},
      "description": {
        "en_US": "Used when the solver is randomized.",
        "pt_BR": "Usado quando o solver é aleatório.",
      },
    },
  ],
}
