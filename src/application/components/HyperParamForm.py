import typing as t
import tkinter as tk
from tkinter import ttk

from application.enums import ParamType
from application.i18n import _, resolve_text
from application.managers.model.ModelManager import HyperParamConfig

def create_tooltip(widget: tk.Widget, text: str) -> None:
  tooltip_window: t.Optional[tk.Toplevel] = None

  def on_enter(event: tk.Event) -> None:
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

  def on_leave(event: tk.Event) -> None:
    nonlocal tooltip_window

    if tooltip_window:
      tooltip_window.destroy()
      tooltip_window = None

  widget.bind("<Enter>", on_enter)
  widget.bind("<Leave>", on_leave)

class HyperParamForm(ttk.Frame):

  def __init__(
    self,
    master: t.Optional[tk.Misc] = None,
    on_change: t.Optional[t.Callable[[dict[str, t.Any]], None]] = None,
    is_readonly: bool = False,
  ) -> None:
    super().__init__(master)
    self.on_change = on_change 
    self.is_readonly = is_readonly

    self.param_vars: dict[str, tk.StringVar] = {}
    
    self.param_definitions: list[HyperParamConfig] = []

    self.canvas = tk.Canvas(self, height=180, highlightthickness=0)
    self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
    self.canvas.configure(yscrollcommand=self.scrollbar.set)

    self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.inner_frame = ttk.Frame(self.canvas)
    self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

    self.inner_frame.bind("<Configure>", self._on_frame_configure)
    self.canvas.bind("<Configure>", self._on_canvas_configure)

  def _on_frame_configure(self, event: t.Optional[tk.Event] = None) -> None:
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))

  def _on_canvas_configure(self, event: tk.Event) -> None:
    self.canvas.itemconfig(self.canvas_window, width=event.width)

  def clear_form(self) -> None:
    for widget in self.inner_frame.winfo_children():
      widget.destroy()

  def render_form(self, params_config: list[HyperParamConfig]) -> None:
    self.clear_form()
    self.param_vars.clear()
    self.param_definitions = params_config

    if not params_config:
      ttk.Label(self.inner_frame, text=_("model.hyperparams.empty"), foreground="gray").pack(padx=10, pady=10)
      self._trigger_change()
      return

    for param in params_config:
      row = ttk.Frame(self.inner_frame)
      row.pack(fill=tk.X, padx=10, pady=5)

      label = resolve_text(param.label)
      ttk.Label(row, text=label + ":").pack(side=tk.LEFT)

      var = tk.StringVar(value=str(param.default if param.default is not None else ""))
      
      if not self.is_readonly:
        var.trace_add("write", self._trigger_change)

      self.param_vars[param.name] = var

      desc = resolve_text(param.description) or _("common.no_description_available")
      info_icon = tk.Label(row, text="ⓘ", foreground="#0055cc", cursor="question_arrow", font=("", 10))
      info_icon.pack(side=tk.RIGHT, padx=(5, 0))

      create_tooltip(info_icon, desc)

      if param.type == ParamType.CATEGORICAL.value:
        cbox_state = "disabled" if self.is_readonly else "readonly"
        input_widget = ttk.Combobox(row, textvariable=var, values=param.options, state=cbox_state, width=15)
      elif param.type == ParamType.BOOL.value:
        cbox_state = "disabled" if self.is_readonly else "readonly"
        input_widget = ttk.Combobox(row, textvariable=var, values=["True", "False"], state=cbox_state, width=15)
      else: # ParamType.INT | FLOAT | STRING.value
        entry_state = "readonly" if self.is_readonly else "normal"
        input_widget = ttk.Entry(row, textvariable=var, state=entry_state, width=15)

      input_widget.pack(side=tk.RIGHT)

    if not self.is_readonly:
      self._trigger_change()

  def _trigger_change(self, *args: t.Any) -> None:
    if self.on_change:
      try:
        parsed_vals = self.get_parsed_values()
        self.on_change(parsed_vals)
      except ValueError:
        pass

  def get_parsed_values(self) -> dict[str, t.Any]:
    parsed_kwargs: dict[str, t.Any] = {}

    for param in self.param_definitions:
      name = param.name
      raw_value = self.param_vars[name].get()
      ptype = param.type

      if raw_value == "None" or raw_value == "":
        continue

      if raw_value == "True":
        parsed_kwargs[name] = True
        continue
      if raw_value == "False":
        parsed_kwargs[name] = False
        continue

      try:
        if ptype == ParamType.INT.value:
          parsed_kwargs[name] = int(raw_value)
        elif ptype == ParamType.FLOAT.value:
          parsed_kwargs[name] = float(raw_value)
        elif ptype == ParamType.BOOL.value:
          parsed_kwargs[name] = raw_value.lower() in ('true', '1', 't', 'y', 'yes')
        else: # ParamType.CATEGORICAL.value
          parsed_kwargs[name] = raw_value
      except ValueError:
        raise ValueError(
          _("model.hyperparams.invalid_value").format(label=resolve_text(param.label), type=ptype)
        )

    for param in self.param_definitions:
      if getattr(param, "validate", None) is None:
        continue

      if param.field_validation is None:
        continue

      field_value = parsed_kwargs.get(param.name)

      error_msg = param.field_validation(field_value, parsed_kwargs)

      if error_msg:
        raise ValueError(error_msg)

    return parsed_kwargs