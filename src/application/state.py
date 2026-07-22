class AppState:
  filepath: str = ""
  target_col: str = ""
  train_size: float = 0.8

  problem_type: str = "Classification"
  selected_algorithm: str = "Random Forest"
  hyperparameters: dict = {}

store = AppState()