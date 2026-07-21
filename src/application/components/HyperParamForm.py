import tkinter as tk
from tkinter import ttk

class HyperParamForm(ttk.LabelFrame):
  def __init__(self, master=None):
    super().__init__(master, text="Hyperparameters")
    self.param_vars: dict[str, tk.StringVar] = {}
    self.param_definitions = []

    self.canvas = tk.Canvas(self, height=180, highlightthickness=0)
    self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
    self.canvas.configure(yscrollcommand=self.scrollbar.set)

    self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.inner_frame = ttk.Frame(self.canvas)

    self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

    self.inner_frame.bind("<Configure>", self._on_frame_configure)
    self.canvas.bind("<Configure>", self._on_canvas_configure)

  def _on_frame_configure(self, event=None):
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))

  def _on_canvas_configure(self, event):
    self.canvas.itemconfig(self.canvas_window, width=event.width)

  def render_form(self, params_config):
    for widget in self.inner_frame.winfo_children():
      widget.destroy()

    self.param_vars.clear()
    self.param_definitions = params_config

    if not params_config:
      ttk.Label(self.inner_frame, text="No hyperparameters available.", foreground="gray").pack(padx=10, pady=10)
      return

    for param in params_config:
      row = ttk.Frame(self.inner_frame)
      row.pack(fill=tk.X, padx=10, pady=5)

      ttk.Label(row, text=param["label"] + ":").pack(side=tk.LEFT)

      var = tk.StringVar(value=str(param.get("default", "")))
      self.param_vars[param["name"]] = var

      if param["type"] == "categorical":
        input_widget = ttk.Combobox(row, textvariable=var, values=param.get("options", []), state="readonly", width=15)
      else:
        input_widget = ttk.Entry(row, textvariable=var, width=15)

      input_widget.pack(side=tk.RIGHT)

  def get_parsed_values(self):
    parsed_kwargs = {}

    for param in self.param_definitions:
      name = param["name"]
      raw_value = self.param_vars[name].get()
      ptype = param["type"]

      if raw_value == "None":
        parsed_kwargs[name] = None
        continue

      if raw_value == "":
        continue

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