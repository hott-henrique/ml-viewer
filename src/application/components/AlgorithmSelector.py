import typing as t

import tkinter as tk

from tkinter import ttk

from loader import AlgorithmRegistry

class AlgorithmSelector(ttk.LabelFrame):
  def __init__(self, master=None, on_change: t.Optional[t.Callable]=None):
    super().__init__(master, text="Model Configuration")

    self.on_change = on_change

    ttk.Label(self, text="Algorithm:").pack(side=tk.LEFT, padx=10, pady=10)

    self.algo_var = tk.StringVar()
    self.algo_selector = ttk.Combobox(
      self,
      textvariable=self.algo_var,
      state="readonly",
      width=30
    )

    self.algo_selector['values'] = AlgorithmRegistry.options()

    self.algo_selector.current(0) 
    self.algo_selector.pack(side=tk.LEFT, padx=10, pady=10)

    self.algo_selector.bind("<<ComboboxSelected>>", self._handle_selection)

  def get_name(self):
    return self.algo_var.get()

  def get_params_structure(self):
    return AlgorithmRegistry.registry().get(self.algo_var.get())['params']

  def _handle_selection(self, event):
    if self.on_change:
      self.on_change()