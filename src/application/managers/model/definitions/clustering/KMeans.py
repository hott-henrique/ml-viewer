KMEANS_REGISTRY_INSTANCE = {
  "module": "sklearn.cluster",
  "class": "KMeans",
  "description": "Partitions samples into k clusters by minimizing within-cluster variance (Lloyd's algorithm).",
  "params": [
    {
      "name": "n_clusters",
      "type": "int",
      "default": 3,
      "label": "N Clusters",
      "description": "Number of clusters to form and centroids to generate.",
    },
    {
      "name": "init",
      "type": "categorical",
      "options": ["k-means++", "random"],
      "default": "k-means++",
      "label": "Init",
      "description": "Method for centroid initialization.",
    },
    {
      "name": "n_init",
      "type": "int",
      "default": 10,
      "label": "N Init",
      "description": "Number of times the algorithm is run with different centroid seeds.",
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": 300,
      "label": "Max Iter",
      "description": "Maximum number of iterations for a single run.",
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State",
      "description": "Controls reproducibility of centroid initialization.",
    },
  ],
}
