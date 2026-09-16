from application.managers.model.definitions.rl.QLearning import QLEARNING_REGISTRY_INSTANCE
from application.managers.model.definitions.rl.MonteCarlo import MONTE_CARLO_REGISTRY_INSTANCE
from application.managers.model.definitions.rl.REINFORCE import REINFORCE_REGISTRY_INSTANCE

RL_REGISTRY = {
  "Q-Learning": QLEARNING_REGISTRY_INSTANCE,
  "Monte Carlo": MONTE_CARLO_REGISTRY_INSTANCE,
  "REINFORCE": REINFORCE_REGISTRY_INSTANCE,
}

__all__ = [
  "RL_REGISTRY",
]
