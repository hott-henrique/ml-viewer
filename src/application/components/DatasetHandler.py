import tkinter as tk
from tkinter import ttk
import pandas as pd

class DatasetHandler(ttk.LabelFrame):
  def __init__(self, master=None):
    super().__init__(master, text="Dataset Configuration", padding=(10, 10))

    self.target_var = tk.StringVar()
    self.split_var = tk.StringVar(value="0.8") 

    top_row = ttk.Frame(self)
    top_row.pack(fill=tk.X)

    bottom_row = ttk.Frame(self)
    bottom_row.pack(fill=tk.X)

    ttk.Label(top_row, text="Target Variable:").pack(side=tk.LEFT, padx=10, pady=10)

    self.target_selector = ttk.Combobox(
      top_row, 
      textvariable=self.target_var, 
      state="readonly",
      width=20
    )
    self.target_selector.pack(side=tk.LEFT, padx=10, pady=10)

    vcmd = (self.register(self.validate_split), '%P')

    ttk.Label(bottom_row, text="Train Size (0 to 1):").pack(side=tk.LEFT, padx=10, pady=10)

    self.split_input = ttk.Entry(
      bottom_row, 
      textvariable=self.split_var,
      width=10,
      validate="key", 
      validatecommand=vcmd
    )

    self.split_input.pack(side=tk.LEFT, padx=10, pady=10)

  def validate_split(self, typed_value):
    if typed_value == "":
      return True
    
    if typed_value in ("0", "0.", "1", "1."):
      return True

    try:
      value = float(typed_value)
      return 0.0 <= value <= 1.0
    except ValueError:
      return False

  def load_columns(self, filepath):
    try:
      df = pd.read_csv(filepath, nrows=0)
      columns = df.columns.tolist()

      self.target_selector['values'] = columns
      
      if columns:
        self.target_selector.set(columns[-1])

    except Exception as e:
      print(f"Error reading CSV: {e}")
      self.target_selector['values'] = []
      self.target_var.set("Error loading")