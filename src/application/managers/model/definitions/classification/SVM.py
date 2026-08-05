SVM_REGISTRY_INSTANCE =  {
  "module": "sklearn.svm",
  "class": "SVC",
  "title": {"en_US": "SVM", "pt_BR": "SVM"},
  "description": "A machine learning model that finds the best line or boundary (hyperplane) to separate different categories of data.",
  "params": [
    {
      "name": "C",
      "type": "float",
      "default": 1.0,
      "label": "C (Regularization)",
      "description": "Controls the penalty for misclassifying data points. Quality effect: High values force the model to classify training data strictly (can lead to overfitting); low values create a smoother boundary (helps prevent overfitting). Performance effect: Higher values can significantly increase training time."
    },
    {
      "name": "kernel",
      "type": "categorical",
      "options": ["linear", "poly", "rbf", "sigmoid", "precomputed"],
      "default": "rbf",
      "label": "Kernel",
      "description": "The mathematical function used to transform data to find a separating boundary. Quality effect: 'rbf' works well for complex data, while 'linear' is better for simple, easily separable data. Performance effect: 'linear' is generally much faster to train and predict than non-linear kernels like 'poly' or 'rbf'."
    },
    {
      "name": "degree",
      "type": "int",
      "default": 3,
      "label": "Degree",
      "description": "The degree of the polynomial when using the 'poly' kernel (ignored by other kernels). Quality effect: Higher degrees allow the model to fit highly complex patterns, increasing the risk of overfitting. Performance effect: Higher values severely increase training and prediction time."
    },
    {
      "name": "gamma",
      "type": "categorical",
      "options": ["scale", "auto"],
      "default": "scale",
      "label": "Gamma",
      "description": "Determines the influence of a single training example in 'rbf', 'poly', and 'sigmoid' kernels. Quality effect: High values create very tight, complex boundaries (high overfitting risk); low values create broader, smoother boundaries. Performance effect: Extremely high values can increase training time."
    },
    {
      "name": "coef0",
      "type": "float",
      "default": 0.0,
      "label": "Coef0",
      "description": "An independent constant added to 'poly' and 'sigmoid' kernel functions. Quality effect: Controls how much the model is influenced by high-degree polynomials versus low-degree ones, helping fine-tune complex models. Performance effect: Negligible impact on computation time."
    },
    {
      "name": "probability",
      "type": "categorical",
      "options": [True, False],
      "default": False,
      "label": "Probability",
      "description": "Whether to calculate the actual probability of a prediction belonging to a class. Quality effect: Does not affect the final decision boundary or base accuracy, but provides useful confidence scores. Performance effect: Setting this to True heavily increases training time due to internal cross-validation."
    },
    {
      "name": "shrinking",
      "type": "categorical",
      "options": [True, False],
      "default": True,
      "label": "Shrinking",
      "description": "Whether to use a mathematical shortcut (shrinking heuristic) during optimization. Quality effect: Zero impact on the final model accuracy or decision boundary. Performance effect: Setting it to True generally speeds up training, especially on large datasets."
    },
    {
      "name": "tol",
      "type": "float",
      "default": 0.001,
      "label": "Tolerance",
      "description": "The threshold that tells the algorithm when to stop searching for a better boundary. Quality effect: Very large values might stop the training too early (underfitting); small values ensure a precise boundary. Performance effect: Smaller tolerances increase training time because the algorithm runs for more iterations."
    },
    {
      "name": "class_weight",
      "type": "categorical",
      "options": ["None", "balanced"],
      "default": "None",
      "label": "Class Weight",
      "description": "Adjusts the penalty for misclassifying specific classes. Quality effect: Using 'balanced' is crucial for imbalanced datasets, heavily improving the prediction accuracy for minority classes. Performance effect: Negligible impact on computation time."
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": -1,
      "label": "Max Iterations",
      "description": "A strict limit on the number of mathematical steps the algorithm can take. Quality effect: If set too low, the model will stop before finding a good boundary, destroying accuracy. '-1' means no limit. Performance effect: A low number forces early stopping, speeding up training but at a severe cost to model quality."
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State",
      "description": "Controls the randomness used in shuffling data (only relevant if probability is True). Quality effect: Ensures reproducible results across multiple runs without fundamentally altering the model's accuracy. Performance effect: No impact on computation time."
    }
  ]
}