from __future__ import annotations

import typing as t

import pandas as pd
from mlxtend.frequent_patterns import association_rules


def _eclat_frequent_itemsets(
  frame: pd.DataFrame,
  min_support: float,
  max_len: int | None,
) -> pd.DataFrame:
  """Mine frequent itemsets with Eclat (vertical tidsets)."""
  n_transactions = len(frame)
  if n_transactions == 0:
    return pd.DataFrame(columns=["support", "itemsets"])

  min_count = max(1, int(min_support * n_transactions + 1e-12))
  columns = list(frame.columns)

  # Vertical representation: item -> frozenset of transaction ids
  tidsets: dict[t.Any, frozenset[int]] = {}
  for col in columns:
    tids = frozenset(int(i) for i, present in enumerate(frame[col].tolist()) if bool(present))
    if len(tids) >= min_count:
      tidsets[col] = tids

  frequent: list[tuple[frozenset, float]] = [
    (frozenset([item]), len(tids) / n_transactions) for item, tids in tidsets.items()
  ]

  # Level-wise intersection of tidsets (Eclat-style)
  current: dict[frozenset, frozenset[int]] = {frozenset([item]): tids for item, tids in tidsets.items()}
  k = 2
  while current:
    if max_len is not None and k > max_len:
      break

    items_sorted = sorted(current.keys(), key=lambda s: tuple(sorted(map(str, s))))
    next_level: dict[frozenset, frozenset[int]] = {}

    for i, a in enumerate(items_sorted):
      for b in items_sorted[i + 1 :]:
        union = a | b
        if len(union) != k:
          continue
        # Prefix join: share first k-2 items when sorted
        a_list = sorted(map(str, a))
        b_list = sorted(map(str, b))
        if a_list[: k - 2] != b_list[: k - 2]:
          continue
        inter = current[a] & current[b]
        if len(inter) >= min_count:
          next_level[union] = inter
          frequent.append((union, len(inter) / n_transactions))

    current = next_level
    k += 1

  if not frequent:
    return pd.DataFrame(columns=["support", "itemsets"])

  return pd.DataFrame(
    {"support": [s for _, s in frequent], "itemsets": [items for items, _ in frequent]}
  ).sort_values("support", ascending=False).reset_index(drop=True)


class Eclat:
  """Association-rules miner using Eclat for frequent itemsets + mlxtend rules."""

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
    self.max_len = None if int(max_len) <= 0 else int(max_len)
    self._frequent_itemsets: pd.DataFrame = pd.DataFrame()
    self._rules: pd.DataFrame = pd.DataFrame()

  def fit(self, X: t.Any, y: t.Any = None, **fit_params: t.Any) -> "Eclat":
    if isinstance(X, pd.DataFrame):
      frame = X.copy()
    else:
      frame = pd.DataFrame(X)

    frame = frame.astype(bool)

    if frame.empty or frame.shape[1] == 0:
      raise ValueError("Eclat requires a non-empty binary item matrix.")

    self._frequent_itemsets = _eclat_frequent_itemsets(frame, self.min_support, self.max_len)

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


ECLAT_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.association.Eclat",
  "class": "Eclat",
  "title": {"en_US": "Eclat", "pt_BR": "Eclat"},
  "description": {
    "en_US": "Finds frequent itemsets with Eclat (vertical tidsets) and derives association rules.",
    "pt_BR": "Encontra itemsets frequentes com Eclat (tidsets verticais) e deriva regras de associação.",
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
