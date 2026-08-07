import tkinter as tk
from tkinter import ttk

from application.enums import LearningParadigm, ProblemType
from application.i18n import localize_enum

class ProblemTypeSelector(ttk.Frame):
  def __init__(self, master, type_var: tk.StringVar, initial_value=ProblemType.CLASSIFICATION, **kwargs):
    super().__init__(master, **kwargs)

    self.type_var = type_var

    self.paradigm_map = {
        LearningParadigm.SUPERVISED: [ProblemType.CLASSIFICATION, ProblemType.REGRESSION],
        LearningParadigm.UNSUPERVISED: [
          ProblemType.CLUSTERING,
          ProblemType.DIMENSIONALITY_REDUCTION,
          ProblemType.ASSOCIATION_RULES,
        ],
    }

    # Display label <-> canonical .value
    self._paradigm_label_to_value: dict[str, str] = {}
    self._type_label_to_value: dict[str, str] = {}

    initial_paradigm = LearningParadigm.SUPERVISED

    for paradigm, tasks in self.paradigm_map.items():
      if initial_value in tasks:
        initial_paradigm = paradigm
        break

    self.paradigm_var = tk.StringVar()
    self.type_var.set(str(initial_value) if not isinstance(initial_value, str) else initial_value)
    self._display_type_var = tk.StringVar()

    self._set_paradigm_display(initial_paradigm)
    self._build_ui()
    self._sync_type_display_from_canonical()

  def _set_paradigm_display(self, paradigm: LearningParadigm) -> None:
    label = localize_enum(paradigm)
    self._paradigm_label_to_value[label] = paradigm.value
    self.paradigm_var.set(label)

  def _sync_type_display_from_canonical(self) -> None:
    canonical = self.type_var.get()
    label = localize_enum(canonical)
    self._type_label_to_value[label] = canonical
    self._display_type_var.set(label)

  def _build_ui(self):
    self.columnconfigure(0, weight=1)
    self.columnconfigure(1, weight=1)

    paradigm_labels = []
    self._paradigm_label_to_value = {}
    for paradigm in self.paradigm_map.keys():
      label = localize_enum(paradigm)
      self._paradigm_label_to_value[label] = paradigm.value
      paradigm_labels.append(label)

    self.paradigm_combo = ttk.Combobox(
      self,
      textvariable=self.paradigm_var,
      values=paradigm_labels,
      state="readonly"
    )
    self.paradigm_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    self.paradigm_combo.bind("<<ComboboxSelected>>", self._on_paradigm_change)

    self.type_combo = ttk.Combobox(
      self,
      textvariable=self._display_type_var,
      state="readonly"
    )
    self.type_combo.grid(row=0, column=1, sticky="ew")
    self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

    self._refresh_type_options()

  def _refresh_type_options(self) -> None:
    paradigm_value = self._paradigm_label_to_value.get(self.paradigm_var.get())
    if paradigm_value is None:
      return

    paradigm = LearningParadigm(paradigm_value)
    labels: list[str] = []
    self._type_label_to_value = {}

    for task in self.paradigm_map[paradigm]:
      label = localize_enum(task)
      self._type_label_to_value[label] = task.value
      labels.append(label)

    self.type_combo["values"] = labels

  def _on_paradigm_change(self, event=None):
    self._refresh_type_options()
    labels = list(self.type_combo["values"])
    if labels:
      self._display_type_var.set(labels[0])
      self.type_var.set(self._type_label_to_value[labels[0]])

  def _on_type_change(self, event=None):
    canonical = self._type_label_to_value.get(self._display_type_var.get())
    if canonical:
      self.type_var.set(canonical)
