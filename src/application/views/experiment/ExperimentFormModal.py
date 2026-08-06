import typing as t
import tkinter as tk
from tkinter import ttk, messagebox

from application.managers import AnalysisManager, DatasetManager, ExperimentManager, ModelManager

from application.components import HyperParamForm
from application.enums import DatasetLayout
from application.i18n import _, display_title, localize_enum
from application.managers.DatasetManager import SUPERVISED_TYPES, DatasetMetadata
from application.managers.ExperimentManager import ExperimentMetadata, ExperimentSplitConfig

class ExperimentFormModal(tk.Toplevel):

  def __init__(
    self,
    parent: tk.Misc,
    on_save: t.Callable[[dict[str, t.Any]], None],
    initial_data: t.Optional[ExperimentMetadata] = None,
  ) -> None:
    super().__init__(parent)

    self.title(_("experiment.form.title"))
    self.geometry("560x820")
    self.resizable(False, False)
    self.grab_set()

    self.on_save = on_save
    self.initial_data = initial_data
    self.datasets = DatasetManager.get_all()
    self.analysis_vars: dict[str, tk.BooleanVar] = {}
    self.analysis_param_forms: dict[str, HyperParamForm] = {}
    self._analysis_param_frames: dict[str, ttk.Frame] = {}

    if self.initial_data:
      init_name = _("experiment.form.copy_name").format(name=self.initial_data.name)
    else:
      next_n = len(ExperimentManager.get_all()) + 1
      init_name = _("experiment.form.default_name").format(n=next_n)

    self.name_var = tk.StringVar(value=init_name)
    self.selected_dataset: t.Optional[DatasetMetadata] = None
    self.dataset_var = tk.StringVar()
    self.model_var = tk.StringVar()
    self._model_display_var = tk.StringVar()
    self._dataset_display_to_ds: dict[str, DatasetMetadata] = {}
    self._model_display_to_name: dict[str, str] = {}

    initial_split = self.initial_data.split_config if self.initial_data else None
    self.test_size_var = tk.StringVar(
      value=str(initial_split.test_size if initial_split else 0.2)
    )

    self._build_ui()
    self._apply_autofill()

  def _dataset_display(self, ds: DatasetMetadata) -> str:
    return f"{ds.name} ({localize_enum(ds.type)})"

  def _build_ui(self) -> None:
    main_frame = ttk.Frame(self, padding=(25, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Button(main_frame, text=_("experiment.form.run"), command=self._handle_save).pack(
      side=tk.BOTTOM, fill=tk.X, ipady=6, pady=(8, 0)
    )

    body = ttk.Frame(main_frame)
    body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    ttk.Label(body, text=_("experiment.form.name"), foreground="#333333").pack(anchor=tk.W)
    ttk.Entry(body, textvariable=self.name_var).pack(fill=tk.X, pady=(0, 12))

    ttk.Label(body, text=_("experiment.form.select_dataset"), foreground="#333333").pack(anchor=tk.W)
    self._dataset_display_to_ds = {self._dataset_display(ds): ds for ds in self.datasets}
    dataset_names = list(self._dataset_display_to_ds.keys())

    self.ds_combo = ttk.Combobox(body, textvariable=self.dataset_var, values=dataset_names, state="readonly")
    self.ds_combo.pack(fill=tk.X, pady=(0, 12))
    self.ds_combo.bind("<<ComboboxSelected>>", self._on_dataset_selected)

    self.split_frame = ttk.LabelFrame(body, text=_("experiment.form.split"))
    self.split_frame.pack(fill=tk.X, pady=(0, 12))

    split_inner = ttk.Frame(self.split_frame, padding=(8, 6))
    split_inner.pack(fill=tk.X)

    ttk.Label(split_inner, text=_("experiment.form.split_mode_train_test")).pack(anchor=tk.W)
    size_row = ttk.Frame(split_inner)
    size_row.pack(fill=tk.X, pady=(6, 0))
    ttk.Label(size_row, text=_("experiment.form.test_size")).pack(side=tk.LEFT)
    ttk.Entry(size_row, textvariable=self.test_size_var, width=8).pack(side=tk.LEFT, padx=(8, 0))

    self.split_hint = ttk.Label(split_inner, text="", foreground="#666666", wraplength=440)
    self.split_hint.pack(anchor=tk.W, pady=(6, 0))

    ttk.Label(body, text=_("experiment.form.select_model"), foreground="#333333").pack(anchor=tk.W)
    self.model_combo = ttk.Combobox(body, textvariable=self._model_display_var, state="readonly")
    self.model_combo.pack(fill=tk.X, pady=(0, 12))
    self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)

    self.param_frame = ttk.LabelFrame(body, text=_("experiment.form.hyperparams"))
    self.param_frame.pack(fill=tk.X, pady=(0, 12))

    self.hyperparam_form = HyperParamForm(self.param_frame, is_readonly=False, canvas_height=120)
    self.hyperparam_form.pack(fill=tk.X, padx=5, pady=5)

    self.analyses_frame = ttk.LabelFrame(body, text=_("nav.analyses"))
    self.analyses_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

    analyses_canvas = tk.Canvas(self.analyses_frame, highlightthickness=0, height=180)
    analyses_scroll = ttk.Scrollbar(self.analyses_frame, orient="vertical", command=analyses_canvas.yview)
    analyses_canvas.configure(yscrollcommand=analyses_scroll.set)
    analyses_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    analyses_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    self.analyses_inner = ttk.Frame(analyses_canvas)
    self._analyses_canvas_window = analyses_canvas.create_window((0, 0), window=self.analyses_inner, anchor="nw")

    def _on_analyses_configure(_event: t.Optional[tk.Event] = None) -> None:
      analyses_canvas.configure(scrollregion=analyses_canvas.bbox("all"))

    def _on_analyses_canvas_configure(event: tk.Event) -> None:
      analyses_canvas.itemconfig(self._analyses_canvas_window, width=event.width)

    self.analyses_inner.bind("<Configure>", _on_analyses_configure)
    analyses_canvas.bind("<Configure>", _on_analyses_canvas_configure)

    ttk.Label(
      self.analyses_inner,
      text=_("experiment.form.select_dataset_for_analyses"),
      foreground="#666666",
    ).pack(anchor=tk.W)

    self._update_split_visibility()

  def _needs_experiment_split(self) -> bool:
    ds = self.selected_dataset

    if ds is None:
      return False

    return ds.type in SUPERVISED_TYPES and ds.layout == DatasetLayout.NO_SPLIT

  def _update_split_visibility(self) -> None:
    if self._needs_experiment_split():
      self.split_frame.pack(fill=tk.X, pady=(0, 12), after=self.ds_combo)
      self.split_hint.config(text=_("experiment.form.split_hint_configure"))
    else:
      self.split_frame.pack_forget()

      if self.selected_dataset is None:
        return

      if self.selected_dataset.layout == DatasetLayout.TRAIN_TEST_SPLIT:
        self.split_hint.config(text=_("experiment.form.split_hint_preset"))

  def _render_analyses(self, preselected: t.Optional[list[str]] = None) -> None:
    for child in self.analyses_inner.winfo_children():
      child.destroy()

    self.analysis_vars = {}
    self.analysis_param_forms = {}
    self._analysis_param_frames = {}

    if not self.selected_dataset:
      ttk.Label(
        self.analyses_inner,
        text=_("experiment.form.select_dataset_for_analyses"),
        foreground="#666666",
      ).pack(anchor=tk.W)
      return

    registry = AnalysisManager.registry(self.selected_dataset.type)

    if not registry:
      ttk.Label(self.analyses_inner, text=_("experiment.form.no_analyses"), foreground="#666666").pack(anchor=tk.W)
      return

    saved_params = dict(self.initial_data.analysis_params) if self.initial_data else {}

    for name, config in registry.items():
      default_checked = True if preselected is None else name in preselected

      if preselected is None and not config.is_native:
        default_checked = False

      var = tk.BooleanVar(value=default_checked)
      self.analysis_vars[name] = var

      block = ttk.Frame(self.analyses_inner)
      block.pack(fill=tk.X, anchor=tk.W, pady=4)

      ttk.Checkbutton(
        block,
        text=display_title(config.title, name),
        variable=var,
        command=lambda n=name: self._sync_analysis_param_visibility(n),
      ).pack(anchor=tk.W)

      if config.params:
        params_frame = ttk.LabelFrame(block, text=_("experiment.form.analysis_params"))
        form = HyperParamForm(params_frame, is_readonly=False, canvas_height=88)
        form.pack(fill=tk.X, padx=4, pady=4)
        form.render_form(config.params)

        for pname, pvalue in saved_params.get(name, {}).items():
          if pname in form.param_vars:
            form.param_vars[pname].set(str(pvalue))

        self.analysis_param_forms[name] = form
        self._analysis_param_frames[name] = params_frame
        self._sync_analysis_param_visibility(name)

  def _sync_analysis_param_visibility(self, name: str) -> None:
    frame = self._analysis_param_frames.get(name)
    var = self.analysis_vars.get(name)

    if frame is None or var is None:
      return

    if var.get():
      frame.pack(fill=tk.X, padx=(16, 0), pady=(2, 0))
    else:
      frame.pack_forget()

  def _collect_analysis_params(self) -> dict[str, dict[str, t.Any]]:
    collected: dict[str, dict[str, t.Any]] = {}

    for name, var in self.analysis_vars.items():
      if not var.get():
        continue

      form = self.analysis_param_forms.get(name)

      if form is None:
        continue

      values = form.get_parsed_values()

      if values:
        collected[name] = values

    return collected

  def _apply_autofill(self) -> None:
    if not self.initial_data:
      return

    saved_ds = self.initial_data.dataset
    ds_str_to_find = self._dataset_display(saved_ds)

    if ds_str_to_find in self.ds_combo["values"]:
      self.dataset_var.set(ds_str_to_find)
      self._on_dataset_selected(None, preselected=self.initial_data.selected_analyses or None)

    saved_model = self.initial_data.model_name
    saved_model_display = next(
      (display for display, name in self._model_display_to_name.items() if name == saved_model),
      None,
    )

    if saved_model_display is not None:
      self._model_display_var.set(saved_model_display)
      self.model_var.set(saved_model)
      self._on_model_selected(None)

    saved_hyperparams = self.initial_data.hyperparameters

    for param_name, param_value in saved_hyperparams.items():
      if param_name in self.hyperparam_form.param_vars:
        self.hyperparam_form.param_vars[param_name].set(str(param_value))

  def _on_dataset_selected(
    self,
    event: t.Optional[tk.Event],
    preselected: t.Optional[list[str]] = None,
  ) -> None:
    selected_text = self.dataset_var.get()

    self.selected_dataset = self._dataset_display_to_ds.get(selected_text)

    if not self.selected_dataset:
      return

    self._update_split_visibility()

    prob_type = self.selected_dataset.type

    self._model_display_to_name = {
      display_title(model_config.title, name): name
      for name, model_config in ModelManager.registry(prob_type).items()
    }

    self.model_combo["values"] = list(self._model_display_to_name.keys())
    self._model_display_var.set("")
    self.model_var.set("")
    self.hyperparam_form.render_form([])
    self._render_analyses(preselected=preselected)

  def _on_model_selected(self, event: t.Optional[tk.Event]) -> None:
    if not self.selected_dataset:
      return

    self.model_var.set(self._model_display_to_name.get(self._model_display_var.get(), ""))

    prob_type = self.selected_dataset.type
    model_name = self.model_var.get()
    registry = ModelManager.registry(prob_type)
    model_config = registry.get(model_name)

    if model_config:
      self.hyperparam_form.render_form(model_config.params)

  def _parse_split_config(self) -> t.Optional[ExperimentSplitConfig]:
    if not self._needs_experiment_split():
      return None

    try:
      test_size = float(self.test_size_var.get().strip())
    except ValueError as exc:
      raise ValueError(_("experiment.form.err_invalid_test_size")) from exc

    return ExperimentSplitConfig(version=1, mode="TrainTest", test_size=test_size)

  def _handle_save(self) -> None:
    if not self.name_var.get() or not self.selected_dataset or not self.model_var.get():
      messagebox.showerror(_("common.error"), _("experiment.form.err_required"), parent=self)
      return

    selected_analyses = [name for name, var in self.analysis_vars.items() if var.get()]

    if not selected_analyses:
      messagebox.showerror(_("common.error"), _("experiment.form.err_need_analysis"), parent=self)
      return

    try:
      params = self.hyperparam_form.get_parsed_values()
      split_config = self._parse_split_config()
      analysis_params = self._collect_analysis_params()
    except ValueError as e:
      messagebox.showerror(_("common.validation_error"), str(e), parent=self)
      return

    payload = {
      "name": self.name_var.get(),
      "dataset": self.selected_dataset,
      "model_name": self.model_var.get(),
      "hyperparams": params,
      "analyses": selected_analyses,
      "analysis_params": analysis_params,
      "split_config": split_config,
    }

    self.on_save(payload)
    self.destroy()
