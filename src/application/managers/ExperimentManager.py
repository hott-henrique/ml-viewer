import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_FILE = os.path.join(BASE_DIR, "experiments_metadata.json")

class ExperimentManager:
  @classmethod
  def get_all(cls) -> list[dict]:
    if os.path.exists(EXPERIMENTS_FILE):
      with open(EXPERIMENTS_FILE, "r", encoding="utf-8") as f:
        try:
          return json.load(f)
        except json.JSONDecodeError:
          return []
    return []

  @classmethod
  def add_experiment(cls, name: str, dataset: dict, model_name: str, hyperparams: dict, status: str = "Pending", results: str = "") -> dict:
    experiments = cls.get_all()

    new_exp = {
      "id": str(len(experiments) + 1),
      "name": name,
      "dataset": dataset,
      "dataset_name": dataset.get("name", "Unknown"),
      "problem_type": dataset.get("type", ""),
      "model_name": model_name,
      "hyperparameters": hyperparams,
      "status": status,
      "results": results,
      "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    experiments.append(new_exp)

    cls._save_all(experiments)

    return new_exp

  @classmethod
  def update_experiment(cls, exp_id: str, updates: dict):
    experiments = cls.get_all()

    for exp in experiments:
      if str(exp["id"]) == str(exp_id):
        exp.update(updates)
        break

    cls._save_all(experiments)

  @classmethod
  def delete_experiment(cls, target_id: str):
    experiments = [e for e in cls.get_all() if str(e["id"]) != str(target_id)]
    cls._save_all(experiments)

  @classmethod
  def _save_all(cls, experiments):
    with open(EXPERIMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(experiments, f, indent=4)