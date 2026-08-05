#!/usr/bin/env python3
"""Regenerate .po catalogs (msgid = stable code, msgstr = localized text) from
application.i18n_catalog.MESSAGES."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "src" / "application" / "locales"

_spec = importlib.util.spec_from_file_location(
  "i18n_catalog", ROOT / "src" / "application" / "i18n_catalog.py"
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
MESSAGES = _module.MESSAGES


def _escape(s: str) -> str:
  return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")


def build_po(locale: str) -> str:
  lines = [
    'msgid ""',
    'msgstr ""',
    '"Content-Type: text/plain; charset=UTF-8\\n"',
    f'"Language: {locale}\\n"',
    "",
  ]

  for code in sorted(MESSAGES.keys()):
    text = MESSAGES[code].get(locale, MESSAGES[code].get("en_US", code))
    lines.append(f'msgid "{_escape(code)}"')
    lines.append(f'msgstr "{_escape(text)}"')
    lines.append("")

  return "\n".join(lines)


def main() -> None:
  for locale in ("en_US", "pt_BR"):
    po_path = LOCALES_DIR / locale / "LC_MESSAGES" / "ml-viewer.po"
    po_path.parent.mkdir(parents=True, exist_ok=True)
    po_path.write_text(build_po(locale), encoding="utf-8")
    print(f"Wrote {po_path}")


if __name__ == "__main__":
  main()
