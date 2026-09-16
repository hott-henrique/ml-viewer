from __future__ import annotations

import typing as t

import numpy as np


def _features(state: t.Any) -> np.ndarray:
  arr = np.asarray(state, dtype=float).ravel()
  if arr.size == 0:
    return np.zeros(1, dtype=float)
  return arr


class REINFORCE:
  """Episodic REINFORCE (numpy): Discrete softmax or Box diagonal Gaussian."""

  def __init__(
    self,
    gamma: float = 0.99,
    learning_rate: float = 0.01,
    seed: int = 42,
    **params: t.Any,
  ) -> None:
    self.gamma = float(gamma)
    self.learning_rate = float(learning_rate)
    self.seed = int(seed)
    self._rng = np.random.default_rng(self.seed)
    self._W: np.ndarray | None = None  # Discrete: (n_actions, n_features)
    self._mean_W: np.ndarray | None = None  # Box: (act_dim, n_features)
    self._log_std: np.ndarray | None = None
    self._n_actions: int | None = None
    self._act_dim: int | None = None
    self._mode: str | None = None  # "discrete" | "box"
    self._episode: list[tuple[np.ndarray, t.Any, float, float]] = []  # feat, action, reward, log_prob

  def _ensure_discrete(self, n_features: int, n_actions: int) -> None:
    if self._W is None or self._W.shape != (n_actions, n_features):
      self._W = self._rng.normal(0.0, 0.1, size=(n_actions, n_features))
      self._n_actions = n_actions
      self._mode = "discrete"

  def _ensure_box(self, n_features: int, act_dim: int) -> None:
    if self._mean_W is None or self._mean_W.shape != (act_dim, n_features):
      self._mean_W = self._rng.normal(0.0, 0.1, size=(act_dim, n_features))
      self._log_std = np.full(act_dim, -0.5, dtype=float)
      self._act_dim = act_dim
      self._mode = "box"

  def _softmax(self, logits: np.ndarray) -> np.ndarray:
    z = logits - np.max(logits)
    e = np.exp(z)
    return e / (np.sum(e) + 1e-12)

  def select_action(
    self,
    state: t.Any,
    *,
    legal_actions: t.Sequence[t.Any] = (),
    explore: bool = True,
    action_space: t.Any = None,
  ) -> t.Any:
    feat = _features(state)

    if action_space is not None and hasattr(action_space, "n"):
      n_actions = int(action_space.n)
      self._ensure_discrete(feat.size, n_actions)
      assert self._W is not None
      logits = self._W @ feat
      probs = self._softmax(logits)
      if explore:
        action = int(self._rng.choice(n_actions, p=probs))
      else:
        action = int(np.argmax(probs))
      log_prob = float(np.log(probs[action] + 1e-12))
      self._pending = (feat, action, log_prob)
      return action

    if action_space is not None and hasattr(action_space, "shape"):
      act_dim = int(np.prod(action_space.shape))
      self._ensure_box(feat.size, act_dim)
      assert self._mean_W is not None and self._log_std is not None
      mean = self._mean_W @ feat
      std = np.exp(self._log_std)
      if explore:
        action = mean + std * self._rng.normal(size=act_dim)
      else:
        action = mean
      # Gaussian log-prob
      log_prob = float(
        -0.5 * np.sum(((action - mean) / (std + 1e-12)) ** 2 + 2.0 * self._log_std + np.log(2.0 * np.pi))
      )
      low = getattr(action_space, "low", None)
      high = getattr(action_space, "high", None)
      if low is not None and high is not None:
        action = np.clip(action, low.ravel()[:act_dim], high.ravel()[:act_dim])
      shaped = action.reshape(action_space.shape)
      self._pending = (feat, shaped, log_prob)
      return shaped

    # Fallback: legal_actions discrete list (e.g. TicTacToe without gym space.n usage)
    actions = list(legal_actions)
    if not actions:
      raise ValueError("REINFORCE requires action_space (Discrete/Box) or non-empty legal_actions.")

    n_actions = max(int(a) for a in actions) + 1 if all(isinstance(a, (int, np.integer)) for a in actions) else len(actions)
    self._ensure_discrete(feat.size, n_actions)
    assert self._W is not None
    logits = self._W @ feat
    # Mask illegal
    mask = np.full(n_actions, -1e9)
    for a in actions:
      mask[int(a)] = 0.0
    probs = self._softmax(logits + mask)
    if explore:
      action = int(self._rng.choice(n_actions, p=probs))
    else:
      action = int(np.argmax(probs))
    log_prob = float(np.log(probs[action] + 1e-12))
    self._pending = (feat, action, log_prob)
    return action

  def update(self, state: t.Any, action: t.Any, reward: float, next_state: t.Any, *, terminated: bool) -> None:
    pending = getattr(self, "_pending", None)
    if pending is None:
      feat = _features(state)
      log_prob = 0.0
    else:
      feat, _a, log_prob = pending
    self._episode.append((feat, action, float(reward), log_prob))
    self._pending = None

    if not terminated:
      return

    # Returns G_t
    returns: list[float] = []
    g = 0.0
    for _feat, _act, r, _lp in reversed(self._episode):
      g = r + self.gamma * g
      returns.append(g)
    returns.reverse()
    returns_arr = np.asarray(returns, dtype=float)
    if returns_arr.size > 1:
      returns_arr = (returns_arr - returns_arr.mean()) / (returns_arr.std() + 1e-8)

    if self._mode == "discrete" and self._W is not None:
      for (feat, act, _r, log_prob), Gt in zip(self._episode, returns_arr):
        probs = self._softmax(self._W @ feat)
        grad = -probs
        grad[int(act)] += 1.0
        self._W += self.learning_rate * Gt * np.outer(grad, feat)
    elif self._mode == "box" and self._mean_W is not None and self._log_std is not None:
      for (feat, act, _r, _lp), Gt in zip(self._episode, returns_arr):
        a = np.asarray(act, dtype=float).ravel()
        mean = self._mean_W @ feat
        std = np.exp(self._log_std)
        # d log π / d mean = (a - mean) / std^2
        d_mean = (a - mean) / (std ** 2 + 1e-12)
        self._mean_W += self.learning_rate * Gt * np.outer(d_mean, feat)
        # d log π / d log_std ≈ ((a-mean)^2 / std^2 - 1)
        d_log_std = ((a - mean) ** 2) / (std ** 2 + 1e-12) - 1.0
        self._log_std += self.learning_rate * Gt * d_log_std

    self._episode.clear()

  def get_params(self) -> dict[str, t.Any]:
    return {
      "gamma": self.gamma,
      "learning_rate": self.learning_rate,
      "seed": self.seed,
    }


