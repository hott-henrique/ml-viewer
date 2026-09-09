import typing as t

class SupervisedModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any, **fit_params: t.Any) -> "SupervisedModelAPI":
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict:
    ...

class ClusteringModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any = None, **fit_params: t.Any) -> "ClusteringModelAPI":
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict:
    ...

class DimensionalityReductionModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any = None, **fit_params: t.Any) -> "DimensionalityReductionModelAPI":
    ...

  def transform(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict:
    ...

class AssociationRulesModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any = None, **fit_params: t.Any) -> "AssociationRulesModelAPI":
    ...

  def get_frequent_itemsets(self) -> t.Any:
    ...

  def get_rules(self) -> t.Any:
    ...

  def get_params(self) -> dict:
    ...

class AgentAPI(t.Protocol):
  """Reinforcement-learning agent: policy + per-transition update (no training loop)."""

  def select_action(self, state: t.Hashable, *, legal_actions: t.Sequence[t.Hashable], explore: bool = True) -> t.Hashable:
    ...

  def update(self, state: t.Hashable, action: t.Hashable, reward: float, next_state: t.Hashable, *, terminated: bool) -> None:
    ...

  def get_params(self) -> dict:
    ...

class SemiSupervisedModelAPI(t.Protocol):
  def fit(self, X_l: t.Any, y_l: t.Any, X_u: t.Any, **fit_params: t.Any) -> "SemiSupervisedModelAPI":
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict:
    ...

ModelAPI = (
  SupervisedModelAPI
  | ClusteringModelAPI
  | DimensionalityReductionModelAPI
  | AssociationRulesModelAPI
  | AgentAPI
  | SemiSupervisedModelAPI
)
