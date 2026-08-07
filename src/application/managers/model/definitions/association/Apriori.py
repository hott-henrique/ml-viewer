import typing as t

import pandas as pd

from mlxtend.frequent_patterns import apriori, association_rules


class Apriori:
  """Association-rules miner wrapping mlxtend's Apriori + association_rules."""

  def __init__(
    self,
    min_support: float = 0.1,
    min_confidence: float = 0.5,
    min_lift: float = 1.0,
    max_len: int = 0,
    **params: t.Any,
  ) -> None:
    self.min_support = float(min_support)
    self.min_confidence = float(min_confidence)
    self.min_lift = float(min_lift)
    # 0 means unlimited (HyperParamForm has no native None for int).
    self.max_len = None if int(max_len) <= 0 else int(max_len)
    self._frequent_itemsets: pd.DataFrame = pd.DataFrame()
    self._rules: pd.DataFrame = pd.DataFrame()

  def fit(self, X: t.Any, y: t.Any = None, **fit_params: t.Any) -> "Apriori":
    if isinstance(X, pd.DataFrame):
      frame = X.copy()
    else:
      frame = pd.DataFrame(X)

    frame = frame.astype(bool)

    if frame.empty or frame.shape[1] == 0:
      raise ValueError("Apriori requires a non-empty binary item matrix.")

    self._frequent_itemsets = apriori(
      frame,
      min_support=self.min_support,
      use_colnames=True,
      max_len=self.max_len,
    )

    if self._frequent_itemsets.empty:
      self._rules = pd.DataFrame()
      return self

    rules = association_rules(
      self._frequent_itemsets,
      metric="confidence",
      min_threshold=self.min_confidence,
    )

    if not rules.empty and "lift" in rules.columns:
      rules = rules[rules["lift"] >= self.min_lift]

    self._rules = rules.reset_index(drop=True)
    return self

  def get_frequent_itemsets(self) -> pd.DataFrame:
    return self._frequent_itemsets.copy()

  def get_rules(self) -> pd.DataFrame:
    return self._rules.copy()

  def get_params(self) -> dict[str, t.Any]:
    return {
      "min_support": self.min_support,
      "min_confidence": self.min_confidence,
      "min_lift": self.min_lift,
      "max_len": 0 if self.max_len is None else self.max_len,
    }


APRIORI_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.association.Apriori",
  "class": "Apriori",
  "title": {"en_US": "Apriori", "pt_BR": "Apriori"},
  "description": {
    "en_US": "Finds frequent itemsets with Apriori and derives association rules (support, confidence, lift).",
    "pt_BR": "Encontra itemsets frequentes com Apriori e deriva regras de associação (suporte, confiança, lift).",
  },
  "params": [
    {
      "name": "min_support",
      "type": "float",
      "default": 0.1,
      "label": {"en_US": "Min Support", "pt_BR": "Suporte mínimo"},
      "description": {
        "en_US": "Minimum support threshold for frequent itemsets (0–1).",
        "pt_BR": "Limiar mínimo de suporte para itemsets frequentes (0–1).",
      },
    },
    {
      "name": "min_confidence",
      "type": "float",
      "default": 0.5,
      "label": {"en_US": "Min Confidence", "pt_BR": "Confiança mínima"},
      "description": {
        "en_US": "Minimum confidence threshold for association rules (0–1).",
        "pt_BR": "Limiar mínimo de confiança para regras de associação (0–1).",
      },
    },
    {
      "name": "min_lift",
      "type": "float",
      "default": 1.0,
      "label": {"en_US": "Min Lift", "pt_BR": "Lift mínimo"},
      "description": {
        "en_US": "Keep only rules whose lift is at least this value.",
        "pt_BR": "Mantém apenas regras com lift maior ou igual a este valor.",
      },
    },
    {
      "name": "max_len",
      "type": "int",
      "default": 0,
      "label": {"en_US": "Max Itemset Length", "pt_BR": "Tamanho máx. do itemset"},
      "description": {
        "en_US": "Maximum size of itemsets. Use 0 for unlimited.",
        "pt_BR": "Tamanho máximo dos itemsets. Use 0 para ilimitado.",
      },
    },
  ],
}
