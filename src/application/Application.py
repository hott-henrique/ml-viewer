import tkinter as tk
from tkinter import ttk

from application.db.paths import get_data_dir
from application.db.storage_usage import (
  format_bytes,
  format_percent,
  get_app_storage_breakdown,
  get_host_disk_usage,
)
from application.views import DatasetView, ExperimentView, ModelView, AnalysisView

class Application(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("ML Viewer")
    self.geometry("900x600")

    bg_sidebar = "#2c3e50"

    self.sidebar = tk.Frame(self, bg=bg_sidebar, width=200)
    self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
    self.sidebar.pack_propagate(False)

    tk.Label(self.sidebar, text="ML STUDIO", bg=bg_sidebar, fg="white", font=("", 14, "bold")).pack(pady=20)

    self.main_container = tk.Frame(self)
    self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.main_container.grid_rowconfigure(0, weight=1)
    self.main_container.grid_columnconfigure(0, weight=1)

    self.frames: dict[str, tk.Frame] = {}

    for ViewClass in (DatasetView, ModelView, AnalysisView, ExperimentView):
      page_name = ViewClass.__name__

      frame = ViewClass(parent=self.main_container)

      self.frames[page_name] = frame

      frame.grid(row=0, column=0, sticky="nsew")

    self._create_nav_button("📁 Datasets", DatasetView.__name__)
    self._create_nav_button("🧠 Models", ModelView.__name__)
    self._create_nav_button("📈 Analyses", AnalysisView.__name__)
    self._create_nav_button("🧪 Experiments", ExperimentView.__name__)

    storage_btn = tk.Button(
      self.sidebar,
      text="💾 Storage",
      bg="#34495e",
      fg="white",
      relief="flat",
      anchor="w",
      padx=20,
      cursor="hand2",
      command=self._open_storage_dialog,
    )
    storage_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=12, padx=10)

    self.show_frame(DatasetView.__name__)

  def _create_nav_button(self, text, page_name):
    btn = tk.Button(
      self.sidebar,
      text=text,
      bg="#34495e",
      fg="white",
      relief="flat",
      anchor="w",
      padx=20,
      cursor="hand2",
      command=lambda: self.show_frame(page_name)
    )

    btn.pack(fill=tk.X, pady=2, padx=10)

  def show_frame(self, page_name):
    frame = self.frames[page_name]
    frame.tkraise()

  def _open_storage_dialog(self) -> None:
    breakdown = get_app_storage_breakdown()
    disk = get_host_disk_usage()

    popup = tk.Toplevel(self)
    popup.title("Application Storage")
    popup.geometry("400x520")
    popup.resizable(False, False)
    popup.grab_set()

    frame = ttk.Frame(popup, padding=(20, 20))
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="App data", font=("", 14, "bold")).pack(anchor=tk.W, pady=(0, 4))
    ttk.Label(frame, text=str(get_data_dir()), foreground="#666666", wraplength=350).pack(anchor=tk.W, pady=(0, 12))

    rows = (
      ("Datasets", breakdown["datasets"]),
      ("Models", breakdown["models"]),
      ("Analyses", breakdown["analyses"]),
      ("Experiments", breakdown["experiments"]),
      ("Database", breakdown["database"]),
      ("Other", breakdown["other"]),
    )

    for label, size in rows:
      row = ttk.Frame(frame)
      row.pack(fill=tk.X, pady=2)
      ttk.Label(row, text=label).pack(side=tk.LEFT)
      ttk.Label(row, text=format_bytes(size)).pack(side=tk.RIGHT)

    ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

    total_row = ttk.Frame(frame)
    total_row.pack(fill=tk.X)
    ttk.Label(total_row, text="App total", font=("", 11, "bold")).pack(side=tk.LEFT)
    ttk.Label(total_row, text=format_bytes(breakdown["total"]), font=("", 11, "bold")).pack(side=tk.RIGHT)

    ttk.Label(frame, text="Computer disk", font=("", 14, "bold")).pack(anchor=tk.W, pady=(16, 8))

    disk_rows = (
      ("Disk total", format_bytes(disk["total"])),
      ("Disk used", f'{format_bytes(disk["used"])} ({format_percent(disk["used"], disk["total"])})'),
      ("Disk free", f'{format_bytes(disk["free"])} ({format_percent(disk["free"], disk["total"])})'),
      ("App vs disk", f'{format_bytes(breakdown["total"])} ({format_percent(breakdown["total"], disk["total"])})'),
    )

    for label, value in disk_rows:
      row = ttk.Frame(frame)
      row.pack(fill=tk.X, pady=2)
      ttk.Label(row, text=label).pack(side=tk.LEFT)
      ttk.Label(row, text=value).pack(side=tk.RIGHT)

    ttk.Button(frame, text="Close", command=popup.destroy).pack(anchor=tk.E, pady=(18, 0))

if __name__ == '__main__':
  app = Application()
  app.mainloop()
