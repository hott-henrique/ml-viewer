"""Model / agent Protocols that plugins implement (duck-typed at runtime)."""

from __future__ import annotations

import typing as t


class SupervisedModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any, **fit_params: t.Any) -> "SupervisedModelAPI":
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict[str, t.Any]:
    ...


class ClusteringModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any = None, **fit_params: t.Any) -> "ClusteringModelAPI":
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict[str, t.Any]:
    ...


class DimensionalityReductionModelAPI(t.Protocol):
  def fit(
    self, X: t.Any, y: t.Any = None, **fit_params: t.Any
  ) -> "DimensionalityReductionModelAPI":
    ...

  def transform(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict[str, t.Any]:
    ...


class AssociationRulesModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any = None, **fit_params: t.Any) -> "AssociationRulesModelAPI":
    ...

  def get_frequent_itemsets(self) -> t.Any:
    ...

  def get_rules(self) -> t.Any:
    ...

  def get_params(self) -> dict[str, t.Any]:
    ...


class AgentAPI(t.Protocol):
  """Reinforcement-learning agent: policy + per-transition update (no training loop)."""

  def select_action(
    self,
    state: t.Any,
    *,
    legal_actions: t.Sequence[t.Any] = (),
    explore: bool = True,
    action_space: t.Any = None,
  ) -> t.Any:
    ...

  def update(
    self,
    state: t.Any,
    action: t.Any,
    reward: float,
    next_state: t.Any,
    *,
    terminated: bool,
    truncated: bool = False,
  ) -> None:
    ...

  def get_params(self) -> dict[str, t.Any]:
    ...


class SemiSupervisedModelAPI(t.Protocol):
  def fit(
    self, X_l: t.Any, y_l: t.Any, X_u: t.Any, **fit_params: t.Any
  ) -> "SemiSupervisedModelAPI":
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict[str, t.Any]:
    ...


ModelAPI = (
  SupervisedModelAPI
  | ClusteringModelAPI
  | DimensionalityReductionModelAPI
  | AssociationRulesModelAPI
  | AgentAPI
  | SemiSupervisedModelAPI
)
