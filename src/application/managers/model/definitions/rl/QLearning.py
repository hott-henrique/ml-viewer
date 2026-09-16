from __future__ import annotations

import typing as t

import numpy as np


class QLearning:
  """Tabular Q-learning agent (select_action / update only; no training loop)."""

  def __init__(self, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.1, **params: t.Any) -> None:
    self.alpha = float(alpha)
    self.gamma = float(gamma)
    self.epsilon = float(epsilon)
    self._q: dict[t.Hashable, dict[t.Hashable, float]] = {}
    self._rng = np.random.default_rng()

  def _ensure_actions(self, state: t.Hashable, legal_actions: t.Sequence[t.Hashable]) -> dict[t.Hashable, float]:
    row = self._q.setdefault(state, {})

    for action in legal_actions:
      row.setdefault(action, 0.0)

    return row

  def select_action(
    self,
    state: t.Any,
    *,
    legal_actions: t.Sequence[t.Any] = (),
    explore: bool = True,
    action_space: t.Any = None,
  ) -> t.Any:
    actions = list(legal_actions)
    if not actions and action_space is not None and hasattr(action_space, "n"):
      actions = list(range(int(action_space.n)))

    if not actions:
      raise ValueError(
        "QLearning requires discrete legal actions (or a Discrete action_space). "
        "For continuous Box actions use REINFORCE."
      )

    row = self._ensure_actions(state, actions)

    if explore and self._rng.random() < self.epsilon:
      return actions[int(self._rng.integers(0, len(actions)))]

    best_value = max(row[a] for a in actions)
    best = [a for a in actions if row[a] == best_value]

    return best[int(self._rng.integers(0, len(best)))]

  def update(self, state: t.Any, action: t.Any, reward: float, next_state: t.Any, *, terminated: bool) -> None:
    row = self._q.setdefault(state, {})
    row.setdefault(action, 0.0)

    if terminated:
      target = float(reward)
    else:
      next_row = self._q.get(next_state, {})
      max_next = max(next_row.values()) if next_row else 0.0
      target = float(reward) + self.gamma * max_next

    row[action] = row[action] + self.alpha * (target - row[action])

  def get_q_table(self) -> dict[t.Hashable, dict[t.Hashable, float]]:
    return {s: dict(actions) for s, actions in self._q.items()}

  def get_params(self) -> dict[str, t.Any]:
    return {
      "alpha": self.alpha,
      "gamma": self.gamma,
      "epsilon": self.epsilon,
    }


QLEARNING_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.rl.QLearning",
  "class": "QLearning",
  "title": {"en_US": "Q-Learning", "pt_BR": "Q-Learning"},
  "description": {
    "en_US": "Tabular Q-learning with ε-greedy exploration (α, γ, ε).",
    "pt_BR": "Q-learning tabular com exploração ε-greedy (α, γ, ε).",
  },
  "params": [
    {
      "name": "alpha",
      "type": "float",
      "default": 0.1,
      "label": {"en_US": "Learning Rate (α)", "pt_BR": "Taxa de aprendizado (α)"},
      "description": {
        "en_US": "Step size for TD updates.",
        "pt_BR": "Tamanho do passo nas atualizações TD.",
      },
    },
    {
      "name": "gamma",
      "type": "float",
      "default": 0.9,
      "label": {"en_US": "Discount (γ)", "pt_BR": "Desconto (γ)"},
      "description": {
        "en_US": "Discount factor for future rewards.",
        "pt_BR": "Fator de desconto para recompensas futuras.",
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
