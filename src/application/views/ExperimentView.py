from tkinter import ttk


class ExperimentView(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)
    ttk.Label(self, text="🧪 Execution & Results", font=("", 16, "bold")).pack(pady=20)
    ttk.Label(self, text="Aqui vai a sua progress bar e os relatórios de métricas...").pack()