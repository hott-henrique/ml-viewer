#!/usr/bin/env python3
"""Regenerate gettext .po/.mo catalogs from i18n_catalog.MESSAGES (msgid = stable codes)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from application.i18n_catalog import MESSAGES  # noqa: E402
from compile_locales import compile_locales  # noqa: E402


def esc(s: str) -> str:
  return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def write_po(locale: str, path: Path) -> None:
  header = f'''# {locale} translations for ml-viewer (msgid = stable codes).
msgid ""
msgstr ""
"Project-Id-Version: ml-viewer\\n"
"Language: {locale}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''
  parts = [header]
  for code in sorted(MESSAGES):
    parts.append(f'msgid "{esc(code)}"\n')
    parts.append(f'msgstr "{esc(MESSAGES[code][locale])}"\n\n')
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text("".join(parts), encoding="utf-8")
  print(f"Wrote {path} ({len(MESSAGES)} entries)")


def main() -> None:
  locales_dir = ROOT / "src" / "application" / "locales"
  for locale in ("en_US", "pt_BR"):
    write_po(locale, locales_dir / locale / "LC_MESSAGES" / "ml-viewer.po")
  compile_locales(locales_dir)


if __name__ == "__main__":
  main()
