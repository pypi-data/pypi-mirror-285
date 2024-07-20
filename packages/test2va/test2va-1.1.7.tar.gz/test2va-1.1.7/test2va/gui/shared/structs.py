import sys

import customtkinter as ctk


class HoverScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.bind("<Enter>", self._bind_mouse_wheel)
        self.bind("<Leave>", self._unbind_mouse_wheel)

    def _bind_mouse_wheel(self, _event):
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _unbind_mouse_wheel(self, _event):
        self.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(self, event):
        if sys.platform.startswith("win"):
            if self._orientation == "horizontal":
                if self._parent_canvas.xview() != (0.0, 1.0):
                    self._parent_canvas.xview("scroll", -int(event.delta / 6), "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -int(event.delta / 6), "units")
        elif sys.platform == "darwin":
            if self._orientation == "horizontal":
                if self._parent_canvas.xview() != (0.0, 1.0):
                    self._parent_canvas.xview("scroll", -event.delta, "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -event.delta, "units")
        else:
            if self._orientation == "horizontal":
                if self._parent_canvas.xview() != (0.0, 1.0):
                    self._parent_canvas.xview("scroll", -event.delta, "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -event.delta, "units")
