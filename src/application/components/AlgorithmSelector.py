import tkinter as tk

from tkinter import ttk

from loader import AlgorithmRegistry

class AlgorithmSelector(tk.Frame):
  def __init__(self, master=None):
    super().__init__(master)

    algo_frame = ttk.LabelFrame(self, text="Model Configuration")
    algo_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
    
    ttk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT, padx=(10, 5), pady=10)

    self.algo_var = tk.StringVar()
    self.algo_selector = ttk.Combobox(
      algo_frame,
      textvariable=self.algo_var,
      state="readonly",
      width=30
    )

    self.algo_selector['values'] = AlgorithmRegistry.options()

    self.algo_selector.current(0) 
    self.algo_selector.pack(side=tk.LEFT, padx=(0, 10), pady=10)
  
  def get_instance(self):
    return AlgorithmRegistry.instantiate(self.algo_var.get())