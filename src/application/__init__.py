from application.db import init_db

init_db()

from application.i18n import setup_i18n

setup_i18n()

from application.Application import Application

__all__ = [
  'Application'
]
