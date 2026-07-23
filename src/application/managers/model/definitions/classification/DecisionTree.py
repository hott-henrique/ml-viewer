DECISION_TREE_REGISTRY_INSTANCE =  {
  "module": "sklearn.tree",
  "class": "DecisionTreeClassifier",
  "description": "A flowchart-like model that makes predictions by continuously splitting data into smaller groups based on a series of yes/no questions about its features.",
  "params": [
    {
      "name": "criterion",
      "type": "categorical",
      "options": ["gini", "entropy", "log_loss"],
      "default": "gini",
      "label": "Criterion",
      "description": "The function used to measure the quality of a split. Quality effect: Minor differences, though 'entropy' may yield slightly more balanced trees. Performance effect: 'gini' is faster to compute than 'entropy' because it doesn't require calculating logarithms."
    },
    {
      "name": "splitter",
      "type": "categorical",
      "options": ["best", "random"],
      "default": "best",
      "label": "Splitter",
      "description": "The strategy used to choose the split at each node. Quality effect: 'best' maximizes accuracy but can lead to overfitting; 'random' increases diversity and reduces overfitting. Performance effect: 'random' is significantly faster to compute, especially on large datasets."
    },
    {
      "name": "max_depth",
      "type": "int",
      "default": "",
      "label": "Max Depth",
      "description": "The maximum depth of the tree. Quality effect: Restricting depth prevents overfitting by stopping the tree from perfectly memorizing the training data. Performance effect: Lower values drastically reduce both training and prediction times."
    },
    {
      "name": "min_samples_split",
      "type": "float",
      "default": 1.9,
      "label": "Min Samples Split",
      "description": "The minimum number of samples required to split an internal node. Quality effect: Higher values prevent overfitting by forcing the model to make more generalized splits. Performance effect: Higher values slightly speed up training by stopping tree growth earlier."
    },
    {
      "name": "min_samples_leaf",
      "type": "float",
      "default": 0.9,
      "label": "Min Samples Leaf",
      "description": "The minimum number of samples required to be at a leaf (end) node. Quality effect: Higher values smooth the model and heavily reduce overfitting by eliminating nodes with very few samples. Performance effect: Larger values shrink tree complexity, improving computation speed."
    },
    {
      "name": "min_weight_fraction_leaf",
      "type": "float",
      "default": 0.0,
      "label": "Min Weight Fraction Leaf",
      "description": "The minimum weighted fraction of total weights required to be at a leaf node. Quality effect: Acts as a regularization technique to prevent overfitting, especially useful for datasets with sample weights. Performance effect: Halts tree growth earlier, reducing computation time."
    },
    {
      "name": "max_features",
      "type": "categorical",
      "options": ["None", "sqrt", "log2"],
      "default": "None",
      "label": "Max Features",
      "description": "The number of features to consider when looking for the best split. Quality effect: Using a subset of features increases randomness and helps prevent overfitting. Performance effect: Using a subset (e.g., 'sqrt') massively speeds up the search for splits."
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": "Random State",
      "description": "Controls the randomness of the estimator. Quality effect: Ensures results are reproducible across multiple runs without fundamentally altering the model's absolute accuracy. Performance effect: No impact on computation time."
    },
    {
      "name": "max_leaf_nodes",
      "type": "int",
      "default": "",
      "label": "Max Leaf Nodes",
      "description": "The maximum number of leaf nodes the tree can have. Quality effect: Restricting this limits tree size, preventing overfitting by keeping the model simple. Performance effect: Smaller values lead to faster training and prediction."
    },
    {
      "name": "min_impurity_decrease",
      "type": "float",
      "default": 0.0,
      "label": "Min Impurity Decrease",
      "description": "A threshold for splitting a node based on impurity reduction. Quality effect: Prevents overfitting by only allowing splits that significantly improve the model's certainty. Performance effect: Speeds up training by halting non-beneficial splits."
    },
    {
      "name": "class_weight",
      "type": "categorical",
      "options": ["None", "balanced"],
      "default": "None",
      "label": "Class Weight",
      "description": "Adjusts weights associated with classes. Quality effect: Using 'balanced' heavily improves predictions for minority classes in imbalanced datasets. Performance effect: Negligible impact on computation time."
    },
    {
      "name": "ccp_alpha",
      "type": "float",
      "default": 0.0,
      "label": "CCP Alpha",
      "description": "Complexity parameter used for Minimal Cost-Complexity Pruning. Quality effect: Larger values heavily penalize tree complexity, strongly reducing overfitting at the cost of training accuracy. Performance effect: Finding the optimal pruning path adds a slight computational overhead."
    }
  ]
}