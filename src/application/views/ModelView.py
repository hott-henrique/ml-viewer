from tkinter import ttk

class ModelView(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)
    ttk.Label(self, text="🧠 Model Configuration", font=("", 16, "bold")).pack(pady=20)
    ttk.Label(self, text="Aqui vai o seu AlgorithmSelector e HyperParamForm...").pack()