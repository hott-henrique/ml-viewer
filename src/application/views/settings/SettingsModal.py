import tkinter as tk
from tkinter import ttk
import typing as t

from application.db.paths import get_data_dir
from application.db.storage_usage import (
  format_bytes,
  format_percent,
  get_app_storage_breakdown,
  get_host_disk_usage,
)
from application.i18n import (
  LOCALE_LABELS,
  SUPPORTED_LOCALES,
  _,
  get_locale,
  set_locale,
)

class SettingsModal(tk.Toplevel):
  """Application settings: language preference and storage overview."""

  def __init__(
    self,
    parent: tk.Misc,
    *,
    on_locale_changed: t.Optional[t.Callable[[], None]] = None,
  ) -> None:
    super().__init__(parent)

    self.on_locale_changed = on_locale_changed
    self.title(_("settings.title"))
    self.geometry("420x560")
    self.resizable(False, False)
    self.grab_set()

    self._build_ui()

  def _build_ui(self) -> None:
    main = ttk.Frame(self, padding=(20, 20))
    main.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main, text=_("settings.language"), font=("", 14, "bold")).pack(anchor=tk.W, pady=(0, 6))

    labels = [LOCALE_LABELS[code] for code in SUPPORTED_LOCALES]
    current_label = LOCALE_LABELS.get(get_locale(), LOCALE_LABELS["en_US"])
    self._locale_var = tk.StringVar(value=current_label)

    locale_combo = ttk.Combobox(
      main,
      textvariable=self._locale_var,
      values=labels,
      state="readonly",
    )
    locale_combo.pack(fill=tk.X, pady=(0, 16))
    locale_combo.bind("<<ComboboxSelected>>", self._on_locale_selected)

    ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 16))

    ttk.Label(main, text=_("settings.storage.title"), font=("", 14, "bold")).pack(anchor=tk.W, pady=(0, 8))
    self._build_storage_section(main)

    ttk.Button(main, text=_("common.close"), command=self.destroy).pack(anchor=tk.E, pady=(18, 0))

  def _build_storage_section(self, parent: ttk.Frame) -> None:
    breakdown = get_app_storage_breakdown()
    disk = get_host_disk_usage()

    ttk.Label(parent, text=_("settings.storage.app_data"), font=("", 11, "bold")).pack(anchor=tk.W, pady=(0, 4))
    ttk.Label(parent, text=str(get_data_dir()), foreground="#666666", wraplength=360).pack(anchor=tk.W, pady=(0, 10))

    rows = (
      (_("settings.storage.datasets"), breakdown["datasets"]),
      (_("settings.storage.models"), breakdown["models"]),
      (_("settings.storage.analyses"), breakdown["analyses"]),
      (_("settings.storage.experiments"), breakdown["experiments"]),
      (_("settings.storage.database"), breakdown["database"]),
      (_("settings.storage.other"), breakdown["other"]),
    )

    for label, size in rows:
      row = ttk.Frame(parent)
      row.pack(fill=tk.X, pady=2)
      ttk.Label(row, text=label).pack(side=tk.LEFT)
      ttk.Label(row, text=format_bytes(size)).pack(side=tk.RIGHT)

    ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

    total_row = ttk.Frame(parent)
    total_row.pack(fill=tk.X)
    ttk.Label(total_row, text=_("settings.storage.app_total"), font=("", 11, "bold")).pack(side=tk.LEFT)
    ttk.Label(total_row, text=format_bytes(breakdown["total"]), font=("", 11, "bold")).pack(side=tk.RIGHT)

    ttk.Label(parent, text=_("settings.storage.computer_disk"), font=("", 11, "bold")).pack(anchor=tk.W, pady=(14, 6))

    disk_rows = (
      (_("settings.storage.disk_total"), format_bytes(disk["total"])),
      (_("settings.storage.disk_used"), f'{format_bytes(disk["used"])} ({format_percent(disk["used"], disk["total"])})'),
      (_("settings.storage.disk_free"), f'{format_bytes(disk["free"])} ({format_percent(disk["free"], disk["total"])})'),
      (_("settings.storage.app_vs_disk"), f'{format_bytes(breakdown["total"])} ({format_percent(breakdown["total"], disk["total"])})'),
    )

    for label, value in disk_rows:
      row = ttk.Frame(parent)
      row.pack(fill=tk.X, pady=2)
      ttk.Label(row, text=label).pack(side=tk.LEFT)
      ttk.Label(row, text=value).pack(side=tk.RIGHT)

  def _on_locale_selected(self, _event: object = None) -> None:
    selected_label = self._locale_var.get()
    locale_code = next(
      (code for code, label in LOCALE_LABELS.items() if label == selected_label),
      None,
    )

    if locale_code is None or locale_code == get_locale():
      return

    set_locale(locale_code)
    callback = self.on_locale_changed
    self.destroy()

    if callback:
      callback()
