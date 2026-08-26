import tkinter as tk
from tkinter import ttk

from application.i18n import _
from application.views import DatasetView, EnvironmentView, ExperimentView, ModelView, AnalysisView
from application.views.settings import SettingsModal

class Application(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title(_("app.title"))
    self.geometry("900x600")

    self.bg_sidebar = "#2c3e50"
    self._active_page = DatasetView.__name__
    self._nav_buttons: list[tk.Button] = []

    self.sidebar = tk.Frame(self, bg=self.bg_sidebar, width=200)
    self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
    self.sidebar.pack_propagate(False)

    self.main_container = tk.Frame(self)
    self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.main_container.grid_rowconfigure(0, weight=1)
    self.main_container.grid_columnconfigure(0, weight=1)

    self.frames: dict[str, tk.Frame] = {}

    self._build_sidebar()
    self._build_frames()
    self.show_frame(self._active_page)

  def _build_sidebar(self) -> None:
    for child in self.sidebar.winfo_children():
      child.destroy()

    self._nav_buttons = []

    tk.Label(
      self.sidebar,
      text=_("app.brand"),
      bg=self.bg_sidebar,
      fg="white",
      font=("", 14, "bold"),
    ).pack(pady=20)

    self._create_nav_button(_("nav.datasets"), DatasetView.__name__)
    self._create_nav_button(_("nav.environments"), EnvironmentView.__name__)
    self._create_nav_button(_("nav.models"), ModelView.__name__)
    self._create_nav_button(_("nav.analyses"), AnalysisView.__name__)
    self._create_nav_button(_("experiment.view.title"), ExperimentView.__name__)

    settings_btn = tk.Button(
      self.sidebar,
      text=_("nav.settings"),
      bg="#34495e",
      fg="white",
      relief="flat",
      anchor="w",
      padx=20,
      cursor="hand2",
      command=self._open_settings,
    )
    settings_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=12, padx=10)

  def _build_frames(self) -> None:
    for frame in self.frames.values():
      frame.destroy()

    self.frames.clear()

    for ViewClass in (DatasetView, EnvironmentView, ModelView, AnalysisView, ExperimentView):
      page_name = ViewClass.__name__
      frame = ViewClass(parent=self.main_container)
      self.frames[page_name] = frame
      frame.grid(row=0, column=0, sticky="nsew")

  def _create_nav_button(self, text: str, page_name: str) -> None:
    btn = tk.Button(
      self.sidebar,
      text=text,
      bg="#34495e",
      fg="white",
      relief="flat",
      anchor="w",
      padx=20,
      cursor="hand2",
      command=lambda: self.show_frame(page_name),
    )
    btn.pack(fill=tk.X, pady=2, padx=10)
    self._nav_buttons.append(btn)

  def show_frame(self, page_name: str) -> None:
    self._active_page = page_name
    frame = self.frames[page_name]
    frame.tkraise()

  def _open_settings(self) -> None:
    SettingsModal(self, on_locale_changed=self._rebuild_ui)

  def _rebuild_ui(self) -> None:
    current = self._active_page if self._active_page in self.frames else DatasetView.__name__
    self.title(_("app.title"))
    self._build_sidebar()
    self._build_frames()
    self.show_frame(current if current in self.frames else DatasetView.__name__)

if __name__ == '__main__':
  app = Application()
  app.mainloop()
