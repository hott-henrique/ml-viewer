from __future__ import annotations

import typing as t
import tkinter as tk
from tkinter import ttk

import numpy as np

from application.i18n import _


class WatchWindow(tk.Toplevel):
  """Live view of the agent during training (RGB frames or state text)."""

  def __init__(self, master: tk.Misc, *, env_kind: str = "") -> None:
    super().__init__(master)
    self.title(_("experiment.watch.title"))
    self.geometry("420x480")
    self.resizable(True, True)

    self._env_kind = env_kind
    self._photo: t.Any = None

    self.status_var = tk.StringVar(value=_("experiment.watch.waiting"))
    ttk.Label(self, textvariable=self.status_var).pack(anchor=tk.W, padx=10, pady=(10, 4))

    self.canvas = tk.Canvas(self, width=400, height=400, bg="#1a1a1a", highlightthickness=0)
    self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    self.protocol("WM_DELETE_WINDOW", self._on_close)
    self._closed = False

  def _on_close(self) -> None:
    self._closed = True
    try:
      self.destroy()
    except tk.TclError:
      pass

  @property
  def closed(self) -> bool:
    return self._closed

  def on_step(
    self,
    episode_idx: int,
    step_idx: int,
    state: t.Any,
    action: t.Any,
    step_result: t.Any,
    frame: t.Any | None,
  ) -> bool:
    """Update the view. Returns False if the window is closed (stop watching)."""
    if self._closed:
      return False

    try:
      self.status_var.set(
        _("experiment.watch.status").format(
          episode=episode_idx + 1,
          step=step_idx + 1,
          reward=getattr(step_result, "reward", 0.0),
        )
      )

      if frame is not None:
        self._draw_rgb(frame)
      else:
        self.canvas.delete("all")
        self.canvas.create_text(
          200,
          200,
          text=str(state)[:200],
          fill="#eeeeee",
          width=380,
        )

      self.update_idletasks()
      self.update()
    except tk.TclError:
      self._closed = True
      return False

    return not self._closed

  def _draw_rgb(self, frame: t.Any) -> None:
    try:
      from PIL import Image, ImageTk
    except ImportError:
      self.canvas.delete("all")
      self.canvas.create_text(200, 200, text="Pillow required for RGB frames", fill="#ff8888")
      return

    arr = np.asarray(frame)
    if arr.ndim != 3 or arr.shape[2] not in (3, 4):
      return

    if arr.dtype != np.uint8:
      arr = np.clip(arr, 0, 255).astype(np.uint8)

    img = Image.fromarray(arr[..., :3])
    cw = max(1, int(self.canvas.winfo_width() or 400))
    ch = max(1, int(self.canvas.winfo_height() or 400))
    img = img.resize((cw, ch), Image.Resampling.NEAREST)
    self._photo = ImageTk.PhotoImage(img)
    self.canvas.delete("all")
    self.canvas.create_image(0, 0, anchor=tk.NW, image=self._photo)
