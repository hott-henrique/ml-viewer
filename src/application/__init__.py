from application.db import init_db

init_db()

# Boot catalogs (models/analyses self-boot on import; environments too).
from application.managers.environment import EnvironmentManager  # noqa: F401
from application.managers.model import ModelManager  # noqa: F401
from application.managers.analysis import AnalysisManager  # noqa: F401

from application.i18n import setup_i18n

setup_i18n()

from application.Application import Application

__all__ = [
  'Application'
]
