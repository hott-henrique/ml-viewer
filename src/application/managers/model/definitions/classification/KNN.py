KNN_REGISTRY_INSTANCE =  {
  "module": "sklearn.neighbors",
  "class": "KNeighborsClassifier",
  "title": {"en_US": "K-Nearest Neighbors", "pt_BR": "K-Vizinhos Mais Próximos"},
  "description": "A simple algorithm that classifies a new data point based on the most common category among its closest k neighbors.",
  "params": [
    {
      "name": "n_neighbors",
      "type": "int",
      "default": 5,
      "label": "Number of Neighbors",
      "description": "The number of closest data points to look at when making a prediction. Quality effect: Lower values create complex decision boundaries (prone to overfitting), while higher values create smoother boundaries (can lead to underfitting). Performance effect: Higher values slightly increase prediction time."
    },
    {
      "name": "weights",
      "type": "categorical",
      "options": ["uniform", "distance"],
      "default": "uniform",
      "label": "Weights",
      "description": "Determines how much influence each neighbor has on the prediction. Quality effect: 'distance' gives closer neighbors more influence, which often improves accuracy and helps handle uneven data distribution. Performance effect: 'distance' adds a minor computational overhead during prediction compared to 'uniform'."
    },
    {
      "name": "algorithm",
      "type": "categorical",
      "options": ["auto", "ball_tree", "kd_tree", "brute"],
      "default": "auto",
      "label": "Algorithm",
      "description": "The underlying mathematical method used to find nearest neighbors. Quality effect: Zero impact on the final predictions; all options find the exact same neighbors. Performance effect: Huge impact. Tree-based methods ('kd_tree', 'ball_tree') are significantly faster than 'brute' force on large datasets. 'auto' selects the best option."
    },
    {
      "name": "leaf_size",
      "type": "int",
      "default": 30,
      "label": "Leaf Size",
      "description": "The maximum number of points in a tree node before it splits (used only with 'kd_tree' or 'ball_tree'). Quality effect: Zero impact on model accuracy or predictions. Performance effect: Affects the memory required to store the tree and balances tree construction time against query time."
    },
    {
      "name": "p",
      "type": "int",
      "default": 2,
      "label": "Power Parameter (p)",
      "description": "The power parameter for the Minkowski distance (p=1 is Manhattan, p=2 is Euclidean). Quality effect: Changes how distance is measured, which can shift predictions depending on the dataset's features. Performance effect: Standard values like 1 or 2 are highly optimized, while other values might compute slightly slower."
    },
    {
      "name": "metric",
      "type": "categorical",
      "options": ["minkowski", "euclidean", "manhattan", "chebyshev"],
      "default": "minkowski",
      "label": "Metric",
      "description": "The mathematical formula used to calculate the distance between data points. Quality effect: Choosing the right metric for your specific data type (e.g., Manhattan for grid-like data) strongly improves accuracy. Performance effect: More mathematically complex metrics increase prediction time."
    },
    {
      "name": "n_jobs",
      "type": "int",
      "default": -1,
      "label": "N-Jobs",
      "description": "The number of CPU cores to use for computing neighbors. Quality effect: Zero impact on the model's accuracy or final predictions. Performance effect: Setting this to -1 uses all available cores, massively speeding up the prediction phase on large datasets."
    }
  ]
}