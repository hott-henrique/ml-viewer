from __future__ import annotations

import typing as t

from application.managers.environment.types import StepResult


class EnvironmentAPI(t.Protocol):
  @property
  def id(self) -> str:
    ...

  def reset(self, *, seed: int | None = None) -> t.Hashable:
    """Initial state s0."""
    ...

  def step(self, action: t.Hashable) -> StepResult:
    """Return (s', r, terminated, truncated, info)."""
    ...

  def legal_actions(self, state: t.Hashable | None = None) -> t.Sequence[t.Hashable]:
    """Legal actions for the current or explicit state."""
    ...
