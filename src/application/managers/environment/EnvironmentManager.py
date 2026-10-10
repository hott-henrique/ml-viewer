from __future__ import annotations

import importlib
import importlib.util
import sys
import typing as t
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from application.db.database import SessionLocal
from application.db.models import AgentEnvironmentCompat as CompatRow
from application.db.models import Environment as EnvironmentRow
from application.db.paths import get_environments_dir
from application.db.storage import FileStore, delete_file, save_file_groups
from application.i18n import TranslatableStr, _
from application.api.params import HyperParamConfig
from application.managers.environment.base import EnvironmentAPI
from application.managers.environment.definitions import ENV_KIND_REGISTRY

# Seed pairs: (agent model name, env kind)
NATIVE_COMPAT_SEED: list[tuple[str, str]] = [
  ("Q-Learning", "tic_tac_toe"),
  ("Monte Carlo", "tic_tac_toe"),
  ("REINFORCE", "tic_tac_toe"),
  ("Q-Learning", "gymnasium"),
  ("Monte Carlo", "gymnasium"),
  ("REINFORCE", "gymnasium"),
]

ENVIRONMENTS_DIR = get_environments_dir()


class EnvironmentKindConfig(BaseModel):
  model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

  class_name: str = Field(..., alias="class")
  title: t.Optional[TranslatableStr] = None
  description: TranslatableStr = ""
  params: list[HyperParamConfig] = Field(default_factory=list)
  module: t.Optional[str] = None
  custom_module: t.Optional[t.Any] = None
  plugin_path: t.Optional[str] = None
  is_native: bool = False

@dataclass(frozen=True)
class EnvironmentVersion:
  id: int
  name: str
  version: int
  md5_hash: t.Optional[str]
  is_native: bool
  title: t.Optional[TranslatableStr]
  params: list[HyperParamConfig]

