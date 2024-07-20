import customtkinter as ctk

from PIL import Image


class TabIconWidget(ctk.CTkImage):

    def __init__(self, path: str, size: tuple):
        super().__init__(Image.open(path).resize(size))
