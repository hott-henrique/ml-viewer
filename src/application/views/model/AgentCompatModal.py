from __future__ import annotations

import typing as t
import tkinter as tk
from tkinter import ttk, messagebox

from application.i18n import _, display_title
from application.managers import EnvironmentManager


class AgentCompatModal(tk.Toplevel):
  """Checklist of environment kinds compatible with an RL agent."""

  def __init__(
    self,
    parent: tk.Misc,
    *,
    agent_name: str,
    initial_kinds: t.Sequence[str] | None = None,
    title: str | None = None,
  ) -> None:
    super().__init__(parent)
    self.title(title or _("model.compat.title").format(agent=agent_name))
    self.resizable(False, False)
    self.transient(parent)
    self.grab_set()

    self.agent_name = agent_name
    self.result: list[str] | None = None
    self._vars: dict[str, tk.BooleanVar] = {}

    initial = set(initial_kinds or [])

    body = ttk.Frame(self, padding=12)
    body.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
      body,
      text=_("model.compat.hint").format(agent=agent_name),
      wraplength=360,
    ).pack(anchor=tk.W, pady=(0, 8))

    list_frame = ttk.Frame(body)
    list_frame.pack(fill=tk.BOTH, expand=True)

    for kind in EnvironmentManager.kind_options():
      config = EnvironmentManager.kind_config(kind)
      label = display_title(config.title, kind)
      var = tk.BooleanVar(value=kind in initial)
      self._vars[kind] = var
      ttk.Checkbutton(list_frame, text=label, variable=var).pack(anchor=tk.W, pady=2)

    if not self._vars:
      ttk.Label(list_frame, text=_("model.compat.no_environments"), foreground="#666666").pack(
        anchor=tk.W
      )

    btns = ttk.Frame(body)
    btns.pack(fill=tk.X, pady=(12, 0))
    ttk.Button(btns, text=_("common.cancel"), command=self._on_cancel).pack(side=tk.RIGHT)
    ttk.Button(btns, text=_("common.save"), command=self._on_save).pack(side=tk.RIGHT, padx=(0, 8))

    self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    self.update_idletasks()
    self.wait_visibility()
    self.focus_set()

  def _selected(self) -> list[str]:
    return [kind for kind, var in self._vars.items() if var.get()]

  def _on_save(self) -> None:
    selected = self._selected()
    if not selected:
      messagebox.showerror(_("common.error"), _("model.compat.err_need_one"), parent=self)
      return
    self.result = selected
    self.destroy()

  def _on_cancel(self) -> None:
    self.result = None
    self.destroy()

  @classmethod
  def ask(
    cls,
    parent: tk.Misc,
    *,
    agent_name: str,
    initial_kinds: t.Sequence[str] | None = None,
    title: str | None = None,
  ) -> list[str] | None:
    modal = cls(parent, agent_name=agent_name, initial_kinds=initial_kinds, title=title)
    parent.wait_window(modal)
    return modal.result
