"""Hyperparameter schema shared by MODEL_CONFIG / ENV_CONFIG / ANALYSIS_CONFIG."""

from __future__ import annotations

import typing as t

from pydantic import BaseModel, ConfigDict, Field

from application.enums import ParamType
from application.i18n import TranslatableStr

# Re-export for plugin authors: `from application.api import ParamType`
__all__ = ["ParamType", "HyperParamConfig"]


class HyperParamConfig(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)

  name: str
  label: TranslatableStr
  type: ParamType
  default: t.Any = None
  options: list[t.Any] = Field(default_factory=list)
  description: TranslatableStr = ""

  field_validation: t.Optional[t.Callable[[t.Any, dict], t.Optional[str]]] = None
