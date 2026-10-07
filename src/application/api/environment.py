"""Environment Protocol for RL plugins."""

from __future__ import annotations

import typing as t

from application.api.types import StepResult


class EnvironmentAPI(t.Protocol):
  @property
  def id(self) -> str:
    ...

  @property
  def observation_space(self) -> t.Any:
    ...

  @property
  def action_space(self) -> t.Any:
    ...

  def reset(self, *, seed: int | None = None) -> t.Any:
    """Initial state s0."""
    ...

  def step(self, action: t.Any) -> StepResult:
    """Return (s', r, terminated, truncated, info)."""
    ...

  def legal_actions(self, state: t.Any = None) -> t.Sequence[t.Any]:
    """Legal actions for the current or explicit state. Empty for continuous action spaces."""
    ...

  def render_frame(self) -> t.Any | None:
    """Optional RGB HxWx3 uint8 array for the watch UI; None shows state as text."""
    ...
