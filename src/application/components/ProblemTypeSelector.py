import tkinter as tk
from tkinter import ttk

class ProblemTypeSelector(ttk.Frame):

  def __init__(self, parent, type_var: tk.StringVar, initial_value="Classification", **kwargs):
    super().__init__(parent, **kwargs)

    self.type_var = type_var

    self.paradigm_map = {
      "Supervised": ["Classification", "Regression"],
      "Unsupervised": ["Clustering", "Dimensionality Reduction"]
    }

    initial_paradigm = "Supervised"
    for paradigm, tasks in self.paradigm_map.items():
      if initial_value in tasks:
        initial_paradigm = paradigm
        break

    self.paradigm_var = tk.StringVar(value=initial_paradigm)
    self.type_var.set(initial_value)

    self._build_ui()

  def _build_ui(self):
    self.columnconfigure(0, weight=1)
    self.columnconfigure(1, weight=1)

    self.paradigm_combo = ttk.Combobox(
      self,
      textvariable=self.paradigm_var,
      values=list(self.paradigm_map.keys()),
      state="readonly"
    )
    self.paradigm_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    self.paradigm_combo.bind("<<ComboboxSelected>>", self._on_paradigm_change)

    self.type_combo = ttk.Combobox(
      self,
      textvariable=self.type_var,
      values=self.paradigm_map[self.paradigm_var.get()],
      state="readonly"
    )

    self.type_combo.grid(row=0, column=1, sticky="ew")

  def _on_paradigm_change(self, event=None):
    """Atualiza a lista de tarefas quando o paradigma muda."""
    paradigm = self.paradigm_var.get()
    valid_tasks = self.paradigm_map[paradigm]

    self.type_combo['values'] = valid_tasks

    self.type_var.set(valid_tasks[0])