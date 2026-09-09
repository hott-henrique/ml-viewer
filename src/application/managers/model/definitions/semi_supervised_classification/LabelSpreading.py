from __future__ import annotations

import typing as t

import numpy as np
import pandas as pd
from sklearn.semi_supervised import LabelSpreading as SklearnLabelSpreading


def _to_numpy(X: t.Any) -> np.ndarray:
  if isinstance(X, pd.DataFrame):
    return X.to_numpy(dtype=float)
  return np.asarray(X, dtype=float)


def _to_1d(y: t.Any) -> np.ndarray:
  if isinstance(y, pd.Series):
    return y.to_numpy()
  arr = np.asarray(y)
  return arr.ravel()


class LabelSpreading:
  """Semi-supervised classifier wrapping sklearn LabelSpreading with fit(X_l, y_l, X_u)."""

  def __init__(
    self,
    kernel: str = "rbf",
    gamma: float = 20.0,
    n_neighbors: int = 7,
    alpha: float = 0.2,
    max_iter: int = 30,
    tol: float = 0.001,
    **params: t.Any,
  ) -> None:
    self.kernel = kernel
    self.gamma = float(gamma)
    self.n_neighbors = int(n_neighbors)
    self.alpha = float(alpha)
    self.max_iter = int(max_iter)
    self.tol = float(tol)
    self._model = SklearnLabelSpreading(
      kernel=self.kernel,
      gamma=self.gamma,
      n_neighbors=self.n_neighbors,
      alpha=self.alpha,
      max_iter=self.max_iter,
      tol=self.tol,
    )

  def fit(self, X_l: t.Any, y_l: t.Any, X_u: t.Any, **fit_params: t.Any) -> "LabelSpreading":
    Xl = _to_numpy(X_l)
    Xu = _to_numpy(X_u)
    yl = _to_1d(y_l)

    if Xu.size == 0:
      X = Xl
      y = yl
    else:
      X = np.vstack([Xl, Xu])
      y = np.concatenate([yl, np.full(Xu.shape[0], -1)])

    self._model.fit(X, y)
    return self

  def predict(self, X: t.Any) -> t.Any:
    return self._model.predict(_to_numpy(X))

  def get_params(self) -> dict[str, t.Any]:
    return {
      "kernel": self.kernel,
      "gamma": self.gamma,
      "n_neighbors": self.n_neighbors,
      "alpha": self.alpha,
      "max_iter": self.max_iter,
      "tol": self.tol,
    }


LABEL_SPREADING_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.semi_supervised_classification.LabelSpreading",
  "class": "LabelSpreading",
  "title": {"en_US": "Label Spreading", "pt_BR": "Label Spreading"},
  "description": {
    "en_US": "Graph-based semi-supervised classifier (sklearn LabelSpreading).",
    "pt_BR": "Classificador semi-supervisionado baseado em grafo (sklearn LabelSpreading).",
  },
  "params": [
    {
      "name": "kernel",
      "type": "categorical",
      "options": ["knn", "rbf"],
      "default": "rbf",
      "label": {"en_US": "Kernel", "pt_BR": "Kernel"},
      "description": {
        "en_US": "Similarity kernel for the label graph.",
        "pt_BR": "Kernel de similaridade para o grafo de rótulos.",
      },
    },
    {
      "name": "gamma",
      "type": "float",
      "default": 20.0,
      "label": {"en_US": "Gamma", "pt_BR": "Gamma"},
      "description": {
        "en_US": "RBF kernel parameter (ignored for knn).",
        "pt_BR": "Parâmetro do kernel RBF (ignorado no knn).",
      },
    },
    {
      "name": "n_neighbors",
      "type": "int",
      "default": 7,
      "label": {"en_US": "Neighbors", "pt_BR": "Vizinhos"},
      "description": {
        "en_US": "Number of neighbors for the knn kernel.",
        "pt_BR": "Número de vizinhos para o kernel knn.",
      },
    },
    {
      "name": "alpha",
      "type": "float",
      "default": 0.2,
      "label": {"en_US": "Alpha", "pt_BR": "Alpha"},
      "description": {
        "en_US": "Clamping factor (0 = hard clamp to labeled points).",
        "pt_BR": "Fator de clamping (0 = fixa os pontos rotulados).",
      },
    },
    {
      "name": "max_iter",
      "type": "int",
      "default": 30,
      "label": {"en_US": "Max Iterations", "pt_BR": "Máx. iterações"},
      "description": {
        "en_US": "Maximum iterations for label spreading.",
        "pt_BR": "Máximo de iterações do label spreading.",
      },
    },
    {
      "name": "tol",
      "type": "float",
      "default": 0.001,
      "label": {"en_US": "Tolerance", "pt_BR": "Tolerância"},
      "description": {
        "en_US": "Convergence tolerance.",
        "pt_BR": "Tolerância de convergência.",
      },
    },
  ],
}
