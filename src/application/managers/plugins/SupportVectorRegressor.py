MODEL_CONFIG = {
  "Support Vector Regressor (SVR)": {
    "type": "Regression", 
    "module": "sklearn.svm",
    "class": "SVR",
    "description": "Epsilon-Support Vector Regression. Fits the error within a certain threshold.",
    "params": [
      {
        "name": "C",
        "type": "float",
        "default": 1.0,
        "label": "Regularization (C)",
        "description": "Regularization parameter. The strength of the regularization is inversely proportional to C."
      },
      {
        "name": "kernel",
        "type": "categorical",
        "default": "rbf",
        "options": ["linear", "poly", "rbf", "sigmoid"],
        "label": "Kernel Type",
        "description": "Specifies the kernel type to be used in the algorithm."
      }
    ]
  }
}