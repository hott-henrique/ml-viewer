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

# Backward-compatible alias used by export/pickle helpers that accept any trained estimator.
ModelAPI = (
  SupervisedModelAPI
  | ClusteringModelAPI
  | DimensionalityReductionModelAPI
  | AssociationRulesModelAPI
)
