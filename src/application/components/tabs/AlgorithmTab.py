import tkinter as tk
from tkinter import ttk

from application.components import AlgorithmSelector, HyperParamForm
from application.state import store

class AlgorithmTab(ttk.Frame):

  def __init__(self, master=None):
    super().__init__(master)

    self.algorithm_selector = AlgorithmSelector(self, on_change=self.on_algorithm_changed)
    self.algorithm_selector.pack(fill=tk.X, padx=10, pady=15)

    self.hyperparam_form = HyperParamForm(self, on_change=self.on_hyperparams_changed)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=5) 
    
    self.on_algorithm_changed()

  def on_algorithm_changed(self, *args):
    store.selected_algorithm = self.algorithm_selector.get_name()
    
    self.hyperparam_form.render_form(self.algorithm_selector.get_params_structure())

  def on_hyperparams_changed(self, parsed_params: dict):
    store.hyperparameters = parsed_params