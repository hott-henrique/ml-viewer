import typing as t
import tkinter as tk
from tkinter import ttk
from loader import AlgorithmRegistry

class AlgorithmSelector(ttk.LabelFrame):
  def __init__(self,
               master=None,
               on_change: t.Optional[t.Callable]=None,
               on_no_algorithm_available: t.Optional[t.Callable]=None):
    super().__init__(master, text="Model Configuration")
    
    self.on_change = on_change
    self.on_no_algorithm_available = on_no_algorithm_available
    self.algo_var = tk.StringVar()
    self.dropdown_window = None

    self.current_problem_type = "Classification"

    container = ttk.Frame(self)
    container.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(container, text="Algorithm:").pack(side=tk.LEFT, padx=(0, 10))

    self.input_frame = tk.Frame(container, bg="white", highlightbackground="#a0a0a0", highlightthickness=1)
    self.input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

    self.display_box = tk.Label(
      self.input_frame, 
      textvariable=self.algo_var, 
      bg="white", 
      anchor=tk.W, 
      padx=5,
      pady=4,
      cursor="hand2"
    )
    self.display_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.arrow_btn = tk.Label(
      self.input_frame, 
      text="▼", 
      bg="#e0e0e0", 
      width=3, 
      cursor="hand2"
    )
    self.arrow_btn.pack(side=tk.RIGHT, fill=tk.Y)

    self.display_box.bind("<Button-1>", lambda e: self.toggle_dropdown())
    self.arrow_btn.bind("<Button-1>", lambda e: self.toggle_dropdown())

    self.bind_all("<Button-1>", self._check_click_outside, add="+")

    registry = AlgorithmRegistry.registry(self.current_problem_type)

    if registry:
      first_key = list(registry.keys())[0]
      self.algo_var.set(first_key)

  def set_problem_type(self, problem_type: str):
    self.current_problem_type = problem_type

    algos = AlgorithmRegistry.registry(problem_type)

    if algos:
      self.algo_var.set(list(algos.keys())[0])
    else:
      self.algo_var.set("No algorithms found")

    if self.on_change and algos and len(algos) > 0:
      self.on_change()
    elif self.on_no_algorithm_available:
      self.on_no_algorithm_available()

  def _check_click_outside(self, event: tk.Event):
    if not self.dropdown_window or not self.dropdown_window.winfo_exists():
      return
      
    if event.widget in (self.display_box, self.arrow_btn, self.input_frame):
      return
      
    try:
      if event.widget.winfo_toplevel() != self.dropdown_window:
        self.close_dropdown()
    except tk.TclError:
      pass

  def toggle_dropdown(self):
    if self.dropdown_window and self.dropdown_window.winfo_exists():
      self.close_dropdown()
      return

    self.dropdown_window = tk.Toplevel(self)
    self.dropdown_window.wm_overrideredirect(True)
    self.dropdown_window.configure(bg="gray")

    x = self.input_frame.winfo_rootx()
    y = self.input_frame.winfo_rooty() + self.input_frame.winfo_height()
    width = self.input_frame.winfo_width()

    self.dropdown_window.geometry(f"{width}x250+{x}+{y}")

    canvas = tk.Canvas(self.dropdown_window, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(self.dropdown_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    inner_frame = tk.Frame(canvas, bg="white")

    canvas.create_window((0, 0), window=inner_frame, anchor="nw", width=width-15)

    def on_frame_configure(event):
      canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", on_frame_configure)

    self._populate_dropdown(inner_frame, width)

  def _populate_dropdown(self, parent_frame, box_width):
    registry = AlgorithmRegistry.registry(self.current_problem_type)

    if not registry or len(registry) <= 0:
      return

    for key, data in registry.items():
      desc = data.get("description", "No description available.")

      item_frame = tk.Frame(parent_frame, bg="white", cursor="hand2")
      item_frame.pack(fill=tk.X, pady=1)

      title_lbl = tk.Label(item_frame, text=key, font=("", 10, "bold"), bg="white", anchor=tk.W)
      title_lbl.pack(fill=tk.X, padx=5, pady=(5, 0))

      desc_lbl = tk.Label(
        item_frame, 
        text=desc, 
        foreground="#666666", 
        bg="white", 
        anchor=tk.W, 
        justify=tk.LEFT, 
        wraplength=box_width - 20
      )
      desc_lbl.pack(fill=tk.X, padx=5, pady=(0, 5))

      self._bind_item_events(item_frame, title_lbl, desc_lbl, key)

  def _bind_item_events(self, frame: tk.Frame, title: tk.Label, desc: tk.Label, algo_key: str):
    def on_enter(e):
      frame.config(bg="#f0f0f0")
      title.config(bg="#f0f0f0")
      desc.config(bg="#f0f0f0")

    def on_leave(e):
      frame.config(bg="white")
      title.config(bg="white")
      desc.config(bg="white")

    def on_select(e):
      self.algo_var.set(algo_key)
      self.close_dropdown()
      if self.on_change:
        self.on_change()

    for widget in (frame, title, desc):
      widget.bind("<Enter>", on_enter)
      widget.bind("<Leave>", on_leave)
      widget.bind("<Button-1>", on_select)

  def close_dropdown(self):
    if self.dropdown_window:
      self.dropdown_window.destroy()
      self.dropdown_window = None

  def get_name(self):
    return self.algo_var.get()

  def get_params_structure(self):
    actual_name = self.get_name()

    if not actual_name:
      return []

    return AlgorithmRegistry.registry(self.current_problem_type).get(actual_name, {}).get('params', [])