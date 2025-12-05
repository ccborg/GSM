import pandas as pd
from tkinter import *
from tkinter.filedialog import askopenfilename

class Settings(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.geometry("600x600")
        self.title("Settings")
        self.resizable(width=False, height=False)
        chooseStudentFile = Frame(self)