REINFORCE_REGISTRY_INSTANCE = {
  "module": "application.managers.model.definitions.rl.REINFORCE",
  "class": "REINFORCE",
  "title": {"en_US": "REINFORCE", "pt_BR": "REINFORCE"},
  "description": {
    "en_US": "Episodic policy gradient (numpy): softmax for Discrete, diagonal Gaussian for Box.",
    "pt_BR": "Policy gradient episódico (numpy): softmax para Discrete, Gaussiana diagonal para Box.",
  },
  "params": [
    {
      "name": "gamma",
      "type": "float",
      "default": 0.99,
      "label": {"en_US": "Discount (γ)", "pt_BR": "Desconto (γ)"},
      "description": {
        "en_US": "Discount factor for returns.",
        "pt_BR": "Fator de desconto para retornos.",
      },
    },
    {
      "name": "learning_rate",
      "type": "float",
      "default": 0.01,
      "label": {"en_US": "Learning Rate", "pt_BR": "Taxa de aprendizado"},
      "description": {
        "en_US": "Step size for policy parameter updates.",
        "pt_BR": "Tamanho do passo nas atualizações da política.",
      },
    },
    {
      "name": "seed",
      "type": "int",
      "default": 42,
      "label": {"en_US": "Seed", "pt_BR": "Seed"},
      "description": {
        "en_US": "RNG seed for policy initialization and sampling.",
        "pt_BR": "Seed do RNG para inicialização e amostragem da política.",
      },
    },
  ],
}
