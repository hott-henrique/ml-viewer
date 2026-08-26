from __future__ import annotations

import typing as t
from dataclasses import dataclass, field


@dataclass(frozen=True)
class StepResult:
  state: t.Hashable
  reward: float
  terminated: bool
  truncated: bool
  info: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Transition:
  state: t.Hashable
  action: t.Hashable
  reward: float
  next_state: t.Hashable
  terminated: bool
  truncated: bool
