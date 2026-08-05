GAUSSIAN_MIXTURE_REGISTRY_INSTANCE = {
  "module": "sklearn.mixture",
  "class": "GaussianMixture",
  "title": {"en_US": "Gaussian Mixture", "pt_BR": "Mistura Gaussiana"},
  "description": {
    "en_US": "Probabilistic clustering that fits a mixture of Gaussian distributions and assigns soft/hard cluster labels.",
    "pt_BR": "Agrupamento probabilístico que ajusta uma mistura de distribuições Gaussianas.",
  },
  "params": [
    {
      "name": "n_components",
      "type": "int",
      "default": 3,
      "label": {"en_US": "N Components", "pt_BR": "N componentes"},
      "description": {
        "en_US": "Number of mixture components (clusters).",
        "pt_BR": "Número de componentes (clusters) da mistura.",
      },
    },
    {
      "name": "covariance_type",
      "type": "categorical",
      "options": ["full", "tied", "diag", "spherical"],
      "default": "full",
      "label": {"en_US": "Covariance Type", "pt_BR": "Tipo de covariância"},
      "description": {
        "en_US": "Constraints on the covariance of each mixture component.",
        "pt_BR": "Restrições sobre a covariância de cada componente.",
      },
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": 100,
      "label": {"en_US": "Max Iter", "pt_BR": "Máx. iterações"},
      "description": {
        "en_US": "Maximum number of EM iterations.",
        "pt_BR": "Número máximo de iterações do EM.",
      },
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": {"en_US": "Random State", "pt_BR": "Estado aleatório"},
      "description": {
        "en_US": "Controls reproducibility of initialization.",
        "pt_BR": "Controla a reprodutibilidade da inicialização.",
      },
    },
  ],
}
