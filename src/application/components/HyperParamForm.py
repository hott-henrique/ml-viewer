import tkinter as tk
from tkinter import ttk

def create_tooltip(widget: tk.Widget, text: str):
  tooltip_window = None

  def on_enter(event: tk.Event):
    nonlocal tooltip_window

    tooltip_window = tk.Toplevel(widget)
    tooltip_window.wm_overrideredirect(True)

    x = widget.winfo_rootx() + 20
    y = widget.winfo_rooty() + 15
    tooltip_window.wm_geometry(f"+{x}+{y}")

    label = tk.Label(
      tooltip_window, 
      text=text, 
      justify=tk.LEFT,
      background="#ffffe0", 
      relief=tk.SOLID, 
      borderwidth=1,
      wraplength=250
    )
    label.pack(ipadx=4, ipady=4)

  def on_leave(event):
    nonlocal tooltip_window
    if tooltip_window:
      tooltip_window.destroy()
      tooltip_window = None

  widget.bind("<Enter>", on_enter)
  widget.bind("<Leave>", on_leave)

class HyperParamForm(ttk.LabelFrame):

  def __init__(self, master=None, on_change=None):
    super().__init__(master, text="Hyperparameters")
    self.on_change = on_change 
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

  def clear_form(self):
    for widget in self.inner_frame.winfo_children():
      widget.destroy()

  def render_form(self, params_config):
    self.clear_form()

    self.param_vars.clear()
    self.param_definitions = params_config

    if not params_config:
      ttk.Label(self.inner_frame, text="No hyperparameters available.", foreground="gray").pack(padx=10, pady=10)
      self._trigger_change()
      return

    for param in params_config:
      row = ttk.Frame(self.inner_frame)
      row.pack(fill=tk.X, padx=10, pady=5)

      ttk.Label(row, text=param["label"] + ":").pack(side=tk.LEFT)

      var = tk.StringVar(value=str(param.get("default", "")))
      var.trace_add("write", self._trigger_change)

      self.param_vars[param["name"]] = var

      desc = param.get("description", "No description available.")
      info_icon = tk.Label(row, text="ⓘ", foreground="#0055cc", cursor="question_arrow", font=("", 10))
      info_icon.pack(side=tk.RIGHT, padx=(5, 0))

      create_tooltip(info_icon, desc)

      if param["type"] == "categorical":
        input_widget = ttk.Combobox(row, textvariable=var, values=param.get("options", []), state="readonly", width=15)
      elif param["type"] == "bool":
        input_widget = ttk.Combobox(row, textvariable=var, values=["True", "False"], state="readonly", width=15)
      else:
        input_widget = ttk.Entry(row, textvariable=var, width=15)

      input_widget.pack(side=tk.RIGHT)

    self._trigger_change()

  def _trigger_change(self, *args):
    if self.on_change:
      try:
        parsed_vals = self.get_parsed_values()
        self.on_change(parsed_vals)
      except ValueError:
        pass

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

      if raw_value == "True":
        parsed_kwargs[name] = True
        continue
      if raw_value == "False":
        parsed_kwargs[name] = False
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