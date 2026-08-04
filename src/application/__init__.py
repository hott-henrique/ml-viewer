from application.db import init_db

init_db()

from application.Application import Application

__all__ = [
  'Application'
]
