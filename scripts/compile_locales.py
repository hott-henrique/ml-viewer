#!/usr/bin/env python3
"""Compile gettext .po catalogs to binary .mo files (no gettext toolchain required)."""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path


def _unescape(s: str) -> str:
  return (
    s.replace(r"\\", "\x00")
    .replace(r"\n", "\n")
    .replace(r"\t", "\t")
    .replace(r"\"", '"')
    .replace("\x00", "\\")
  )


def parse_po(path: Path) -> dict[str, str]:
  """Parse a simple .po file into msgid -> msgstr (skips plurals / contexts)."""
  text = path.read_text(encoding="utf-8")
  entries: dict[str, str] = {}

  msgid: list[str] | None = None
  msgstr: list[str] | None = None
  mode: str | None = None

  string_re = re.compile(r'^"(.*)"\s*$')

  def flush() -> None:
    nonlocal msgid, msgstr, mode
    if msgid is not None and msgstr is not None:
      key = _unescape("".join(msgid))
      val = _unescape("".join(msgstr))
      # Keep the empty msgid header (charset metadata) and all real entries.
      entries[key] = val
    msgid = None
    msgstr = None
    mode = None

  for raw in text.splitlines():
    line = raw.strip()

    if not line or line.startswith("#"):
      continue

    if line.startswith("msgid "):
      flush()
      mode = "msgid"
      msgid = []
      msgstr = None
      rest = line[len("msgid ") :].strip()
      m = string_re.match(rest)
      if m:
        msgid.append(m.group(1))
      continue

    if line.startswith("msgstr "):
      mode = "msgstr"
      msgstr = []
      rest = line[len("msgstr ") :].strip()
      m = string_re.match(rest)
      if m:
        msgstr.append(m.group(1))
      continue

    if line.startswith("msgid_plural ") or line.startswith("msgstr["):
      # Plurals are not used in this catalog; ignore continuation of plural forms.
      mode = None
      continue

    m = string_re.match(line)
    if m and mode == "msgid" and msgid is not None:
      msgid.append(m.group(1))
    elif m and mode == "msgstr" and msgstr is not None:
      msgstr.append(m.group(1))

  flush()
  return entries


def write_mo(entries: dict[str, str], path: Path) -> None:
  """Write a GNU .mo file (little-endian) from msgid/msgstr pairs."""
  keys = sorted(entries.keys())
  ids = b"\x00".join(k.encode("utf-8") for k in keys) + b"\x00"
  strs = b"\x00".join(entries[k].encode("utf-8") for k in keys) + b"\x00"

  keystart = 7 * 4 + 16 * len(keys)
  valuestart = keystart + len(ids)
  koffsets: list[tuple[int, int]] = []
  voffsets: list[tuple[int, int]] = []
  k_offset = 0
  v_offset = 0

  for k in keys:
    k_enc = k.encode("utf-8")
    v_enc = entries[k].encode("utf-8")
    koffsets.append((len(k_enc), keystart + k_offset))
    voffsets.append((len(v_enc), valuestart + v_offset))
    k_offset += len(k_enc) + 1
    v_offset += len(v_enc) + 1

  output = struct.pack(
    "Iiiiiii",
    0x950412DE,  # magic
    0,  # version
    len(keys),
    7 * 4,  # offset of table with original strings
    7 * 4 + 8 * len(keys),  # offset of table with translation strings
    0,
    0,
  )

  for length, offset in koffsets:
    output += struct.pack("ii", length, offset)
  for length, offset in voffsets:
    output += struct.pack("ii", length, offset)

  output += ids
  output += strs

  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_bytes(output)


def compile_locales(locales_dir: Path) -> list[Path]:
  written: list[Path] = []

  for po_path in locales_dir.glob("*/LC_MESSAGES/*.po"):
    entries = parse_po(po_path)
    mo_path = po_path.with_suffix(".mo")
    write_mo(entries, mo_path)
    written.append(mo_path)
    print(f"Compiled {po_path} -> {mo_path} ({len(entries)} entries)")

  return written


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--locales-dir",
    type=Path,
    default=Path(__file__).resolve().parents[1] / "src" / "application" / "locales",
  )
  args = parser.parse_args()
  compile_locales(args.locales_dir)


if __name__ == "__main__":
  main()
