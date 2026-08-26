from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from application.managers.environment.base import EnvironmentAPI
from application.managers.environment.types import Transition
from application.managers.model.base import AgentAPI


@dataclass
class TrainConfig:
  n_episodes: int
  seed: int | None = None


@dataclass
class TrainResult:
  transitions: list[Transition] = field(default_factory=list)
  episode_returns: list[float] = field(default_factory=list)


class TrainingRunner:
  """Owns the episode loop and transition history. Agents do not orchestrate training."""

  def run(self, agent: AgentAPI, env: EnvironmentAPI, config: TrainConfig) -> TrainResult:
    if config.n_episodes < 1:
      raise ValueError("n_episodes must be >= 1")

    transitions: list[Transition] = []
    episode_returns: list[float] = []

    for ep in range(config.n_episodes):
      episode_seed = None if config.seed is None else config.seed + ep
      s = env.reset(seed=episode_seed)
      G = 0.0

      while True:
        legal = env.legal_actions(s)
        a = agent.select_action(s, legal_actions=legal, explore=True)
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
        s = step.state

        if step.terminated or step.truncated:
          break

      episode_returns.append(G)

    return TrainResult(transitions=transitions, episode_returns=episode_returns)
