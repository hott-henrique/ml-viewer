import tkinter as tk

from application.views import DatasetView, ExperimentView, ModelView

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

    for ViewClass in (DatasetView, ModelView, ExperimentView):
      page_name = ViewClass.__name__

      frame = ViewClass(parent=self.main_container)

      self.frames[page_name] = frame

      frame.grid(row=0, column=0, sticky="nsew")

    self._create_nav_button("📁 Datasets", DatasetView.__name__)
    self._create_nav_button("🧠 Models", ModelView.__name__)
    self._create_nav_button("🧪 Experiments", ExperimentView.__name__)

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

if __name__ == '__main__':
  app = Application()
  app.mainloop()