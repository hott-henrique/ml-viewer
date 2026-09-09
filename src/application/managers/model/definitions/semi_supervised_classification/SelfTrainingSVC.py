from __future__ import annotations

import typing as t

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.semi_supervised import SelfTrainingClassifier
from sklearn.svm import SVC

from application.managers.model.definitions.semi_supervised_classification.LabelSpreading import _to_1d, _to_numpy


class SelfTrainingSVC:
  """Self-training classifier with an SVC base estimator; fit(X_l, y_l, X_u)."""

  def __init__(
    self,
    threshold: float = 0.75,
    criterion: str = "threshold",
    k_best: int = 10,
    max_iter: int = 10,
    C: float = 1.0,
    kernel: str = "rbf",
    gamma: str = "scale",
    **params: t.Any,
  ) -> None:
    self.threshold = float(threshold)
    self.criterion = criterion
    self.k_best = int(k_best)
    self.max_iter = int(max_iter)
    self.C = float(C)
    self.kernel = kernel
    self.gamma = gamma
    # SelfTraining needs predict_proba; calibrate SVC (probability=True is deprecated).
    base = CalibratedClassifierCV(SVC(C=self.C, kernel=self.kernel, gamma=self.gamma), ensemble=False)
    self._model = SelfTrainingClassifier(
      base,
      threshold=self.threshold,
      criterion=self.criterion,
      k_best=self.k_best,
      max_iter=self.max_iter,
    )

  def fit(self, X_l: t.Any, y_l: t.Any, X_u: t.Any, **fit_params: t.Any) -> "SelfTrainingSVC":
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
      "threshold": self.threshold,
      "criterion": self.criterion,
      "k_best": self.k_best,
      "max_iter": self.max_iter,
      "C": self.C,
      "kernel": self.kernel,
      "gamma": self.gamma,
    }


SELF_TRAINING_SVC_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.semi_supervised_classification.SelfTrainingSVC",
  "class": "SelfTrainingSVC",
  "title": {"en_US": "Self-Training (SVC)", "pt_BR": "Self-Training (SVC)"},
  "description": {
    "en_US": "Self-training wrapper around SVC with probability-based pseudo-labels.",
    "pt_BR": "Self-training em torno de SVC com pseudo-rótulos por probabilidade.",
  },
  "params": [
    {
      "name": "threshold",
      "type": "float",
      "default": 0.75,
      "label": {"en_US": "Threshold", "pt_BR": "Limiar"},
      "description": {
        "en_US": "Minimum prediction probability to accept a pseudo-label.",
        "pt_BR": "Probabilidade mínima para aceitar um pseudo-rótulo.",
      },
    },
    {
      "name": "criterion",
      "type": "categorical",
      "options": ["threshold", "k_best"],
      "default": "threshold",
      "label": {"en_US": "Criterion", "pt_BR": "Critério"},
      "description": {
        "en_US": "How pseudo-labels are selected each iteration.",
        "pt_BR": "Como os pseudo-rótulos são selecionados a cada iteração.",
      },
    },
    {
      "name": "k_best",
      "type": "int",
      "default": 10,
      "label": {"en_US": "K Best", "pt_BR": "K melhores"},
      "description": {
        "en_US": "Number of samples to pseudo-label when criterion is k_best.",
        "pt_BR": "Quantidade de amostras para pseudo-rotular quando o critério é k_best.",
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
      "name": "C",
      "type": "float",
      "default": 1.0,
      "label": {"en_US": "C (Regularization)", "pt_BR": "C (Regularização)"},
      "description": {
        "en_US": "SVC regularization parameter.",
        "pt_BR": "Parâmetro de regularização do SVC.",
      },
    },
    {
      "name": "kernel",
      "type": "categorical",
      "options": ["linear", "poly", "rbf", "sigmoid"],
      "default": "rbf",
      "label": {"en_US": "Kernel", "pt_BR": "Kernel"},
      "description": {
        "en_US": "SVC kernel type.",
        "pt_BR": "Tipo de kernel do SVC.",
      },
    },
    {
      "name": "gamma",
      "type": "categorical",
      "options": ["scale", "auto"],
      "default": "scale",
      "label": {"en_US": "Gamma", "pt_BR": "Gamma"},
      "description": {
        "en_US": "Kernel coefficient for rbf/poly/sigmoid.",
        "pt_BR": "Coeficiente do kernel para rbf/poly/sigmoid.",
      },
    },
  ],
}
