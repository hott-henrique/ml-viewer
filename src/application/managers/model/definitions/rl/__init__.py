from application.managers.model.definitions.rl.QLearning import QLEARNING_REGISTRY_INSTANCE

RL_REGISTRY = {
  "Q-Learning": QLEARNING_REGISTRY_INSTANCE,
}

__all__ = [
  "RL_REGISTRY",
]
