import tkinter as tk
from tkinter import ttk

from application.i18n import _


_SECTIONS = (
  "datasets",
  "environments",
  "models",
  "analyses",
  "experiments",
  "settings",
)


class HomeView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text=_("home.view.title"), font=("", 16, "bold")).pack(side=tk.LEFT)

    body = ttk.Frame(self)
    body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    for section in _SECTIONS:
      block = ttk.Frame(body)
      block.pack(fill=tk.X, anchor=tk.W, pady=(0, 6))
      ttk.Label(block, text=_(f"home.title.{section}"), font=("", 11, "bold")).pack(anchor=tk.W)
      ttk.Label(
        block,
        text=_(f"home.body.{section}"),
        wraplength=900,
        justify=tk.LEFT,
      ).pack(anchor=tk.W, pady=(2, 0))
