import tkinter as tk
from tkinter import ttk
import pandas as pd

class DatasetHandler(tk.Frame):
  def __init__(self, master=None):
    super().__init__(master)

    self.target_var = tk.StringVar()
    self.split_var = tk.StringVar(value="0.8") 

    self.group = ttk.LabelFrame(self, text="Dataset Configuration")
    self.group.pack(fill=tk.X, expand=True, padx=10, pady=5)

    # --- Criação das linhas (Frames invisíveis) ---
    top_row = ttk.Frame(self.group)
    top_row.pack(fill=tk.X)

    bottom_row = ttk.Frame(self.group)
    bottom_row.pack(fill=tk.X)

    # --- Target Section (Primeira linha) ---
    ttk.Label(top_row, text="Target Variable:").pack(side=tk.LEFT, padx=(10, 5), pady=10)

    self.target_selector = ttk.Combobox(
      top_row, 
      textvariable=self.target_var, 
      state="readonly",
      width=20
    )
    self.target_selector.pack(side=tk.LEFT, padx=(0, 10), pady=10)

    # --- Split Section (Segunda linha) ---
    vcmd = (self.register(self.validate_split), '%P')

    # Ajustei o padx para (10, 5) para o texto ficar perfeitamente alinhado com o de cima
    # Ajustei o pady para (0, 10) para não somar com a margem da linha de cima
    ttk.Label(bottom_row, text="Train Size (0 to 1):").pack(side=tk.LEFT, padx=(10, 5), pady=(0, 10))

    self.split_input = ttk.Entry(
      bottom_row, 
      textvariable=self.split_var,
      width=10,
      validate="key", 
      validatecommand=vcmd
    )

    self.split_input.pack(side=tk.LEFT, padx=(0, 10), pady=(0, 10))

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