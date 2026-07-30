import json
import os
import typing as t
from datetime import datetime
from pydantic import BaseModel

from application.enums import ExperimentStatus, ProblemType
from application.managers.DatasetManager import DatasetMetadata

class ExperimentMetadata(BaseModel):
  id: str
  name: str
  dataset: DatasetMetadata
  dataset_name: str
  problem_type: ProblemType
  model_name: str
  hyperparameters: dict[str, t.Any]
  status: ExperimentStatus
  results: str
  date: str

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_FILE = os.path.join(BASE_DIR, "experiments_metadata.json")

class ExperimentManager:

  @classmethod
  def get_all(cls) -> list[ExperimentMetadata]:
    if os.path.exists(EXPERIMENTS_FILE):
      with open(EXPERIMENTS_FILE, "r", encoding="utf-8") as f:
        try:
          data = json.load(f)

          return [ExperimentMetadata.model_validate(exp) for exp in data]
        except (json.JSONDecodeError, ValueError) as e:
          print(f"Warning: Failed to parse experiments JSON: {e}")
          return []
    return []

  @classmethod
  def add_experiment(cls,
                     name: str,
                     dataset: DatasetMetadata,
                     model_name: str,
                     hyperparams: dict,
                     status: ExperimentStatus = ExperimentStatus.PENDING,
                     results: str = "") -> ExperimentMetadata:
    experiments = cls.get_all()

    new_exp = ExperimentMetadata(
      id=str(len(experiments) + 1),
      name=name,
      dataset=dataset,
      dataset_name=dataset.name,
      problem_type=dataset.type,
      model_name=model_name,
      hyperparameters=hyperparams,
      status=status,
      results=results,
      date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    experiments.append(new_exp)

    cls._save_all(experiments)

    return new_exp

  @classmethod
  def update_experiment(cls, exp_id: str, updates: dict) -> ExperimentMetadata:
    experiments = cls.get_all()
    
    for i, exp in enumerate(experiments):
      if exp.id == str(exp_id):
        valid_updates = {k: v for k, v in updates.items() if k in ExperimentMetadata.model_fields and v is not None}

        updated_exp = exp.model_copy(update=valid_updates)

        experiments[i] = updated_exp
        cls._save_all(experiments)
        return updated_exp

    raise ValueError(f"Experimento com ID {exp_id} não encontrado.")

  @classmethod
  def delete_experiment(cls, target_id: str):
    experiments = cls.get_all()

    updated_experiments = [e for e in experiments if e.id != str(target_id)]

    cls._save_all(updated_experiments)

  @classmethod
  def _save_all(cls, experiments: list[ExperimentMetadata]):
    with open(EXPERIMENTS_FILE, "w", encoding="utf-8") as f:
      json.dump([exp.model_dump(mode='json') for exp in experiments], f, indent=4)