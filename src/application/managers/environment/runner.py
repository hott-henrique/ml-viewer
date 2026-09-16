from __future__ import annotations

import time
import typing as t
from dataclasses import dataclass, field

from application.managers.environment.base import EnvironmentAPI
from application.managers.environment.types import Transition
from application.managers.model.base import AgentAPI


@dataclass
class TrainConfig:
  n_episodes: int
  seed: int | None = None
  watch_during: bool = True
  watch_last_episodes: int = 5
  watch_delay_ms: int = 100


@dataclass
class TrainResult:
  transitions: list[Transition] = field(default_factory=list)
  episode_returns: list[float] = field(default_factory=list)


StepCallback = t.Callable[
  [int, int, t.Any, t.Any, t.Any, t.Any | None],
  t.Any,
]


class TrainingRunner:
  """Owns the episode loop and transition history. Agents do not orchestrate training."""

  def run(
    self,
    agent: AgentAPI,
    env: EnvironmentAPI,
    config: TrainConfig,
    *,
    on_step: StepCallback | None = None,
  ) -> TrainResult:
    if config.n_episodes < 1:
      raise ValueError("n_episodes must be >= 1")

    transitions: list[Transition] = []
    episode_returns: list[float] = []
    watch_start = max(0, config.n_episodes - max(0, int(config.watch_last_episodes)))
    watch_enabled = bool(config.watch_during) and on_step is not None

    for ep in range(config.n_episodes):
      episode_seed = None if config.seed is None else config.seed + ep
      s = env.reset(seed=episode_seed)
      G = 0.0
      step_idx = 0
      watching = watch_enabled and ep >= watch_start

      while True:
        legal = env.legal_actions(s)
        space = getattr(env, "action_space", None)
        a = agent.select_action(s, legal_actions=legal, explore=True, action_space=space)
        step = env.step(a)
        agent.update(s, a, step.reward, step.state, terminated=step.terminated)
        transitions.append(
          Transition(
            state=s,
            action=a,
            reward=step.reward,
            next_state=step.state,
            terminated=step.terminated,
            truncated=step.truncated,
          )
        )
        G += step.reward

        if watching:
          frame = None
          if hasattr(env, "render_frame"):
            try:
              frame = env.render_frame()
            except Exception:
              frame = None
          cont = on_step(ep, step_idx, step.state, a, step, frame)
          if cont is False:
            watching = False
            watch_enabled = False
          elif config.watch_delay_ms > 0:
            time.sleep(config.watch_delay_ms / 1000.0)

        s = step.state
        step_idx += 1

        if step.terminated or step.truncated:
          break

      episode_returns.append(G)

    return TrainResult(transitions=transitions, episode_returns=episode_returns)
