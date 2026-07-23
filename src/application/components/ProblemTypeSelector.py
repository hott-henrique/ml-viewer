import tkinter as tk
from tkinter import ttk
from application.enums import LearningParadigm, ProblemType

class ProblemTypeSelector(ttk.Frame):
  def __init__(self, master, type_var: tk.StringVar, initial_value=ProblemType.CLASSIFICATION, **kwargs):
    super().__init__(master, **kwargs)

    self.type_var = type_var

    self.paradigm_map = {
        LearningParadigm.SUPERVISED: [ProblemType.CLASSIFICATION, ProblemType.REGRESSION],
        LearningParadigm.UNSUPERVISED: [ProblemType.CLUSTERING, ProblemType.DIMENSIONALITY_REDUCTION]
    }

    initial_paradigm = LearningParadigm.SUPERVISED

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

    paradigms = [p.value for p in self.paradigm_map.keys()]

    self.paradigm_combo = ttk.Combobox(
      self,
      textvariable=self.paradigm_var, 
      values=paradigms, 
      state="readonly"
    )
    self.paradigm_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    self.paradigm_combo.bind("<<ComboboxSelected>>", self._on_paradigm_change)

    current_tasks = [t.value for t in self.paradigm_map[LearningParadigm(self.paradigm_var.get())]]

    self.type_combo = ttk.Combobox(
      self, 
      textvariable=self.type_var, 
      values=current_tasks, 
      state="readonly"
    )

    self.type_combo.grid(row=0, column=1, sticky="ew")

  def _on_paradigm_change(self, event=None):
    paradigm = LearningParadigm(self.paradigm_var.get())
    valid_tasks = [t.value for t in self.paradigm_map[paradigm]]
    
    self.type_combo['values'] = valid_tasks
    self.type_var.set(valid_tasks[0])