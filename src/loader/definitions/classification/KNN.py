KNN_REGISTRY_INSTANCE =  {
  "module": "sklearn.neighbors",
  "class": "KNeighborsClassifier",
  "description": "A simple algorithm that classifies a new data point based on the most common category among its closest k neighbors.",
  "params": [
    {
      "name": "n_neighbors",
      "type": "int",
      "default": 5,
      "label": "Number of Neighbors"
    },
    {
      "name": "weights",
      "type": "categorical",
      "options": ["uniform", "distance"],
      "default": "uniform",
      "label": "Weights"
    },
    {
      "name": "algorithm",
      "type": "categorical",
      "options": ["auto", "ball_tree", "kd_tree", "brute"],
      "default": "auto",
      "label": "Algorithm"
    },
    {
      "name": "leaf_size",
      "type": "int",
      "default": 30,
      "label": "Leaf Size"
    },
    {
      "name": "p",
      "type": "int",
      "default": 2,
      "label": "Power Parameter (p)"
    },
    {
      "name": "metric",
      "type": "categorical",
      "options": ["minkowski", "euclidean", "manhattan", "chebyshev"],
      "default": "minkowski",
      "label": "Metric"
    },
    {
      "name": "n_jobs",
      "type": "int",
      "default": -1,
      "label": "N-Jobs"
    }
  ]
}