from application.managers.environment.definitions.TicTacToe import TIC_TAC_TOE_REGISTRY_INSTANCE

ENV_KIND_REGISTRY: dict[str, dict] = {
  "tic_tac_toe": TIC_TAC_TOE_REGISTRY_INSTANCE,
}

__all__ = [
  "ENV_KIND_REGISTRY",
]
