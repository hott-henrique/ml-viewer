DECISION_TREE_REGISTRY_INSTANCE =  {
  "module": "sklearn.tree",
  "class": "DecisionTreeClassifier",
  "params": [
    {
      "name": "criterion",
      "type": "categorical",
      "options": ["gini", "entropy", "log_loss"],
      "default": "gini",
      "label": "Criterion"
    },
    {
      "name": "splitter",
      "type": "categorical",
      "options": ["best", "random"],
      "default": "best",
      "label": "Splitter"
    },
    {
      "name": "max_depth",
      "type": "int",
      "default": "",
      "label": "Max Depth"
    },
    {
      "name": "min_samples_split",
      "type": "float",
      "default": 1.9,
      "label": "Min Samples Split"
    },
    {
      "name": "min_samples_leaf",
      "type": "float",
      "default": 0.9,
      "label": "Min Samples Leaf"
    },
    {
      "name": "min_weight_fraction_leaf",
      "type": "float",
      "default": 0.0,
      "label": "Min Weight Fraction Leaf"
    },
    {
      "name": "max_features",
      "type": "categorical",
      "options": ["None", "sqrt", "log2"],
      "default": "None",
      "label": "Max Features"
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State"
    },
    {
      "name": "max_leaf_nodes",
      "type": "int",
      "default": "",
      "label": "Max Leaf Nodes"
    },
    {
      "name": "min_impurity_decrease",
      "type": "float",
      "default": 0.0,
      "label": "Min Impurity Decrease"
    },
    {
      "name": "class_weight",
      "type": "categorical",
      "options": ["None", "balanced"],
      "default": "None",
      "label": "Class Weight"
    },
    {
      "name": "ccp_alpha",
      "type": "float",
      "default": 0.0,
      "label": "CCP Alpha"
    }
  ]
}