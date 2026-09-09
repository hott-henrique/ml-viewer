DECISION_TREE_REGRESSOR_REGISTRY_INSTANCE = {
  "module": "sklearn.tree",
  "class": "DecisionTreeRegressor",
  "title": {"en_US": "Decision Tree Regressor", "pt_BR": "Árvore de Decisão (Regressão)"},
  "description": {
    "en_US": "Decision tree that predicts continuous targets by recursive feature splits.",
    "pt_BR": "Árvore de decisão que prevê alvos contínuos por partições recursivas de atributos.",
  },
  "params": [
    {
      "name": "criterion",
      "type": "categorical",
      "options": ["squared_error", "friedman_mse", "absolute_error", "poisson"],
      "default": "squared_error",
      "label": {"en_US": "Criterion", "pt_BR": "Critério"},
      "description": {
        "en_US": "Function used to measure split quality.",
        "pt_BR": "Função usada para medir a qualidade do split.",
      },
    },
    {
      "name": "splitter",
      "type": "categorical",
      "options": ["best", "random"],
      "default": "best",
      "label": {"en_US": "Splitter", "pt_BR": "Splitter"},
      "description": {
        "en_US": "Strategy used to choose the split at each node.",
        "pt_BR": "Estratégia para escolher o split em cada nó.",
      },
    },
    {
      "name": "max_depth",
      "type": "int",
      "default": "",
      "label": {"en_US": "Max Depth", "pt_BR": "Profundidade máxima"},
      "description": {
        "en_US": "Maximum tree depth (empty = unlimited).",
        "pt_BR": "Profundidade máxima da árvore (vazio = ilimitado).",
      },
    },
    {
      "name": "min_samples_split",
      "type": "int",
      "default": 2,
      "label": {"en_US": "Min Samples Split", "pt_BR": "Mín. amostras p/ split"},
      "description": {
        "en_US": "Minimum samples required to split an internal node.",
        "pt_BR": "Mínimo de amostras para dividir um nó interno.",
      },
    },
    {
      "name": "min_samples_leaf",
      "type": "int",
      "default": 1,
      "label": {"en_US": "Min Samples Leaf", "pt_BR": "Mín. amostras na folha"},
      "description": {
        "en_US": "Minimum samples required at a leaf node.",
        "pt_BR": "Mínimo de amostras em um nó folha.",
      },
    },
    {
      "name": "random_state",
      "type": "int",
      "default": 42,
      "label": {"en_US": "Random State", "pt_BR": "Random State"},
      "description": {
        "en_US": "Controls randomness for reproducible results.",
        "pt_BR": "Controla a aleatoriedade para resultados reproduzíveis.",
      },
    },
  ],
}
