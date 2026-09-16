from __future__ import annotations

import typing as t

import numpy as np

from application.managers.environment.types import StepResult

try:
  import gymnasium as gym
  from gymnasium import spaces
except ImportError as exc:  # pragma: no cover
  raise ImportError(
    "Gymnasium is required for GymnasiumEnv. Install with: pip install gymnasium"
  ) from exc


def _is_discrete(space: t.Any) -> bool:
  return isinstance(space, spaces.Discrete)


def _is_box(space: t.Any) -> bool:
  return isinstance(space, spaces.Box)


def _discretize_box(obs: np.ndarray, space: spaces.Box, n_bins: int) -> tuple[int, ...]:
  flat = np.asarray(obs, dtype=float).ravel()
  low = np.asarray(space.low, dtype=float).ravel()
  high = np.asarray(space.high, dtype=float).ravel()
  # Clip infinite bounds to a wide finite range for binning.
  low = np.where(np.isfinite(low), low, -10.0)
  high = np.where(np.isfinite(high), high, 10.0)
  high = np.where(high <= low, low + 1.0, high)
  scaled = (flat - low) / (high - low)
  scaled = np.clip(scaled, 0.0, 1.0 - 1e-9)
  bins = np.floor(scaled * n_bins).astype(int)
  bins = np.clip(bins, 0, n_bins - 1)
  return tuple(int(b) for b in bins.tolist())


class GymnasiumEnv:
  """Wraps gymnasium.make(env_id) as EnvironmentAPI (Discrete or Box actions)."""

  def __init__(
    self,
    env_id: str = "CartPole-v1",
    n_bins: int = 10,
    discretize_obs: bool = False,
    **params: t.Any,
  ) -> None:
    self.env_id = str(env_id)
    self.n_bins = max(2, int(n_bins))
    self.discretize_obs = bool(discretize_obs)
    self._env = gym.make(self.env_id, render_mode="rgb_array")
    self._obs: t.Any = None

    if not (_is_discrete(self._env.action_space) or _is_box(self._env.action_space)):
      self._env.close()
      raise ValueError(
        f"GymnasiumEnv only supports Discrete or Box action spaces; got {self._env.action_space}"
      )

  @property
  def id(self) -> str:
    return f"gymnasium:{self.env_id}"

  @property
  def action_space(self) -> t.Any:
    return self._env.action_space

  @property
  def observation_space(self) -> t.Any:
    return self._env.observation_space

  def _encode_obs(self, obs: t.Any) -> t.Any:
    if self.discretize_obs and _is_box(self._env.observation_space):
      return _discretize_box(np.asarray(obs), self._env.observation_space, self.n_bins)
    if _is_discrete(self._env.observation_space):
      return int(obs)
    return np.asarray(obs, dtype=float)

  def reset(self, *, seed: int | None = None) -> t.Any:
    obs, _info = self._env.reset(seed=seed)
    self._obs = obs
    return self._encode_obs(obs)

  def legal_actions(self, state: t.Any = None) -> list[t.Any]:
    space = self._env.action_space
    if _is_discrete(space):
      return list(range(int(space.n)))
    return []

  def render_frame(self) -> t.Any | None:
    frame = self._env.render()
    if frame is None:
      return None
    return np.asarray(frame)

  def step(self, action: t.Any) -> StepResult:
    if _is_discrete(self._env.action_space):
      action = int(action)
    else:
      action = np.asarray(action, dtype=np.float32)

    obs, reward, terminated, truncated, info = self._env.step(action)
    self._obs = obs
    return StepResult(
      state=self._encode_obs(obs),
      reward=float(reward),
      terminated=bool(terminated),
      truncated=bool(truncated),
      info=dict(info or {}),
    )

  def close(self) -> None:
    self._env.close()


GYMNASIUM_REGISTRY_INSTANCE = {
  "module": "application.managers.environment.definitions.GymnasiumEnv",
  "class": "GymnasiumEnv",
  "title": {"en_US": "Gymnasium", "pt_BR": "Gymnasium"},
  "description": {
    "en_US": "Any Gymnasium environment via env_id (Discrete or Box actions). Optional obs binning for tabular agents.",
    "pt_BR": "Qualquer ambiente Gymnasium via env_id (ações Discrete ou Box). Binning opcional de obs para agentes tabulares.",
  },
  "params": [
    {
      "name": "env_id",
      "type": "string",
      "default": "CartPole-v1",
      "label": {"en_US": "Environment ID", "pt_BR": "ID do ambiente"},
      "description": {
        "en_US": "Gymnasium environment id passed to gym.make (e.g. CartPole-v1, Pendulum-v1).",
        "pt_BR": "ID do ambiente Gymnasium passado a gym.make (ex.: CartPole-v1, Pendulum-v1).",
      },
    },
    {
      "name": "discretize_obs",
      "type": "bool",
      "default": False,
      "label": {"en_US": "Discretize observations", "pt_BR": "Discretizar observações"},
      "description": {
        "en_US": "Bin Box observations into tuples for tabular agents (Q-Learning / Monte Carlo).",
        "pt_BR": "Discretiza observações Box em tuplas para agentes tabulares (Q-Learning / Monte Carlo).",
      },
    },
    {
      "name": "n_bins",
      "type": "int",
      "default": 10,
      "label": {"en_US": "Bins per dim", "pt_BR": "Bins por dimensão"},
      "description": {
        "en_US": "Number of bins per observation dimension when discretize_obs is True.",
        "pt_BR": "Número de bins por dimensão da observação quando discretize_obs é verdadeiro.",
      },
    },
  ],
}
