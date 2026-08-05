"""Internationalization helpers: gettext for free-text UI strings plus a stable-code
catalog (`i18n_catalog.MESSAGES`) for error messages and other programmatically
referenced strings, and per-record TranslatableStr fields (title/description/label).

Plugin authors (custom models / analyses) can read the active UI locale without
importing this module and without changing `fit` / `predict` / `analyze` signatures:

    import os
    locale = os.environ.get("ML_VIEWER_LOCALE", "en_US")  # "en_US" | "pt_BR"

Prefer static `title` / `description` / `label` as ``str | dict[locale, text]`` when
possible; use ``ML_VIEWER_LOCALE`` for dynamic runtime strings only.
"""

from __future__ import annotations

import gettext
import json
import os
import typing as t
from pathlib import Path

from application.db.paths import get_data_dir
from application.i18n_catalog import ENGLISH_TO_CODE, MESSAGES

DOMAIN = "ml-viewer"
SUPPORTED_LOCALES = ("en_US", "pt_BR")
DEFAULT_LOCALE = "en_US"
LOCALE_ENV_VAR = "ML_VIEWER_LOCALE"

LOCALE_LABELS: dict[str, str] = {
  "en_US": "English (US)",
  "pt_BR": "Português (BR)",
}

# A TranslatableStr is either a plain string (legacy / user-provided text, shown as-is)
# or a dict mapping locale codes (e.g. "en_US", "pt_BR") to localized text.
TranslatableStr = str | dict[str, str]

_current_locale: str = DEFAULT_LOCALE
_translator: gettext.NullTranslations = gettext.NullTranslations()


def _locales_dir() -> Path:
  """Resolve locales directory: src/application/locales or repo locales/."""
  package_locales = Path(__file__).resolve().parent / "locales"
  if package_locales.is_dir():
    return package_locales

  repo_locales = Path(__file__).resolve().parents[2] / "locales"
  return repo_locales


def _settings_path() -> Path:
  return get_data_dir() / "settings.json"


def load_saved_locale() -> str:
  path = _settings_path()

  if not path.exists():
    return DEFAULT_LOCALE

  try:
    data = json.loads(path.read_text(encoding="utf-8"))
    locale = data.get("locale", DEFAULT_LOCALE)
    return locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
  except Exception:
    return DEFAULT_LOCALE


def save_locale(locale: str) -> None:
  if locale not in SUPPORTED_LOCALES:
    raise ValueError(f"Unsupported locale: {locale}")

  path = _settings_path()
  data: dict[str, t.Any] = {}

  if path.exists():
    try:
      data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
      data = {}

  data["locale"] = locale
  path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def setup_i18n(locale: str | None = None) -> str:
  """Install gettext translations for the given (or saved) locale. Returns active locale."""
  global _current_locale, _translator

  chosen = locale or load_saved_locale()

  if chosen not in SUPPORTED_LOCALES:
    chosen = DEFAULT_LOCALE

  locales_dir = _locales_dir()

  try:
    _translator = gettext.translation(
      DOMAIN,
      localedir=str(locales_dir),
      languages=[chosen],
      fallback=True,
    )
  except Exception:
    _translator = gettext.NullTranslations()

  _current_locale = chosen
  # Expose locale to custom model/analysis plugins without requiring app imports.
  os.environ[LOCALE_ENV_VAR] = chosen
  return _current_locale


def get_locale() -> str:
  return _current_locale


def set_locale(locale: str) -> str:
  """Persist and activate a locale. Returns the active locale code."""
  if locale not in SUPPORTED_LOCALES:
    raise ValueError(f"Unsupported locale: {locale}")

  save_locale(locale)
  return setup_i18n(locale)


def resolve_text(value: TranslatableStr | None, locale: str | None = None) -> str:
  """Resolve a TranslatableStr to plain text for the given (or current) locale.

  Plain strings are returned as-is (legacy / user-provided free text). Dicts are
  resolved to the requested locale, falling back to en_US, then to any value present.
  """
  if not value:
    return ""

  if isinstance(value, str):
    return value

  chosen = locale or _current_locale

  if chosen in value and value[chosen]:
    return value[chosen]

  if DEFAULT_LOCALE in value and value[DEFAULT_LOCALE]:
    return value[DEFAULT_LOCALE]

  for text in value.values():
    if text:
      return text

  return ""


def display_title(title: TranslatableStr | None, fallback: str) -> str:
  """Resolve a TranslatableStr title, falling back to a plain identifier (e.g. registry key)."""
  resolved = resolve_text(title)
  return resolved or fallback


def _(message: str) -> str:
  """Translate a message.

  If `message` is a stable code present in the `i18n_catalog.MESSAGES` catalog, resolve
  it directly from the catalog for the active locale. Otherwise, fall back to the legacy
  gettext (.po/.mo) lookup, keyed by the English source text.
  """
  if message in MESSAGES:
    return MESSAGES[message].get(_current_locale) or MESSAGES[message].get(DEFAULT_LOCALE, message)

  return _translator.gettext(message)


def localize_enum(value: t.Any) -> str:
  """Localize an enum member (or its `.value`) using the catalog's `enum.*` codes."""
  raw = getattr(value, "value", value)
  code = ENGLISH_TO_CODE.get(str(raw))

  if code is not None:
    return _(code)

  return _(str(raw))


def ngettext(singular: str, plural: str, n: int) -> str:
  return _translator.ngettext(singular, plural, n)


# Initialize with saved preference as soon as the module is imported (after data dir exists).
setup_i18n()
