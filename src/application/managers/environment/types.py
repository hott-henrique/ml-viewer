from __future__ import annotations

import typing as t
from dataclasses import dataclass, field


@dataclass(frozen=True)
class StepResult:
  state: t.Any
  reward: float
  terminated: bool
  truncated: bool
  info: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Transition:
  state: t.Any
  action: t.Any
  reward: float
  next_state: t.Any
  terminated: bool
  truncated: bool
