from __future__ import annotations

import typing as t

import numpy as np


class MonteCarlo:
  """Tabular every-visit Monte Carlo control (ε-greedy); episode buffer until terminated."""

  def __init__(self, gamma: float = 0.9, epsilon: float = 0.1, **params: t.Any) -> None:
    self.gamma = float(gamma)
    self.epsilon = float(epsilon)
    self._q: dict[t.Hashable, dict[t.Hashable, float]] = {}
    self._counts: dict[t.Hashable, dict[t.Hashable, int]] = {}
    self._episode: list[tuple[t.Hashable, t.Hashable, float]] = []
    self._rng = np.random.default_rng()

  def _ensure_actions(self, state: t.Hashable, legal_actions: t.Sequence[t.Hashable]) -> dict[t.Hashable, float]:
    row = self._q.setdefault(state, {})
    self._counts.setdefault(state, {})

    for action in legal_actions:
      row.setdefault(action, 0.0)
      self._counts[state].setdefault(action, 0)

    return row

  def select_action(self, state: t.Hashable, *, legal_actions: t.Sequence[t.Hashable], explore: bool = True) -> t.Hashable:
    actions = list(legal_actions)

    if not actions:
      raise ValueError("MonteCarlo.select_action requires at least one legal action.")

    row = self._ensure_actions(state, actions)

    if explore and self._rng.random() < self.epsilon:
      return actions[int(self._rng.integers(0, len(actions)))]

    best_value = max(row[a] for a in actions)
    best = [a for a in actions if row[a] == best_value]

    return best[int(self._rng.integers(0, len(best)))]

  def update(self, state: t.Hashable, action: t.Hashable, reward: float, next_state: t.Hashable, *, terminated: bool) -> None:
    self._q.setdefault(state, {}).setdefault(action, 0.0)
    self._counts.setdefault(state, {}).setdefault(action, 0)
    self._episode.append((state, action, float(reward)))

    if not terminated:
      return

    g = 0.0
    for s, a, r in reversed(self._episode):
      g = r + self.gamma * g
      count = self._counts[s][a] + 1
      self._counts[s][a] = count
      q_sa = self._q[s][a]
      self._q[s][a] = q_sa + (g - q_sa) / count

    self._episode.clear()

  def get_q_table(self) -> dict[t.Hashable, dict[t.Hashable, float]]:
    return {s: dict(actions) for s, actions in self._q.items()}

  def get_params(self) -> dict[str, t.Any]:
    return {
      "gamma": self.gamma,
      "epsilon": self.epsilon,
    }


MONTE_CARLO_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.rl.MonteCarlo",
  "class": "MonteCarlo",
  "title": {"en_US": "Monte Carlo", "pt_BR": "Monte Carlo"},
  "description": {
    "en_US": "Tabular every-visit Monte Carlo control with ε-greedy exploration (γ, ε).",
    "pt_BR": "Monte Carlo tabular every-visit com exploração ε-greedy (γ, ε).",
  },
  "params": [
    {
      "name": "gamma",
      "type": "float",
      "default": 0.9,
      "label": {"en_US": "Discount (γ)", "pt_BR": "Desconto (γ)"},
      "description": {
        "en_US": "Discount factor for returns.",
        "pt_BR": "Fator de desconto para retornos.",
      },
    },
    {
      "name": "epsilon",
      "type": "float",
      "default": 0.1,
      "label": {"en_US": "Exploration (ε)", "pt_BR": "Exploração (ε)"},
      "description": {
        "en_US": "Probability of choosing a random legal action.",
        "pt_BR": "Probabilidade de escolher uma ação legal aleatória.",
      },
    },
  ],
}
