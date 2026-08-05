LINEAR_REGRESSION_REGISTRY_INSTANCE = {
  "module": "sklearn.linear_model",
  "class": "LinearRegression",
  "title": {"en_US": "Linear Regression", "pt_BR": "Regressão Linear"},
  "description": "A foundational algorithm that predicts a continuous number by finding the best-fitting straight line (or hyperplane) through the data points.",
  "params": [
    {
      "name": "fit_intercept",
      "type": "bool",
      "default": True,
      "label": "Fit Intercept",
      "description": "Determines whether to calculate the y-intercept (the point where the line crosses the y-axis) for this model. Quality effect: Keep it True unless you are absolutely sure your data is already centered around zero; setting it to False on uncentered data will severely degrade accuracy. Performance effect: Setting it to False slightly speeds up computation as it skips a mathematical step."
    },
    {
      "name": "copy_X",
      "type": "bool",
      "default": True,
      "label": "Copy X",
      "description": "Whether to create a copy of the input data or overwrite it during internal calculations. Quality effect: Zero impact on model accuracy or final predictions. Performance effect: Setting it to False saves memory and slightly speeds up execution on very large datasets, but modifies your original dataset in place."
    },
    {
      "name": "positive",
      "type": "bool",
      "default": False,
      "label": "Positive Coefficients",
      "description": "Forces all predicted weights (coefficients) to be positive numbers. Quality effect: Useful only if you have strict domain knowledge that the features must have a positive relationship with the target; otherwise, it restricts the model and usually reduces accuracy. Performance effect: Setting it to True requires a different optimization solver, which can increase computation time."
    },
    {
      "name": "n_jobs",
      "type": "int",
      "default": -1,
      "label": "N-Jobs",
      "description": "The number of CPU cores to use for computation (mostly relevant when predicting multiple target variables simultaneously). Quality effect: Zero impact on the model's accuracy. Performance effect: Setting this to -1 uses all available cores, which can speed up training on multi-output datasets, but has no effect on standard single-target regression."
    }
  ]
}