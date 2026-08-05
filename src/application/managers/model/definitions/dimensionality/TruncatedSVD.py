TRUNCATED_SVD_REGISTRY_INSTANCE = {
  "module": "sklearn.decomposition",
  "class": "TruncatedSVD",
  "title": {"en_US": "Truncated SVD", "pt_BR": "SVD Truncado"},
  "description": {
    "en_US": "Dimensionality reduction via truncated singular value decomposition (works well on sparse count data).",
    "pt_BR": "Redução de dimensionalidade via decomposição em valores singulares truncada.",
  },
  "params": [
    {
      "name": "n_components",
      "type": "int",
      "default": 2,
      "label": {"en_US": "N Components", "pt_BR": "N componentes"},
      "description": {
        "en_US": "Desired dimensionality of the output data.",
        "pt_BR": "Dimensionalidade desejada dos dados de saída.",
      },
    },
    {
      "name": "algorithm",
      "type": "categorical",
      "options": ["randomized", "arpack"],
      "default": "randomized",
      "label": {"en_US": "Algorithm", "pt_BR": "Algoritmo"},
      "description": {
        "en_US": "SVD solver to use.",
        "pt_BR": "Solver SVD a utilizar.",
      },
    },
    {
      "name": "n_iter",
      "type": "int",
      "default": 5,
      "label": {"en_US": "N Iter", "pt_BR": "N iterações"},
      "description": {
        "en_US": "Number of iterations for randomized SVD solver.",
        "pt_BR": "Número de iterações do solver SVD aleatório.",
      },
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": {"en_US": "Random State", "pt_BR": "Estado aleatório"},
      "description": {
        "en_US": "Controls reproducibility of randomized SVD.",
        "pt_BR": "Controla a reprodutibilidade do SVD aleatório.",
      },
    },
  ],
}
