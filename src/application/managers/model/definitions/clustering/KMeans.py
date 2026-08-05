KMEANS_REGISTRY_INSTANCE = {
  "module": "sklearn.cluster",
  "class": "KMeans",
  "title": {"en_US": "K-Means", "pt_BR": "K-Means"},
  "description": {
    "en_US": "Partitions samples into k clusters by minimizing within-cluster variance (Lloyd's algorithm).",
    "pt_BR": "Particiona amostras em k clusters minimizando a variância intra-cluster (algoritmo de Lloyd).",
  },
  "params": [
    {
      "name": "n_clusters",
      "type": "int",
      "default": 3,
      "label": {"en_US": "N Clusters", "pt_BR": "N clusters"},
      "description": {
        "en_US": "Number of clusters to form and centroids to generate.",
        "pt_BR": "Número de clusters a formar e de centróides a gerar.",
      },
    },
    {
      "name": "init",
      "type": "categorical",
      "options": ["k-means++", "random"],
      "default": "k-means++",
      "label": {"en_US": "Init", "pt_BR": "Inicialização"},
      "description": {
        "en_US": "Method for centroid initialization.",
        "pt_BR": "Método de inicialização dos centróides.",
      },
    },
    {
      "name": "n_init",
      "type": "int",
      "default": 10,
      "label": {"en_US": "N Init", "pt_BR": "N inicializações"},
      "description": {
        "en_US": "Number of times the algorithm is run with different centroid seeds.",
        "pt_BR": "Número de vezes que o algoritmo é executado com sementes diferentes.",
      },
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": 300,
      "label": {"en_US": "Max Iter", "pt_BR": "Máx. iterações"},
      "description": {
        "en_US": "Maximum number of iterations for a single run.",
        "pt_BR": "Número máximo de iterações em uma execução.",
      },
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": {"en_US": "Random State", "pt_BR": "Estado aleatório"},
      "description": {
        "en_US": "Controls reproducibility of centroid initialization.",
        "pt_BR": "Controla a reprodutibilidade da inicialização dos centróides.",
      },
    },
  ],
}
