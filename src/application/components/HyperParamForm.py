import tkinter as tk
from tkinter import ttk

class HyperParamForm(ttk.LabelFrame):

  def __init__(self, master=None):
    super().__init__(master, text="Hyperparameters")
    self.param_vars: dict[str, tk.StringVar] = {}
    self.param_definitions = []

  def render_form(self, params_config):
    for widget in self.winfo_children():
      widget.destroy()

    self.param_vars.clear()
    self.param_definitions = params_config

    if not params_config:
      ttk.Label(self, text="No hyperparameters available.", foreground="gray").pack(padx=10, pady=10)
      return

    for param in params_config:
      row = ttk.Frame(self)
      row.pack(fill=tk.X, padx=10, pady=10)

      ttk.Label(row, text=param["label"] + ":").pack(side=tk.LEFT)

      var = tk.StringVar(value=str(param.get("default", "")))
      self.param_vars[param["name"]] = var

      if param["type"] == "categorical":
        input_widget = ttk.Combobox(row, textvariable=var, values=param.get("options", []), state="readonly", width=15)
      else:
        input_widget = ttk.Entry(row, textvariable=var, width=15)

      input_widget.pack(side=tk.RIGHT)

  def get_parsed_values(self):
    """Converte os valores das strings do Tkinter para os tipos corretos."""
    parsed_kwargs = {}

    for param in self.param_definitions:
      name = param["name"]
      raw_value = self.param_vars[name].get()
      ptype = param["type"]

      try:
        if ptype == "int":
          parsed_kwargs[name] = int(raw_value)
        elif ptype == "float":
          parsed_kwargs[name] = float(raw_value)
        elif ptype == "bool":
          parsed_kwargs[name] = raw_value.lower() in ('true', '1', 't', 'y', 'yes')
        else: # string / categorical
          parsed_kwargs[name] = raw_value
      except ValueError:
        raise ValueError(f"Invalid value for {param['label']}. Expected {ptype}.")

    return parsed_kwargs