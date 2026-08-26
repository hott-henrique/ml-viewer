from pathlib import Path

import platformdirs

APP_NAME = "ml-viewer"

def get_data_dir() -> Path:
  data_dir = Path(platformdirs.user_data_dir(APP_NAME))
  data_dir.mkdir(parents=True, exist_ok=True)

  for subdir in ("datasets", "models", "experiments", "analyses", "environments"):
    (data_dir / subdir).mkdir(parents=True, exist_ok=True)

  return data_dir

def get_datasets_dir() -> Path:
  return get_data_dir() / "datasets"

def get_models_dir() -> Path:
  return get_data_dir() / "models"

def get_analyses_dir() -> Path:
  return get_data_dir() / "analyses"

def get_environments_dir() -> Path:
  return get_data_dir() / "environments"

def get_experiments_dir() -> Path:
  return get_data_dir() / "experiments"

def get_experiment_dir(experiment_id: int) -> Path:
  """Returns the per-experiment subfolder that holds that experiment's trained model pickle."""
  experiment_dir = get_experiments_dir() / str(experiment_id)
  experiment_dir.mkdir(parents=True, exist_ok=True)

  return experiment_dir

def get_db_path() -> Path:
  return get_data_dir() / "app.db"
