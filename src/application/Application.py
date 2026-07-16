import tkinter as tk

class Application(tk.Tk):

  def __init__(self):
    super().__init__()

    self.title('App Title')
    self.geometry('300x300')