class EnvironmentManager:
  BASE_ENV_REGISTRY: dict[str, EnvironmentKindConfig] = {}

  @staticmethod
  def registry() -> dict[str, EnvironmentKindConfig]:
    return EnvironmentManager.BASE_ENV_REGISTRY

  @staticmethod
  def kind_options() -> list[str]:
    return list(EnvironmentManager.BASE_ENV_REGISTRY.keys())

  @staticmethod
  def kind_config(kind: str) -> EnvironmentKindConfig:
    config = EnvironmentManager.BASE_ENV_REGISTRY.get(kind)
    if config is None:
      raise ValueError(_("environment.err.unknown_kind").format(kind=kind))
    return config

  @staticmethod
  def _load_module_from_path(filepath: str) -> t.Any:
    module_name = Path(filepath).stem
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
      raise ImportError(f"Could not load the file: {filepath}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

  @classmethod
  def _seed_native_environments(cls, session: Session) -> None:
    has_any = session.scalar(select(EnvironmentRow.id).limit(1)) is not None
    if has_any:
      return

    for name, data in ENV_KIND_REGISTRY.items():
      try:
        config = EnvironmentKindConfig.model_validate(data)
      except Exception as e:
        print(f"Warning: Native environment '{name}' failed validation: {e}")
        continue

      session.add(EnvironmentRow(
        name=name,
        class_name=config.class_name,
        module=config.module,
        title=config.title,
        description=config.description,
        params=[p.model_dump(mode="json") for p in config.params],
        is_native=True,
        version=1,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      ))

    session.commit()

  @classmethod
  def _seed_compat(cls, session: Session) -> None:
    has_any = session.scalar(select(CompatRow.id).limit(1)) is not None
    if has_any:
      return

    for agent, env in NATIVE_COMPAT_SEED:
      session.add(CompatRow(agent=agent, env=env))
    session.commit()

  @classmethod
  def _register_row_in_memory(cls, row: EnvironmentRow) -> None:
    custom_module: t.Optional[t.Any] = None
    plugin_path: t.Optional[str] = None

    if not row.is_native:
      store = FileStore(ENVIRONMENTS_DIR)
      if not row.storage_filename or not row.md5_hash or not store.verify_integrity(row.storage_filename, row.md5_hash):
        print(f"Warning: Plugin environment '{row.name}' failed integrity check, skipping.")
        return
      plugin_path = str(store.resolve_path(row.storage_filename))
      custom_module = cls._load_module_from_path(plugin_path)

    title: t.Optional[TranslatableStr] = row.title
    description: TranslatableStr = row.description or ""
    params = [HyperParamConfig.model_validate(p) for p in (row.params or [])]

    if row.is_native:
      native_data = ENV_KIND_REGISTRY.get(row.name)
      if native_data is not None:
        title = native_data.get("title", title)
        description = native_data.get("description", description)
        params = [HyperParamConfig.model_validate(p) for p in native_data.get("params", [])]

    config = EnvironmentKindConfig(
      **{
        "class": row.class_name,
        "title": title,
        "description": description,
        "params": params,
        "module": row.module,
        "custom_module": custom_module,
        "plugin_path": plugin_path,
        "is_native": row.is_native,
      }
    )
    cls.BASE_ENV_REGISTRY[row.name] = config

  @classmethod
  def boot_environments(cls) -> None:
    cls.BASE_ENV_REGISTRY = {}
    with SessionLocal() as session:
      cls._seed_native_environments(session)
      cls._seed_compat(session)
      rows = session.scalars(select(EnvironmentRow).order_by(EnvironmentRow.version)).all()
      for row in rows:
        cls._register_row_in_memory(row)

  @classmethod
  def list_versions(cls) -> list[EnvironmentVersion]:
    with SessionLocal() as session:
      rows = session.scalars(select(EnvironmentRow).order_by(EnvironmentRow.name, EnvironmentRow.version)).all()

      versions: list[EnvironmentVersion] = []

      for row in rows:
        title: t.Optional[TranslatableStr] = row.title
        params = [HyperParamConfig.model_validate(p) for p in (row.params or [])]

        if row.is_native:
          native_data = ENV_KIND_REGISTRY.get(row.name)

          if native_data is not None:
            title = native_data.get("title", title)
            params = [HyperParamConfig.model_validate(p) for p in native_data.get("params", [])]

        versions.append(EnvironmentVersion(
          id=row.id,
          name=row.name,
          version=row.version,
          md5_hash=row.md5_hash,
          is_native=row.is_native,
          title=title,
          params=params,
        ))

      return versions

  @classmethod
  def import_from_file(cls, filepath: str) -> list[str]:
    module = cls._load_module_from_path(filepath)

    if not hasattr(module, "ENV_CONFIG"):
      raise ValueError("The imported file must contain an 'ENV_CONFIG' dictionary.")

    custom_config = getattr(module, "ENV_CONFIG")

    if not isinstance(custom_config, dict):
      raise ValueError("'ENV_CONFIG' must be a dictionary.")

    pending: list[tuple[str, EnvironmentKindConfig, int, str | None]] = []

    with SessionLocal() as session:
      for env_name, env_data in custom_config.items():
        try:
          raw = dict(env_data)
          raw.pop("compatible_agents", None)
          config = EnvironmentKindConfig.model_validate(raw)

          if not hasattr(module, config.class_name):
            raise ValueError(
              f"Environment class '{config.class_name}' not found in the imported file."
            )

          latest = session.scalar(
            select(EnvironmentRow)
            .where(EnvironmentRow.name == env_name)
            .order_by(EnvironmentRow.version.desc())
            .limit(1)
          )
          version = 1 if latest is None else latest.version + 1
          previous_key = None if latest is None else latest.logical_key
          pending.append((env_name, config, version, previous_key))
        except Exception as e:
          print(f"Warning: Custom environment '{env_name}' rejected due to validation error: {e}")

    if not pending:
      raise ValueError(_("environment.err.import_none_added"))

    saved_by_key = save_file_groups(filepath, [item[3] for item in pending], "environments")
    added: list[str] = []

    with SessionLocal() as session:
      for env_name, config, version, previous_key in pending:
        stored = saved_by_key[previous_key]
        session.add(EnvironmentRow(
          name=env_name,
          class_name=config.class_name,
          module=None,
          title=config.title,
          description=config.description,
          params=[p.model_dump(mode="json") for p in config.params],
          storage_filename=stored.storage_filename,
          original_filename=stored.original_filename,
          md5_hash=stored.md5_hash,
          size_bytes=stored.size_bytes,
          logical_key=stored.key,
          version=version,
          is_native=False,
          created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        added.append(env_name)

      session.commit()

    cls.boot_environments()
    return added

  @classmethod
  def delete_environment(cls, environment_id: int) -> None:
    with SessionLocal() as session:
      row = session.get(EnvironmentRow, environment_id)

      if row is None:
        return

      if row.is_native:
        raise ValueError(_("environment.err.native_cannot_delete"))

      storage_filename = row.storage_filename
      logical_key = row.logical_key
      name = row.name
      session.delete(row)
      session.commit()

      still_used = False

      if logical_key:
        still_used = session.scalar(
          select(EnvironmentRow.id).where(EnvironmentRow.logical_key == logical_key)
        ) is not None

      name_remains = session.scalar(
        select(EnvironmentRow.id).where(EnvironmentRow.name == name)
      ) is not None

      if not name_remains:
        session.execute(delete(CompatRow).where(CompatRow.env == name))
        session.commit()

    if logical_key and not still_used:
      delete_file(logical_key)
    elif storage_filename and not logical_key:
      FileStore(ENVIRONMENTS_DIR).delete(storage_filename)

    cls.boot_environments()

  @classmethod
  def instantiate(cls, kind: str, params: t.Optional[dict[str, t.Any]] = None) -> EnvironmentAPI:
    config = cls.kind_config(kind)
    if config.module:
      module = importlib.import_module(config.module)
      env_cls = getattr(module, config.class_name)
    elif config.custom_module:
      env_cls = getattr(config.custom_module, config.class_name)
    else:
      raise ValueError(f"Configuration for '{kind}' must have either 'module' or a local class.")
    return env_cls(**(params or {}))

  # Backward-compatible alias used by older call sites.
  instantiate_kind = instantiate

  @classmethod
  def agents_for_env(cls, env_kind: str) -> list[str]:
    with SessionLocal() as session:
      rows = session.scalars(
        select(CompatRow.agent).where(CompatRow.env == env_kind).order_by(CompatRow.agent)
      ).all()
      return list(rows)

  @classmethod
  def envs_for_agent(cls, agent_name: str) -> list[str]:
    with SessionLocal() as session:
      rows = session.scalars(
        select(CompatRow.env).where(CompatRow.agent == agent_name).order_by(CompatRow.env)
      ).all()
      return list(rows)

  @classmethod
  def set_compat_for_agent(cls, agent_name: str, env_kinds: t.Sequence[str]) -> None:
    kinds = [str(k) for k in env_kinds]
    if not kinds:
      raise ValueError(_("environment.err.compat_need_one"))

    known = set(cls.kind_options())
    unknown = [k for k in kinds if k not in known]
    if unknown:
      raise ValueError(
        _("environment.err.unknown_kind").format(kind=", ".join(unknown))
      )

    with SessionLocal() as session:
      session.execute(delete(CompatRow).where(CompatRow.agent == agent_name))
      for env in kinds:
        session.add(CompatRow(agent=agent_name, env=env))
      session.commit()

  @classmethod
  def clear_compat_for_agent(cls, agent_name: str) -> None:
    with SessionLocal() as session:
      session.execute(delete(CompatRow).where(CompatRow.agent == agent_name))
      session.commit()

  @classmethod
  def assert_compatible(cls, env_kind: str, agent_name: str) -> None:
    allowed = cls.agents_for_env(env_kind)
    if agent_name not in allowed:
      raise ValueError(
        _("environment.err.incompatible_agent").format(agent=agent_name, env=env_kind)
      )

  # Kept for callers that still invoke seed_compat explicitly.
  @classmethod
  def seed_compat(cls) -> None:
    with SessionLocal() as session:
      cls._seed_compat(session)


EnvironmentManager.boot_environments()
