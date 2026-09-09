from __future__ import annotations

import typing as t

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.tree import DecisionTreeRegressor

from application.managers.model.definitions.semi_supervised_regression.SelfTrainingRegressor import (
  _to_1d,
  _to_numpy,
)


class SelfTrainingDecisionTreeRegressor:
  """Self-training regressor with a DecisionTreeRegressor base estimator."""

  def __init__(
    self,
    threshold: float = 0.1,
    max_iter: int = 10,
    n_neighbors: int = 5,
    max_depth: int | None = None,
    min_samples_split: int = 2,
    min_samples_leaf: int = 1,
    random_state: int = 42,
    **params: t.Any,
  ) -> None:
    self.threshold = float(threshold)
    self.max_iter = int(max_iter)
    self.n_neighbors = int(n_neighbors)
    # HyperParamForm may pass "" for unlimited depth.
    if max_depth == "" or max_depth is None:
      self.max_depth = None
    else:
      self.max_depth = int(max_depth)
    self.min_samples_split = int(min_samples_split)
    self.min_samples_leaf = int(min_samples_leaf)
    self.random_state = int(random_state)
    self._model = DecisionTreeRegressor(
      max_depth=self.max_depth,
      min_samples_split=self.min_samples_split,
      min_samples_leaf=self.min_samples_leaf,
      random_state=self.random_state,
    )

  def fit(self, X_l: t.Any, y_l: t.Any, X_u: t.Any, **fit_params: t.Any) -> "SelfTrainingDecisionTreeRegressor":
    Xl = _to_numpy(X_l)
    yl = _to_1d(y_l)
    Xu = _to_numpy(X_u)

    if Xu.size == 0 or Xu.shape[0] == 0:
      self._model.fit(Xl, yl)
      return self

    for _ in range(self.max_iter):
      self._model.fit(Xl, yl)

      if Xu.shape[0] == 0:
        break

      preds = self._model.predict(Xu)
      k = min(self.n_neighbors, Xl.shape[0])
      nn = NearestNeighbors(n_neighbors=k)
      nn.fit(Xl)
      _distances, indices = nn.kneighbors(Xu)
      neighbor_means = yl[indices].mean(axis=1)
      disagreement = np.abs(preds - neighbor_means)
      mask = disagreement <= self.threshold

      if not np.any(mask):
        break

      Xl = np.vstack([Xl, Xu[mask]])
      yl = np.concatenate([yl, preds[mask]])
      Xu = Xu[~mask]

    self._model.fit(Xl, yl)
    return self

  def predict(self, X: t.Any) -> t.Any:
    return self._model.predict(_to_numpy(X))

  def get_params(self) -> dict[str, t.Any]:
    return {
      "threshold": self.threshold,
      "max_iter": self.max_iter,
      "n_neighbors": self.n_neighbors,
      "max_depth": self.max_depth if self.max_depth is not None else "",
      "min_samples_split": self.min_samples_split,
      "min_samples_leaf": self.min_samples_leaf,
      "random_state": self.random_state,
    }


SELF_TRAINING_DECISION_TREE_REGRESSOR_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.semi_supervised_regression.SelfTrainingDecisionTreeRegressor",
  "class": "SelfTrainingDecisionTreeRegressor",
  "title": {
    "en_US": "Self-Training (Decision Tree)",
    "pt_BR": "Self-Training (Árvore de Decisão)",
  },
  "description": {
    "en_US": "Self-training DecisionTreeRegressor that pseudo-labels unlabeled points agreeing with labeled neighbors.",
    "pt_BR": "DecisionTreeRegressor com self-training que pseudo-rotula pontos alinhados aos vizinhos rotulados.",
  },
  "params": [
    {
      "name": "threshold",
      "type": "float",
      "default": 0.1,
      "label": {"en_US": "Threshold", "pt_BR": "Limiar"},
      "description": {
        "en_US": "Max |prediction − neighbor mean| to accept a pseudo-label.",
        "pt_BR": "Máximo |predição − média dos vizinhos| para aceitar um pseudo-rótulo.",
      },
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": 10,
      "label": {"en_US": "Max Iterations", "pt_BR": "Máx. iterações"},
      "description": {
        "en_US": "Maximum self-training iterations.",
        "pt_BR": "Máximo de iterações do self-training.",
      },
    },
    {
      "name": "n_neighbors",
      "type": "int",
      "default": 5,
      "label": {"en_US": "Neighbors", "pt_BR": "Vizinhos"},
      "description": {
        "en_US": "Labeled neighbors used to score pseudo-label agreement.",
        "pt_BR": "Vizinhos rotulados usados para avaliar o pseudo-rótulo.",
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
