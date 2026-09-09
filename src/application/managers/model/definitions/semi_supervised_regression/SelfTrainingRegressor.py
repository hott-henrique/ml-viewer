from __future__ import annotations

import typing as t

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors


def _to_numpy(X: t.Any) -> np.ndarray:
  if isinstance(X, pd.DataFrame):
    return X.to_numpy(dtype=float)
  return np.asarray(X, dtype=float)


def _to_1d(y: t.Any) -> np.ndarray:
  if isinstance(y, pd.Series):
    return y.to_numpy(dtype=float)
  return np.asarray(y, dtype=float).ravel()


class SelfTrainingRegressor:
  """Iterative self-training regressor with a LinearRegression base estimator."""

  def __init__(
    self,
    threshold: float = 0.1,
    max_iter: int = 10,
    n_neighbors: int = 5,
    fit_intercept: bool = True,
    copy_X: bool = True,
    positive: bool = False,
    n_jobs: int = -1,
    **params: t.Any,
  ) -> None:
    self.threshold = float(threshold)
    self.max_iter = int(max_iter)
    self.n_neighbors = int(n_neighbors)
    self.fit_intercept = bool(fit_intercept)
    self.copy_X = bool(copy_X)
    self.positive = bool(positive)
    self.n_jobs = int(n_jobs)
    self._model = LinearRegression(
      fit_intercept=self.fit_intercept,
      copy_X=self.copy_X,
      positive=self.positive,
      n_jobs=self.n_jobs,
    )

  def fit(self, X_l: t.Any, y_l: t.Any, X_u: t.Any, **fit_params: t.Any) -> "SelfTrainingRegressor":
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
      "fit_intercept": self.fit_intercept,
      "copy_X": self.copy_X,
      "positive": self.positive,
      "n_jobs": self.n_jobs,
    }


SELF_TRAINING_REGRESSOR_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.semi_supervised_regression.SelfTrainingRegressor",
  "class": "SelfTrainingRegressor",
  "title": {"en_US": "Self-Training Regressor", "pt_BR": "Self-Training Regressor"},
  "description": {
    "en_US": "Self-training LinearRegression that pseudo-labels unlabeled points agreeing with labeled neighbors.",
    "pt_BR": "LinearRegression com self-training que pseudo-rotula pontos alinhados aos vizinhos rotulados.",
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
      "name": "fit_intercept",
      "type": "bool",
      "default": True,
      "label": {"en_US": "Fit Intercept", "pt_BR": "Ajustar intercepto"},
      "description": {
        "en_US": "Whether LinearRegression fits an intercept.",
        "pt_BR": "Se a LinearRegression ajusta um intercepto.",
      },
    },
    {
      "name": "copy_X",
      "type": "bool",
      "default": True,
      "label": {"en_US": "Copy X", "pt_BR": "Copiar X"},
      "description": {
        "en_US": "Whether to copy X before fitting.",
        "pt_BR": "Se deve copiar X antes do fit.",
      },
    },
    {
      "name": "positive",
      "type": "bool",
      "default": False,
      "label": {"en_US": "Positive Coefficients", "pt_BR": "Coeficientes positivos"},
      "description": {
        "en_US": "Force non-negative coefficients.",
        "pt_BR": "Força coeficientes não negativos.",
      },
    },
    {
      "name": "n_jobs",
      "type": "int",
      "default": -1,
      "label": {"en_US": "N-Jobs", "pt_BR": "N-Jobs"},
      "description": {
        "en_US": "Number of CPU cores for LinearRegression.",
        "pt_BR": "Número de núcleos de CPU para LinearRegression.",
      },
    },
  ],
}
