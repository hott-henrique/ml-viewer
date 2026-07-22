import typing as t
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import AlgorithmSelector, HyperParamForm
from application.state import store
from loader import AlgorithmRegistry

class AlgorithmTab(ttk.Frame):

  def __init__(self, master=None):
    super().__init__(master)

    self._last_problem_type: t.Optional[str] = None

    import_frame = ttk.Frame(self)
    import_frame.pack(fill=tk.X, padx=10, pady=(15, 0))

    self.import_btn = ttk.Button(import_frame, text="Import Custom Algorithm (.py)", command=self._import_algorithm)
    self.import_btn.pack(side=tk.RIGHT)

    self.algorithm_selector = AlgorithmSelector(
      self,
      on_change=self.on_algorithm_changed,
      on_no_algorithm_available=self.on_no_algorithm_available
    )
    self.algorithm_selector.pack(fill=tk.X, padx=10, pady=15)

    self.hyperparam_form = HyperParamForm(self, on_change=self.on_hyperparams_changed)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=5) 
    
    self.bind("<Visibility>", self._on_tab_visible)

  def _import_algorithm(self):
    filepath = filedialog.askopenfilename(
      title="Select Custom Algorithm File",
      filetypes=[("Python Files", "*.py")]
    )
    
    if not filepath:
      return

    try:
      added_algos = AlgorithmRegistry.import_from_file(filepath)

      self.algorithm_selector.set_problem_type(store.problem_type)

      messagebox.showinfo("Success", f"Successfully imported: {', '.join(added_algos)}")
    except Exception as e:
      messagebox.showerror("Import Error", f"Failed to load custom algorithm:\n\n{str(e)}")

  def _on_tab_visible(self, event: t.Optional[tk.Event]=None):
    current_type = store.problem_type

    if self._last_problem_type != current_type:
      self._last_problem_type = current_type
      self.algorithm_selector.set_problem_type(current_type)

  def on_algorithm_changed(self, *args):
    store.selected_algorithm = self.algorithm_selector.get_name()
    self.hyperparam_form.render_form(self.algorithm_selector.get_params_structure())

  def on_no_algorithm_available(self, *args):
    store.selected_algorithm = ""
    self.hyperparam_form.clear_form()

  def on_hyperparams_changed(self, parsed_params: dict):
    store.hyperparameters = parsed_params