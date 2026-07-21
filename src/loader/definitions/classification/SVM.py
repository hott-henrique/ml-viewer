SVM_REGISTRY_INSTANCE =  {
  "module": "sklearn.svm",
  "class": "SVC",
  "params": [
    {
      "name": "C",
      "type": "float",
      "default": 1.0,
      "label": "C (Regularization)"
    },
    {
      "name": "kernel",
      "type": "categorical",
      "options": ["linear", "poly", "rbf", "sigmoid", "precomputed"],
      "default": "rbf",
      "label": "Kernel"
    },
    {
      "name": "degree",
      "type": "int",
      "default": 3,
      "label": "Degree"
    },
    {
      "name": "gamma",
      "type": "categorical",
      "options": ["scale", "auto"],
      "default": "scale",
      "label": "Gamma"
    },
    {
      "name": "coef0",
      "type": "float",
      "default": 0.0,
      "label": "Coef0"
    },
    {
      "name": "probability",
      "type": "categorical",
      "options": [True, False],
      "default": False,
      "label": "Probability"
    },
    {
      "name": "shrinking",
      "type": "categorical",
      "options": [True, False],
      "default": True,
      "label": "Shrinking"
    },
    {
      "name": "tol",
      "type": "float",
      "default": 0.001,
      "label": "Tolerance"
    },
    {
      "name": "class_weight",
      "type": "categorical",
      "options": ["None", "balanced"],
      "default": "None",
      "label": "Class Weight"
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": -1,
      "label": "Max Iterations"
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State"
    }
  ]
}